import dataclasses
import logging
from typing import Any, Callable, Tuple
from urllib.parse import urljoin, urlparse

import certbot.display
import dns.exception
import dns.resolver
import requests
import zope.interface
from certbot._internal.account import Account, AccountFileStorage
from certbot.errors import PluginError
from certbot.interfaces import IAuthenticator, IPluginFactory
from certbot.plugins.dns_common import DNSAuthenticator, base_domain_name_guesses
from certbot.plugins.storage import PluginStorage
from certbot.util import is_wildcard_domain

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class AcmeDnsAccount:
    username: str
    password: str
    fulldomain: str
    subdomain: str


@zope.interface.implementer(IAuthenticator)
@zope.interface.provider(IPluginFactory)
class Authenticator(DNSAuthenticator):
    """
    ACME DNS proxy Authenticator

    This Authenticator fulfills dns-01 challenges using an ACME DNS proxy
    server running the acme-dns software [1].

    [1] https://github.com/joohoi/acme-dns
    """

    description = "Obtains certificates using an ACME DNS proxy."

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage = PluginStorage(self.config, self.name)

    def more_info(self) -> str:
        return self.description

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None], **kwargs: Any) -> None:
        super().add_parser_arguments(add, **kwargs)
        add(
            "url",
            type=str,
            default="https://auth.acme-dns.io",
            help="URL of the ACME DNS proxy server.",
        )
        add(
            "is-trusted",
            type=str,
            default="no",
            help="[INSECURE] Ignore that the chosen CA does not support RFC 8657.",
        )

    def _setup_credentials(self) -> None:
        pass

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        account = self._get_account()
        accounturi = account.regr.uri
        ca_server = urlparse(self.config.server).netloc
        ca_id = self._ca_server_to_ca_id(ca_server)
        is_wildcard = is_wildcard_domain(domain)

        if not self._ca_supports_rfc8657(ca_server):
            if self.conf("is-trusted").upper() in ("YES", "TRUE"):
                LOGGER.warning(
                    "Ignoring that the chosen CA does not support RFC 8657"
                    " (INSECURE, unless you self-host the ACME DNS proxy)."
                )
            else:
                raise PluginError(
                    "CA does not support RFC 8657, unable to proceed securely."
                )

        # walk dns records to check whether CAA record is already configured,
        # otherwise prompt the user to do so
        for caa_domain in base_domain_name_guesses(domain):
            if self._has_secure_caa_records(
                domain=caa_domain,
                wildcard=is_wildcard,
                ca_id=ca_id,
                accounturi=accounturi,
            ):
                LOGGER.info("Found securely configured CAA records on %s.", caa_domain)
                break
        else:
            caa_value = f"{ca_id}; accounturi={accounturi}"
            certbot.display.util.notify(
                f"Please create the following CAA records at or above {domain}:\n"
                f"\t0 issue \"{caa_value}\"\n"
                f"\t0 issuewild \"{caa_value if is_wildcard else ';'}\"\n"
            )
            raise PluginError(f"No properly restricted CAA record found for {domain}.")

        acme_dns_account, registered = self._get_acme_dns_account()
        if registered:
            certbot.display.util.input_with_timeout(
                f"Please create a CNAME record at {validation_name} pointing to"
                f" {acme_dns_account.fulldomain}, then press return to continue."
            )

        self._validate_cname_record(acme_dns_account, validation_name)
        self._update_challenge_record(acme_dns_account, validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        pass

    def _get_account(self) -> Account:
        acc_storage = AccountFileStorage(self.config)

        if self.config.account is None:
            raise PluginError(
                "Certbot did not provide us with the ACME CA account to use."
            )

        return acc_storage.load(self.config.account)

    @staticmethod
    def _ca_server_to_ca_id(ca_server: str) -> str:
        try:
            return {
                "acme-v02.api.letsencrypt.org": "letsencrypt.org",
            }[ca_server]
        except KeyError as exc:
            raise PluginError(
                f"Unknown CA server `{ca_server}`, cannot translate to CA ID for CAA records."
            ) from exc

    @staticmethod
    def _ca_supports_rfc8657(ca_server: str) -> bool:
        return ca_server in ()

    @staticmethod
    def _has_secure_caa_records(
        domain: str, wildcard: bool, ca_id: str, accounturi: str
    ) -> bool:
        # request CAA records for domain, verify that an "issue" or "issuewild"
        # CAA record exists for current ACME CA with an account URI set to our CA account;
        # log a warning for every other record
        # must raise PluginError if CAA records are found but disallow issuance,
        # False if no CAA records exist for the domain
        if is_wildcard_domain(domain):
            return False

        try:
            answer = dns.resolver.resolve(domain, "CAA")
        except dns.resolver.NoAnswer:
            return False
        except dns.exception.DNSException as exc:
            raise PluginError(f"Failed to query CAA records for {domain}.") from exc

        found_issue: bool = False
        found_noissue: bool = False
        found_issuewild: bool = False
        found_noissuewild: bool = False
        for caa_record in [x.to_text() for x in answer.rrset]:
            if caa_record == f'0 issue "{ca_id}; accounturi={accounturi}"':
                found_issue = True
            elif caa_record == f'0 issuewild "{ca_id}; accounturi={accounturi}"':
                found_issuewild = True
            elif caa_record == '0 issue ";"':
                found_noissue = True
            elif caa_record == '0 issuewild ";"':
                found_noissuewild = True
            else:
                LOGGER.warning("Found extra CAA record: %s", caa_record)

        if wildcard:
            if found_noissuewild:
                raise PluginError(
                    f"Found CAA issuewild record disallowing any issuance on domain {domain}!"
                )
            if found_issuewild:
                return True
        if found_noissue:
            raise PluginError(
                f"Found CAA issue record disallowing any issuance on domain {domain}!"
            )
        return found_issue

    @staticmethod
    def _validate_cname_record(
        acme_dns_account: AcmeDnsAccount, validation_name: str
    ) -> None:
        try:
            answer = dns.resolver.resolve(validation_name, "CNAME")
        except dns.exception.DNSException as exc:
            raise PluginError(
                f"Failed to query CNAME records for {validation_name}."
            ) from exc

        if len(answer.rrset) > 1:
            raise PluginError(f"Multiple CNAME records found for {validation_name}.")

        # older dnspython versions (eg. v2.0.0 as packaged in Debian 11)
        # do not yet support omit_final_dot kwarg (it is ignored)
        cname = answer.rrset[0].to_text(omit_final_dot=True).rstrip(".")
        expected = acme_dns_account.fulldomain

        if cname != expected:
            raise PluginError(
                f"None or incorrect CNAME record for `{validation_name}`:"
                f" got `{cname}` but expected `{expected}`."
            )

        LOGGER.info(
            "Found valid CNAME record for %s pointing to ACME DNS proxy.",
            validation_name,
        )

    def _update_challenge_record(
        self, acme_dns_account: AcmeDnsAccount, validation: str
    ) -> None:
        update_url = urljoin(self.conf("url"), "update")
        try:
            response = requests.post(
                update_url,
                headers={
                    "X-Api-User": acme_dns_account.username,
                    "X-Api-Key": acme_dns_account.password,
                },
                json={
                    "subdomain": acme_dns_account.subdomain,
                    "txt": validation,
                },
            )
        except requests.exceptions.RequestException as exc:
            raise PluginError(
                f"Network error while trying to update ACME DNS proxy validation record: {exc!s}"
            ) from exc
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise PluginError(
                f"Failed to update ACME DNS proxy validation record: {response.text}"
            ) from exc
        LOGGER.info("Successfully updated ACME DNS proxy validation record.")

    def _get_acme_dns_account(self) -> Tuple[AcmeDnsAccount, bool]:
        try:
            accounts = self.storage.fetch("accounts")
        except KeyError:
            accounts = {}

        try:
            return AcmeDnsAccount(**accounts[self.conf("url")]), False
        except KeyError:
            acc = self._register_acme_dns_account()
            accounts[self.conf("url")] = dataclasses.asdict(acc)
            self.storage.put("accounts", accounts)
            self.storage.save()
            return acc, True

    def _register_acme_dns_account(self) -> AcmeDnsAccount:
        register_url = urljoin(self.conf("url"), "register")
        try:
            response = requests.post(register_url)
        except requests.exceptions.RequestException as exc:
            raise PluginError(
                f"Network error while trying to register new ACME DNS proxy account: {exc!s}"
            ) from exc
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise PluginError(
                f"Failed to register new ACME DNS proxy account: {response.text}"
            ) from exc
        creds = response.json()
        acc = AcmeDnsAccount(
            username=creds.get("username"),
            password=creds.get("password"),
            fulldomain=creds.get("fulldomain"),
            subdomain=creds.get("subdomain"),
        )
        LOGGER.info("Created new ACME DNS proxy account: %s", acc.username)
        return acc

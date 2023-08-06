import dataclasses
import pytest
import requests

from certbot.errors import PluginError


class TestAcmeDnsApi:
    def test_register_success(self, authenticator, acme_dns_account, requests_mock):
        requests_mock.post(
            "https://acme-dns.example.com/register",
            json=dataclasses.asdict(acme_dns_account),
        )
        acc = authenticator._register_acme_dns_account()
        assert acc.username == acme_dns_account.username
        assert acc.password == acme_dns_account.password
        assert acc.fulldomain == acme_dns_account.fulldomain
        assert acc.subdomain == acme_dns_account.subdomain

    def test_register_network_failure(self, authenticator, requests_mock):
        requests_mock.post(
            "https://acme-dns.example.com/register",
            exc=requests.exceptions.RequestException,
        )
        with pytest.raises(PluginError):
            authenticator._register_acme_dns_account()

    def test_register_server_failure(self, authenticator, requests_mock):
        requests_mock.post(
            "https://acme-dns.example.com/register",
            text="something went wrong",
            status_code=500,
        )
        with pytest.raises(PluginError):
            authenticator._register_acme_dns_account()

    def test_update_success(self, authenticator, acme_dns_account, requests_mock):
        requests_mock.post(
            "https://acme-dns.example.com/update",
            request_headers={
                "X-Api-User": acme_dns_account.username,
                "X-Api-Key": acme_dns_account.password,
            },
            additional_matcher=lambda x: x.json() == {
                "subdomain": acme_dns_account.subdomain,
                "txt": "xxx",
            },
        )
        authenticator._update_challenge_record(acme_dns_account, validation="xxx")

    def test_update_network_failure(self, authenticator, acme_dns_account, requests_mock):
        requests_mock.post(
            "https://acme-dns.example.com/update",
            request_headers={
                "X-Api-User": acme_dns_account.username,
                "X-Api-Key": acme_dns_account.password,
            },
            additional_matcher=lambda x: x.json() == {
                "subdomain": acme_dns_account.subdomain,
                "txt": "xxx",
            },
            exc=requests.exceptions.RequestException,
        )
        with pytest.raises(PluginError):
            authenticator._update_challenge_record(acme_dns_account, validation="xxx")

    def test_update_server_failure(self, authenticator, acme_dns_account, requests_mock):
        requests_mock.post(
            "https://acme-dns.example.com/update",
            request_headers={
                "X-Api-User": acme_dns_account.username,
                "X-Api-Key": acme_dns_account.password,
            },
            additional_matcher=lambda x: x.json() == {
                "subdomain": acme_dns_account.subdomain,
                "txt": "xxx",
            },
            text="something went wrong",
            status_code=500,
        )
        with pytest.raises(PluginError):
            authenticator._update_challenge_record(acme_dns_account, validation="xxx")



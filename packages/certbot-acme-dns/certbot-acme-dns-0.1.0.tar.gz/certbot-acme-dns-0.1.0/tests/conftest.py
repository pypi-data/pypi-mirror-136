import pytest

from argparse import Namespace
try:
    from certbot.configuration import NamespaceConfig
except ImportError:
    from certbot._internal.configuration import NamespaceConfig
from certbot_acme_dns.acme_dns import AcmeDnsAccount, Authenticator


@pytest.fixture
def authenticator(tmpdir):
    namespace = Namespace(
        config_dir=tmpdir / "config",
        logs_dir=tmpdir / "logs",
        work_dir=tmpdir / "work",
        http01_port=12345,
        https_port=443,
        domains=["my.domain.example.com"],
        acme_dns_url="https://acme-dns.example.com",
    )
    return Authenticator(config=NamespaceConfig(namespace), name="acme-dns")


@pytest.fixture
def acme_dns_account():
    return AcmeDnsAccount(
        username="foo",
        password="bar",
        fulldomain="moo.acme-dns.example.com",
        subdomain="moo",
    )

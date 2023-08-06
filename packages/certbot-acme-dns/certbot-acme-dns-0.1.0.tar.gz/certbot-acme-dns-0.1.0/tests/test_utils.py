import pytest

from certbot.errors import PluginError


class TestCaServerToCaId:
    def test_notfound(self, authenticator):
        with pytest.raises(PluginError):
            authenticator._ca_server_to_ca_id("example.com")

    def test_found(self, authenticator):
        assert authenticator._ca_server_to_ca_id("acme-v02.api.letsencrypt.org") == "letsencrypt.org"


class TestCaSupportsRfc8657:
    def test_false(self, authenticator):
        assert authenticator._ca_supports_rfc8657("example.com") is False


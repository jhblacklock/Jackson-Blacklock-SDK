import responses as resp_lib
import pytest

from lotr_sdk import LotrClient, LotrAuthError, LotrRateLimitError
from tests.conftest import BASE_URL, paginated, SAMPLE_MOVIE


@resp_lib.activate
def test_auth_header_set(client):
    """Authorization header is sent with every request."""
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json=paginated([SAMPLE_MOVIE]),
        status=200,
    )
    client.movies.list()
    assert len(resp_lib.calls) == 1
    assert resp_lib.calls[0].request.headers["Authorization"] == "Bearer test-token"


@resp_lib.activate
def test_accept_header_set(client):
    """Accept: application/json header is sent."""
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json=paginated([SAMPLE_MOVIE]),
        status=200,
    )
    client.movies.list()
    assert resp_lib.calls[0].request.headers["Accept"] == "application/json"


@resp_lib.activate
def test_401_raises_auth_error(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json={"message": "Unauthorized"},
        status=401,
    )
    with pytest.raises(LotrAuthError) as exc_info:
        client.movies.list()
    assert exc_info.value.status_code == 401


@resp_lib.activate
def test_429_raises_rate_limit_error(client):
    resp_lib.add(
        resp_lib.GET,
        f"{BASE_URL}/movie",
        json={"message": "Rate limit exceeded"},
        status=429,
    )
    with pytest.raises(LotrRateLimitError) as exc_info:
        client.movies.list()
    assert exc_info.value.status_code == 429


def test_custom_base_url():
    """Client uses the provided base_url."""
    custom = "https://custom.example.com/v2"
    c = LotrClient(api_key="key", base_url=custom)
    assert c.movies._base_url == custom
    assert c.quotes._base_url == custom


def test_custom_timeout(monkeypatch):
    """Timeout is forwarded to session.get via BaseResource._timeout."""
    import requests

    captured = {}
    original_send = requests.Session.send

    def mock_send(self, request, **kwargs):
        captured["timeout"] = kwargs.get("timeout")
        r = requests.Response()
        r.status_code = 200
        r._content = b'{"docs":[],"total":0,"limit":1000,"offset":0,"page":1,"pages":1}'
        return r

    monkeypatch.setattr(requests.Session, "send", mock_send)

    c = LotrClient(api_key="key", timeout=42)
    c.movies.list()
    assert captured["timeout"] == 42

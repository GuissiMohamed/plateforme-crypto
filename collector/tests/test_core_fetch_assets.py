import requests
import pytest
from collector import core


class DummyResp:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_fetch_assets_ok(monkeypatch):
    payload = [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]

    def fake_get(url, timeout):
        assert "coingecko" in url
        assert timeout == 10
        return DummyResp(payload, 200)

    monkeypatch.setattr(core.requests, "get", fake_get)

    data = core.fetch_assets()
    assert data == payload


def test_fetch_assets_http_error(monkeypatch):
    def fake_get(url, timeout):
        return DummyResp({"error": "nope"}, 500)

    monkeypatch.setattr(core.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        core.fetch_assets()


def test_fetch_assets_timeout(monkeypatch):
    def fake_get(url, timeout):
        raise requests.Timeout("timeout")

    monkeypatch.setattr(core.requests, "get", fake_get)

    with pytest.raises(requests.Timeout):
        core.fetch_assets()


def test_fetch_assets_request_exception(monkeypatch):
    def fake_get(url, timeout):
        raise requests.RequestException("network down")

    monkeypatch.setattr(core.requests, "get", fake_get)

    with pytest.raises(requests.RequestException):
        core.fetch_assets()

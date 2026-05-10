import pytest
from src.routing import Router


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text


    def json(self):
        return self._payload


    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"HTTP {self.status_code}")


def test_init_sets_base_url():
    router = Router()
    assert router.base_url == "http://localhost:8080/ors/v2/isochrones/driving-car"


def test_get_isochrone_posts_with_correct_payload(monkeypatch):
    captured = {}

    def fake_post(url, json, headers):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return FakeResponse(status_code=200, payload={"type": "FeatureCollection"})

    monkeypatch.setattr("src.routing.requests.post", fake_post)

    router = Router()
    iso = router.get_isochrone(49.4, 8.7, time_limit=10)

    assert iso == {"type": "FeatureCollection"}
    assert captured["url"] == router.base_url
    assert captured["json"]["locations"] == [[8.7, 49.4]]
    assert captured["json"]["range"] == [600]
    assert captured["json"]["range_type"] == "time"
    assert captured["headers"]["Accept"].startswith("application/geo+json")


def test_get_isochrone_raises_when_request_fails(monkeypatch):
    def fake_post(url, json, headers):
        return FakeResponse(status_code=500, text="Server error")

    monkeypatch.setattr("src.routing.requests.post", fake_post)

    router = Router()
    with pytest.raises(Exception, match="Local ORS request failed"):
        router.get_isochrone(49.4, 8.7, time_limit=10)

from collector import core


def test_collect_once_calls_fetch_and_save(monkeypatch):
    called = {"fetch": 0, "save": 0}

    def fake_fetch():
        called["fetch"] += 1
        return [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]

    def fake_save(data):
        called["save"] += 1
        assert isinstance(data, list)

    monkeypatch.setattr(core, "fetch_assets", fake_fetch)
    monkeypatch.setattr(core, "save_assets_to_db", fake_save)

    core.collect_once()

    assert called["fetch"] == 1
    assert called["save"] == 1

def test_indicators_ok(client, seed_asset_prices):
    asset_id = seed_asset_prices["asset_id"]
    r = client.get(f"/assets/{asset_id}/indicators")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["asset_id"] == asset_id
    assert data["signal"] in ["bullish", "bearish", "neutral"]

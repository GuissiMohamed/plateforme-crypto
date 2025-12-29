def test_list_assets_empty(client):
    r = client.get("/assets")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_prices_404_when_asset_missing(client):
    r = client.get("/assets/unknown/prices")
    assert r.status_code == 404


def test_prices_ok(client, seed_asset_prices):
    asset_id = seed_asset_prices["asset_id"]
    r = client.get(f"/assets/{asset_id}/prices?limit=10")
    assert r.status_code == 200, r.text
    data = r.json()
    assert len(data) == 10
    assert data[0]["asset_id"] == asset_id

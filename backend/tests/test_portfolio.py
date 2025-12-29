def test_buy_requires_auth(client, seed_asset_prices):
    r = client.post("/portfolio/buy", json={"asset_id": seed_asset_prices["asset_id"], "quantity": 1.0})
    assert r.status_code in (401, 403)


def test_buy_sell_and_value(client, auth_headers, seed_asset_prices):
    asset_id = seed_asset_prices["asset_id"]

    # buy
    r1 = client.post("/portfolio/buy", json={"asset_id": asset_id, "quantity": 2.0}, headers=auth_headers)
    assert r1.status_code == 200, r1.text
    assert r1.json()["is_buy"] is True

    # value > 0
    r2 = client.get("/portfolio/value", headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["value_usd"] > 0

    # sell too much => 400
    r3 = client.post("/portfolio/sell", json={"asset_id": asset_id, "quantity": 999}, headers=auth_headers)
    assert r3.status_code == 400

    # sell ok
    r4 = client.post("/portfolio/sell", json={"asset_id": asset_id, "quantity": 1.0}, headers=auth_headers)
    assert r4.status_code == 200
    assert r4.json()["is_buy"] is False

    # list txs
    r5 = client.get("/portfolio/transactions", headers=auth_headers)
    assert r5.status_code == 200
    assert isinstance(r5.json(), list)
    assert len(r5.json()) >= 2

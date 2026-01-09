def test_alerts_crud(client, auth_headers, seed_asset_prices):
    asset_id = seed_asset_prices["asset_id"]

    # create
    r1 = client.post("/alerts", json={"asset_id": asset_id, "alert_type": "above", "target_value": 1.0}, headers=auth_headers)
    assert r1.status_code == 200, r1.text
    alert_id = r1.json()["id"]

    # list
    r2 = client.get("/alerts", headers=auth_headers)
    assert r2.status_code == 200
    assert any(a["id"] == alert_id for a in r2.json())

    # delete
    r3 = client.delete(f"/alerts/{alert_id}", headers=auth_headers)
    assert r3.status_code == 200
    assert r3.json()["status"] == "deleted"


def test_notifications_list_empty_or_ok(client, auth_headers):
    r = client.get("/notifications", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

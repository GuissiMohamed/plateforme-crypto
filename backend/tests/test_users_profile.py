def test_get_me(client, auth_headers):
    r = client.get("/users/me", headers=auth_headers)
    assert r.status_code == 200
    assert "email" in r.json()


def test_update_profile(client, auth_headers):
    r = client.put("/users/me/profile", json={"display_name": "  Alice  "}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["display_name"] == "Alice"


def test_update_password_wrong_old(client, auth_headers):
    r = client.put("/users/me/password", json={"old_password": "bad", "new_password": "NewPass123!"}, headers=auth_headers)
    assert r.status_code == 400


def test_update_discord_webhook_set_and_clear(client, auth_headers):
    r1 = client.put("/users/me/discord-webhook", json={"discord_webhook_url": "https://example.com/x"}, headers=auth_headers)
    assert r1.status_code == 200
    assert r1.json()["discord_webhook_url"] == "https://example.com/x"

    r2 = client.put("/users/me/discord-webhook", json={"discord_webhook_url": ""}, headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["discord_webhook_url"] is None

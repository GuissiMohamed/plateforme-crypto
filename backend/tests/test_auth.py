def test_register_then_login(client):
    # register
    r = client.post("/auth/register", json={"email": "new@ex.com", "password": "StrongPass123!"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["email"] == "new@ex.com"
    assert "id" in data

    # login
    r2 = client.post(
        "/auth/login",
        data={"username": "new@ex.com", "password": "StrongPass123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r2.status_code == 200, r2.text
    tok = r2.json()
    assert "access_token" in tok
    assert tok["token_type"] == "bearer"


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@ex.com", "password": "x"})
    r = client.post("/auth/register", json={"email": "dup@ex.com", "password": "y"})
    assert r.status_code == 400

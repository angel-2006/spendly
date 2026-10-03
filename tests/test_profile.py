import pytest

import database.db as db
from app import app

EMAIL = "asha@example.com"
PASSWORD = "secret123"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    app.config["TESTING"] = True
    client = app.test_client()
    client.post(
        "/register", data={"name": "Asha Rao", "email": EMAIL, "password": PASSWORD}
    )
    return client


def login(client):
    return client.post("/login", data={"email": EMAIL, "password": PASSWORD})


def test_profile_requires_login(client):
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_profile_renders_when_logged_in(client):
    login(client)
    resp = client.get("/profile")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "demo@spendly.com" in body
    assert "Total spent" in body and "Transactions" in body and "Top category" in body
    assert body.count('class="badge') >= 3
    assert body.count('class="cat-row"') >= 3
    assert "₹" in body
    assert "style=" not in body
    assert "Sign out" in body

import pytest
from werkzeug.security import check_password_hash

import database.db as db
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    app.config["TESTING"] = True
    return app.test_client()


def all_users():
    conn = db.get_db()
    try:
        return conn.execute("SELECT * FROM users").fetchall()
    finally:
        conn.close()


def post(client, name="Asha Rao", email="asha@example.com", password="secret123"):
    return client.post(
        "/register", data={"name": name, "email": email, "password": password}
    )


def test_get_renders_form(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"<form" in resp.data


def test_valid_registration_redirects_and_stores_hash(client):
    resp = post(client, name="  Asha Rao ", email="  Asha@Example.COM ")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    users = all_users()
    assert len(users) == 1
    assert users[0]["name"] == "Asha Rao"
    assert users[0]["email"] == "asha@example.com"
    assert users[0]["password_hash"] != "secret123"
    assert check_password_hash(users[0]["password_hash"], "secret123")


def test_duplicate_email_rejected_case_insensitive(client):
    post(client)
    resp = post(client, email="ASHA@example.com")
    assert resp.status_code == 200
    assert b"already exists" in resp.data
    assert len(all_users()) == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": ""},
        {"email": ""},
        {"email": "no-at-sign"},
        {"email": "@example.com"},
        {"email": "asha@"},
        {"password": "1234567"},
    ],
)
def test_invalid_input_rejected(client, kwargs):
    resp = post(client, **kwargs)
    assert resp.status_code == 200
    assert b"auth-error" in resp.data
    assert all_users() == []


def test_error_keeps_name_and_email_but_not_password(client):
    resp = post(client, name="Asha Rao", email="asha@example.com", password="short")
    body = resp.data.decode()
    assert 'value="Asha Rao"' in body
    assert 'value="asha@example.com"' in body
    assert "short" not in body.replace("Password must be at least 8 characters.", "")

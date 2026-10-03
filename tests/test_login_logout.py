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


def login(client, email=EMAIL, password=PASSWORD):
    return client.post("/login", data={"email": email, "password": password})


def session_user(client):
    with client.session_transaction() as sess:
        return sess.get("user_id")


def test_get_renders_form_posting_to_login(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b'action="/login"' in resp.data


def test_valid_login_redirects_and_sets_session(client):
    resp = login(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")
    assert session_user(client) is not None


def test_login_email_case_and_whitespace_insensitive(client):
    resp = login(client, email="  ASHA@Example.COM ")
    assert resp.status_code == 302
    assert session_user(client) is not None


@pytest.mark.parametrize(
    "kwargs", [{"password": "wrongpass1"}, {"email": "nobody@example.com"}]
)
def test_bad_credentials_generic_error(client, kwargs):
    resp = login(client, **kwargs)
    assert resp.status_code == 200
    assert b"Invalid email or password." in resp.data
    assert session_user(client) is None


@pytest.mark.parametrize("kwargs", [{"email": ""}, {"password": ""}])
def test_empty_fields_rejected(client, kwargs):
    resp = login(client, **kwargs)
    assert resp.status_code == 200
    assert b"auth-error" in resp.data
    assert session_user(client) is None


def test_error_keeps_email_but_not_password(client):
    resp = login(client, password="wrongpass1")
    body = resp.data.decode()
    assert f'value="{EMAIL}"' in body
    assert "wrongpass1" not in body


def test_login_page_redirects_when_logged_in(client):
    login(client)
    resp = client.get("/login")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")


def test_logout_clears_session_and_redirects(client):
    login(client)
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")
    assert session_user(client) is None
    assert b"Sign in" in client.get("/").data


def test_navbar_reflects_login_state(client):
    assert b"Sign out" not in client.get("/").data
    login(client)
    body = client.get("/").data
    assert b"Sign out" in body
    assert b"Sign in" not in body

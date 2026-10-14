"""Password login, refresh sessions, lockout, forced change and admin gating."""
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.main import app
from app.models.audit_log import AuditLog
from app.models.user import RefreshToken, User

ADMIN = ("admin@hospital.test", "Correct-Horse-42")
API = settings.API_V1_PREFIX


@pytest.fixture()
def client():
    init_db()
    db = SessionLocal()
    db.query(AuditLog).delete()
    db.query(RefreshToken).delete()
    db.query(User).delete()
    db.add(
        User(
            email=ADMIN[0],
            name="Admin",
            role="admin",
            password_hash=hash_password(ADMIN[1]),
        )
    )
    db.commit()
    db.close()
    # https base URL is irrelevant here: the cookie is not Secure outside production.
    return TestClient(app)


def _login(client, email=ADMIN[0], password=ADMIN[1]):
    return client.post(f"{API}/auth/login", json={"email": email, "password": password})


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_sets_httponly_cookie_and_returns_access_token(client):
    res = _login(client, email="ADMIN@Hospital.Test")  # case-insensitive
    assert res.status_code == 200
    body = res.json()
    assert body["user"]["role"] == "admin" and body["expires_in"] == 900
    cookie = res.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie
    assert f"Path={API}/auth" in cookie
    assert client.get(f"{API}/cases", headers=_bearer(body["access_token"])).status_code == 200


def test_wrong_password_and_unknown_email_look_identical(client):
    wrong = _login(client, password="nope-nope-nope-1")
    unknown = _login(client, email="ghost@hospital.test")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_account_locks_after_repeated_failures(client):
    for _ in range(settings.MAX_FAILED_LOGINS):
        assert _login(client, password="bad-password-000").status_code == 401
    # Even the right password is refused while locked.
    assert _login(client).status_code == 429


def test_refresh_and_logout(client):
    _login(client)
    refreshed = client.post(f"{API}/auth/refresh")
    assert refreshed.status_code == 200 and refreshed.json()["access_token"]

    assert client.post(f"{API}/auth/logout").status_code == 204
    assert client.post(f"{API}/auth/refresh").status_code == 401


def test_revoked_session_cannot_be_replayed(client):
    _login(client)
    stolen = client.cookies.get(settings.REFRESH_COOKIE_NAME)
    client.post(f"{API}/auth/logout")
    client.cookies.set(settings.REFRESH_COOKIE_NAME, stolen, path=f"{API}/auth")
    assert client.post(f"{API}/auth/refresh").status_code == 401


def test_requests_without_or_with_forged_token_are_rejected(client):
    assert client.get(f"{API}/cases").status_code in (401, 403)
    import jwt

    forged = jwt.encode({"sub": "1", "type": "access"}, "change-me-in-production", "HS256")
    assert client.get(f"{API}/cases", headers=_bearer(forged)).status_code == 401


def test_admin_provisions_user_who_must_change_password(client):
    admin_token = _login(client).json()["access_token"]
    new_user = {
        "email": "dr.silva@hospital.test",
        "name": "Dr Silva",
        "role": "radiologist",
        "password": "Temporary-Pass-77",
    }
    weak = client.post(
        f"{API}/admin/users", json={**new_user, "password": "short1"}, headers=_bearer(admin_token)
    )
    assert weak.status_code == 400
    created = client.post(f"{API}/admin/users", json=new_user, headers=_bearer(admin_token))
    assert created.status_code == 201 and created.json()["must_change_password"] is True
    dup = client.post(f"{API}/admin/users", json=new_user, headers=_bearer(admin_token))
    assert dup.status_code == 409

    user_client = TestClient(app)
    login = _login(user_client, new_user["email"], new_user["password"])
    temp_token = login.json()["access_token"]
    assert login.json()["user"]["must_change_password"] is True

    # Locked out of clinical data until the temporary password is replaced…
    blocked = user_client.get(f"{API}/cases", headers=_bearer(temp_token))
    assert blocked.status_code == 403 and blocked.json()["detail"] == "password_change_required"
    # …and never allowed into admin endpoints.
    changed = user_client.post(
        f"{API}/auth/change-password",
        json={"current_password": new_user["password"], "new_password": "Brand-New-Pass-88"},
        headers=_bearer(temp_token),
    )
    assert changed.status_code == 200
    new_token = changed.json()["access_token"]
    assert user_client.get(f"{API}/cases", headers=_bearer(new_token)).status_code == 200
    assert user_client.get(f"{API}/admin/users", headers=_bearer(new_token)).status_code == 403
    # The pre-change access token died with the password.
    assert user_client.get(f"{API}/auth/me", headers=_bearer(temp_token)).status_code == 401
    # The session that changed the password survives.
    assert user_client.post(f"{API}/auth/refresh").status_code == 200


def test_deactivating_a_user_ends_their_session(client):
    admin_token = _login(client).json()["access_token"]
    created = client.post(
        f"{API}/admin/users",
        json={"email": "locum@hospital.test", "name": "Locum", "password": "Temporary-Pass-77"},
        headers=_bearer(admin_token),
    ).json()

    user_client = TestClient(app)
    token = _login(user_client, "locum@hospital.test", "Temporary-Pass-77").json()["access_token"]

    res = client.patch(
        f"{API}/admin/users/{created['id']}", json={"is_active": False}, headers=_bearer(admin_token)
    )
    assert res.status_code == 200 and res.json()["is_active"] is False
    assert user_client.get(f"{API}/auth/me", headers=_bearer(token)).status_code == 401
    assert user_client.post(f"{API}/auth/refresh").status_code == 401
    assert _login(user_client, "locum@hospital.test", "Temporary-Pass-77").status_code == 401


def test_admin_cannot_deactivate_or_demote_self(client):
    login = _login(client).json()
    me = login["user"]["id"]
    for change in ({"is_active": False}, {"role": "radiologist"}):
        res = client.patch(
            f"{API}/admin/users/{me}", json=change, headers=_bearer(login["access_token"])
        )
        assert res.status_code == 400


def test_production_refuses_default_secret():
    from app.core.config import Settings

    with pytest.raises(ValueError):
        Settings(ENVIRONMENT="production", JWT_SECRET="change-me-in-production")


def test_admin_overview_and_audit_trail(client):
    _login(client, password="bad-password-000")
    token = _login(client).json()["access_token"]
    client.post(
        f"{API}/admin/users",
        json={"email": "locum@hospital.test", "name": "Locum", "password": "Temporary-Pass-77"},
        headers=_bearer(token),
    )

    overview = client.get(f"{API}/admin/overview", headers=_bearer(token)).json()
    assert overview["users_total"] == 2 and overview["users_admin"] == 1
    assert overview["users_pending_password"] == 1
    assert overview["sessions_active"] == 1
    assert overview["failed_logins_24h"] >= 1

    trail = client.get(f"{API}/admin/audit", headers=_bearer(token)).json()
    actions = [e["action"] for e in trail]
    assert actions[0] == "user_created" and trail[0]["target"] == "locum@hospital.test"
    assert "login_success" in actions and "login_failed" in actions

    users = client.get(f"{API}/admin/users", headers=_bearer(token)).json()
    assert next(u for u in users if u["role"] == "admin")["last_login_at"]


def test_audit_and_overview_are_admin_only(client):
    admin_token = _login(client).json()["access_token"]
    client.post(
        f"{API}/admin/users",
        json={"email": "locum@hospital.test", "name": "Locum", "password": "Temporary-Pass-77"},
        headers=_bearer(admin_token),
    )
    user_client = TestClient(app)
    temp = _login(user_client, "locum@hospital.test", "Temporary-Pass-77").json()["access_token"]
    token = user_client.post(
        f"{API}/auth/change-password",
        json={"current_password": "Temporary-Pass-77", "new_password": "Brand-New-Pass-88"},
        headers=_bearer(temp),
    ).json()["access_token"]
    for path in ("overview", "audit", "users"):
        assert user_client.get(f"{API}/admin/{path}", headers=_bearer(token)).status_code == 403

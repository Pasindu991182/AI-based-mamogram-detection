"""Patient images: encrypted at rest, served only via signed links, removed with the case."""
import pytest
from fastapi.testclient import TestClient

from app.core import crypto
from app.core.config import settings
from app.core.media_token import sign_media_path
from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.main import app
from app.models.stored_file import StoredFile
from app.models.user import User
from app.storage import get_storage

API = settings.API_V1_PREFIX
PNG = b"\x89PNG\r\n\x1a\n" + b"pretend-mammogram-pixels" * 50


@pytest.fixture()
def client():
    init_db()
    with SessionLocal() as db:
        db.query(StoredFile).delete()
        db.commit()
    return TestClient(app)


def _raw(path):
    with SessionLocal() as db:
        row = db.query(StoredFile).filter(StoredFile.path == path).first()
        return row.data if row else None


def test_image_is_encrypted_in_the_database(client):
    url = get_storage().save_bytes(PNG, "cases/900/cc.png")
    assert url == "/uploads/cases/900/cc.png"
    stored = _raw("cases/900/cc.png")
    assert stored and PNG not in stored and b"PNG" not in stored
    assert get_storage().read_bytes("cases/900/cc.png") == (PNG, "image/png")


def test_ciphertext_is_bound_to_its_path(client):
    get_storage().save_bytes(PNG, "cases/900/cc.png")
    from cryptography.exceptions import InvalidTag

    with pytest.raises(InvalidTag):
        crypto.decrypt(_raw("cases/900/cc.png"), "cases/901/cc.png")


def test_image_served_only_with_valid_signature(client):
    get_storage().save_bytes(PNG, "cases/900/cc.png")
    assert client.get("/uploads/cases/900/cc.png").status_code == 403
    assert client.get("/uploads/cases/900/cc.png?exp=9999999999&sig=forged").status_code == 403

    ok = client.get(sign_media_path("cases/900/cc.png"))
    assert ok.status_code == 200 and ok.content == PNG
    assert ok.headers["cache-control"] == "private, no-store"
    # A valid signature for one image does not open another.
    assert client.get(sign_media_path("cases/900/missing.png")).status_code == 404


def test_deleting_a_case_removes_its_images(client):
    with SessionLocal() as db:
        db.query(User).filter(User.email == "owner@hospital.test").delete()
        db.add(User(email="owner@hospital.test", name="Owner", password_hash=hash_password("Correct-Horse-42")))
        db.commit()
    token = client.post(
        f"{API}/auth/login", json={"email": "owner@hospital.test", "password": "Correct-Horse-42"}
    ).json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}
    case_id = client.post(f"{API}/cases", json={"patient_ref": "T-1"}, headers=auth).json()["id"]

    get_storage().save_bytes(PNG, f"cases/{case_id}/cc.png")
    get_storage().save_bytes(PNG, f"cases/{case_id}0/cc.png")  # a different case
    assert client.delete(f"{API}/cases/{case_id}", headers=auth).status_code == 204
    assert _raw(f"cases/{case_id}/cc.png") is None
    assert _raw(f"cases/{case_id}0/cc.png") is not None

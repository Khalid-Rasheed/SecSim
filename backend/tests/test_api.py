"""Core API tests — اختبارات الواجهات الأساسية.

Covers health, the Caesar/HASH happy paths, and the auth → simulate →
history chain (including that history requires a JWT). Uses an isolated
in-memory SQLite DB per test via TestConfig.
"""
import pytest
from app import create_app, db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key-32-chars-minimum!!"
    SECRET_KEY = "test-secret-key-32-chars-minimum!!"


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client


def test_health(client):
    assert client.get("/api/health").json["status"] == "ok"


def test_caesar_encrypt(client):
    r = client.post("/api/simulate", json={"algorithm": "caesar", "input": "Hello", "key": 3})
    assert r.status_code == 200
    assert r.json["result"] == "Khoor"
    assert len(r.json["steps"]) == 7  # setup + 5 chars + final


def test_sha256(client):
    r = client.post("/api/simulate", json={"algorithm": "sha256", "input": "Hello"})
    assert r.status_code == 200
    assert len(r.json["result"]) == 64


def test_brute_force_english(client):
    r = client.post("/api/simulate", json={"algorithm": "brute_force", "input": "Khoor Zruog"})
    assert r.status_code == 200
    assert r.json["result"] == "Hello World"
    assert len(r.json["steps"]) == 27  # setup + 25 attempts + final


def test_brute_force_non_english_no_crash(client):
    # Arabic (or any non-English) input must not raise IndexError (500);
    # Caesar leaves non-Latin chars untouched and ranking degrades gracefully.
    r = client.post("/api/simulate", json={"algorithm": "brute_force", "input": "مرحبا بالعالم"})
    assert r.status_code == 200
    assert len(r.json["steps"]) == 27


def test_brute_force_input_warnings(client):
    """Verdict step carries a bilingual warning for dubious input, else none."""
    def warning_for(text):
        r = client.post("/api/simulate", json={"algorithm": "brute_force", "input": text})
        assert r.status_code == 200
        return r.json["steps"][-1]["snapshot"].get("warning")

    # Real ciphertext → no warning.
    assert warning_for("Khoor Zruog") is None
    # Plain English, too-short, non-English, empty → each warns (ar+en).
    for text in ("Hello World", "Hi", "مرحبا بالعالم", ""):
        w = warning_for(text)
        assert w is not None, text
        assert "ar" in w and "en" in w


def test_error_responses_are_json_with_cors(client):
    r = client.get("/api/no-such-route", headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 404
    assert r.json == {"error": "not found"}
    assert r.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"


def test_auth_and_history(client):
    reg = client.post("/api/auth/register", json={"email": "a@a.com", "password": "secret123"})
    assert reg.status_code == 201
    token = reg.json["token"]
    # simulate WITH token → saved to this user
    client.post(
        "/api/simulate",
        json={"algorithm": "caesar", "input": "Hi", "key": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    h = client.get("/api/history", headers={"Authorization": f"Bearer {token}"})
    assert h.status_code == 200
    assert len(h.json) == 1
    # history without token → 401
    assert client.get("/api/history").status_code == 401


def test_register_rejects_bad_email(client):
    """Malformed emails never reach the database (400, no user created)."""
    for bad in ("not-an-email", "a@b", "a b@c.com", "@c.com", "a@.com"):
        r = client.post(
            "/api/auth/register", json={"email": bad, "password": "secret123"}
        )
        assert r.status_code == 400, bad
        assert r.json["error"] == "invalid email address"


def test_register_rejects_weak_password(client):
    """Policy: ≥8 chars with at least one letter and one digit."""
    cases = {
        "short1": "at least 8",  # too short
        "longpassword": "one letter and one digit",  # no digit
        "12345678": "one letter and one digit",  # no letter
    }
    for pw, hint in cases.items():
        r = client.post("/api/auth/register", json={"email": "u@u.com", "password": pw})
        assert r.status_code == 400, pw
        assert hint in r.json["error"]
    ok = client.post("/api/auth/register", json={"email": "u@u.com", "password": "secret123"})
    assert ok.status_code == 201


def test_login_rate_limited(client):
    """11 rapid logins in a minute → the 11th is rejected with 429 JSON."""
    client.post("/api/auth/register", json={"email": "r@r.com", "password": "secret123"})
    last = None
    for _ in range(11):
        last = client.post(
            "/api/auth/login", json={"email": "r@r.com", "password": "secret123"}
        )
    assert last.status_code == 429
    assert last.json == {"error": "rate limit exceeded, try again later"}

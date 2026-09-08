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


def test_aes_roundtrip(client):
    enc = client.post(
        "/api/simulate",
        json={"algorithm": "aes", "input": "Hello World", "key_text": "secret", "key_size": 128},
    )
    assert enc.status_code == 200
    assert ":" in enc.json["result"]
    dec = client.post(
        "/api/simulate",
        json={
            "algorithm": "aes",
            "input": enc.json["result"],
            "key_text": "secret",
            "key_size": 128,
            "mode": "decrypt",
        },
    )
    assert dec.status_code == 200
    assert dec.json["result"] == "Hello World"


def test_aes_rejects_bad_key_size(client):
    r = client.post("/api/simulate", json={"algorithm": "aes", "input": "x", "key_size": 100})
    assert r.status_code == 400


def test_rsa_roundtrip(client):
    enc = client.post("/api/simulate", json={"algorithm": "rsa", "input": "Hi"})
    assert enc.status_code == 200
    assert enc.json["result"] == "3000 3179"
    dec = client.post(
        "/api/simulate", json={"algorithm": "rsa", "input": enc.json["result"], "mode": "decrypt"}
    )
    assert dec.status_code == 200
    assert dec.json["result"] == "Hi"


def test_md5(client):
    r = client.post("/api/simulate", json={"algorithm": "md5", "input": "Hello"})
    assert r.status_code == 200
    assert r.json["result"] == "8b1a9953c4611296a827abf8c47804d7"
    assert r.json["analysis"]["metrics"]["status"] == "broken"


def test_brute_force_recovers_key(client):
    r = client.post("/api/simulate", json={"algorithm": "brute_force", "input": "Khoor Zruog"})
    assert r.status_code == 200
    assert r.json["result"] == "Hello World"
    assert len(r.json["steps"]) == 27  # setup + 25 attempts + verdict
    assert r.json["steps"][-1]["snapshot"]["best_key"] == 3


def test_analyze_endpoint(client):
    r = client.post("/api/analyze", json={"algorithm": "aes", "parameters": {"key_size": 256}})
    assert r.status_code == 200
    assert r.json["analysis"]["metrics"]["key_bits"] == 256
    bad = client.post("/api/analyze", json={"algorithm": "des"})
    assert bad.status_code == 400


def test_algorithm_details_reference(client):
    for algo_id in ("caesar", "aes", "rsa", "sha256", "md5", "brute_force"):
        r = client.get(f"/api/algorithms/{algo_id}")
        assert r.status_code == 200, algo_id
        d = r.json["details"]
        assert {"overview", "history", "how_it_works", "parameters", "security", "uses"} <= set(d)
        for section in ("overview", "history", "security"):
            assert "ar" in d[section] and "en" in d[section], (algo_id, section)
        assert len(d["how_it_works"]["ar"]) >= 3
        assert len(d["uses"]["en"]) >= 2
    assert client.get("/api/algorithms/rot13").status_code == 404


def test_complexity_present_everywhere(client):
    algos = client.get("/api/algorithms").json
    assert len(algos) == 6
    for a in algos:
        cx = a["complexity"]
        assert cx["time"].startswith("O(")
        assert cx["space"].startswith("O(")
        assert "ar" in cx["n"] and "en" in cx["note"]
    expected = {
        "caesar": ("O(n)", "O(n)"),
        "aes": ("O(n)", "O(n)"),
        "sha256": ("O(n)", "O(1)"),
        "md5": ("O(n)", "O(1)"),
    }
    for algo, (t, s) in expected.items():
        r = client.post("/api/simulate", json={"algorithm": algo, "input": "Hello"})
        assert r.status_code == 200
        assert r.json["analysis"]["complexity"]["time"] == t
        assert r.json["analysis"]["complexity"]["space"] == s

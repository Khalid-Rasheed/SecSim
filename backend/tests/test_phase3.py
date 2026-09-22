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


def test_playfair_roundtrip(client):
    enc = client.post("/api/simulate",
                      json={"algorithm": "playfair", "input": "HELLO", "playfair_key": "MONARCHY"})
    assert enc.status_code == 200
    assert enc.json["result"] == "CFSUPM"
    dec = client.post("/api/simulate",
                      json={"algorithm": "playfair", "input": enc.json["result"],
                            "playfair_key": "MONARCHY", "mode": "decrypt"})
    assert dec.status_code == 200
    assert dec.json["result"] == "HELXLO"  # X splitting/padding is visible by design


def test_elgamal_roundtrip(client):
    enc = client.post("/api/simulate", json={"algorithm": "elgamal", "input": "Hi"})
    assert enc.status_code == 200
    assert enc.json["result"].count(" ") == 1  # one c1,c2 pair per char
    dec = client.post("/api/simulate",
                      json={"algorithm": "elgamal", "input": enc.json["result"],
                            "mode": "decrypt"})
    assert dec.status_code == 200
    assert dec.json["result"] == "Hi"


def test_sha512(client):
    r = client.post("/api/simulate", json={"algorithm": "sha512", "input": "Hello"})
    assert r.status_code == 200
    assert len(r.json["result"]) == 128
    assert r.json["analysis"]["metrics"]["digest_bits"] == 512


def test_vigenere_breaker_recovers_key(client):
    plain = ("CRYPTOGRAPHY IS THE PRACTICE OF SECURE COMMUNICATION IN THE PRESENCE "
             "OF ADVERSARIES AND IT RELIES ON MATHEMATICS NOT SECRECY FOR ITS STRENGTH")
    enc = client.post("/api/simulate",
                      json={"algorithm": "vigenere", "input": plain, "vigenere_key": "LEMON"})
    assert enc.status_code == 200
    r = client.post("/api/simulate",
                    json={"algorithm": "vigenere_breaker", "input": enc.json["result"]})
    assert r.status_code == 200
    snap = r.json["steps"][-1]["snapshot"]
    assert snap["guessed_length"] == 5
    assert snap["recovered_key"] == "LEMON"
    assert r.json["result"] == "".join(c for c in plain.upper() if "A" <= c <= "Z")


def test_dh_mitm_reads_message(client):
    r = client.post("/api/simulate", json={"algorithm": "dh_mitm", "input": "HELLO"})
    assert r.status_code == 200
    assert r.json["result"] == "HELLO"  # Eve recovers it
    secrets = r.json["steps"][2]["snapshot"]
    assert secrets["s_alice"] != secrets["s_bob"]  # two different secrets
    eve = r.json["steps"][3]["snapshot"]
    assert eve["s1_match"] and eve["s2_match"]
    assert r.json["steps"][-1]["snapshot"]["eve_success"] is True


def test_birthday_collision_finds_real_pair(client):
    import hashlib

    r = client.post("/api/simulate",
                    json={"algorithm": "birthday_collision", "input": "secsim",
                          "collision_bits": 12})
    assert r.status_code == 200
    snap = r.json["steps"][-1]["snapshot"]
    assert snap["first"] != snap["second"]

    def trunc(s):
        return int(hashlib.sha256(s.encode()).hexdigest(), 16) >> (256 - 12)

    assert trunc(snap["first"]) == trunc(snap["second"]) == snap["value"]
    assert snap["attempts"] >= 1


def test_dictionary_attack_cracks_and_warns(client):
    import hashlib

    hit = client.post("/api/simulate", json={
        "algorithm": "dictionary_attack",
        "input": hashlib.md5(b"password").hexdigest()})
    assert hit.status_code == 200
    assert hit.json["result"] == "password"
    miss = client.post("/api/simulate", json={
        "algorithm": "dictionary_attack",
        "input": hashlib.md5(b"zxqv-unlikely-xyz").hexdigest()})
    assert miss.status_code == 200
    snap = miss.json["steps"][-1]["snapshot"]
    assert snap["cracked"] is False
    assert "ar" in snap["warning"] and "en" in snap["warning"]


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
    for algo_id in ("caesar", "vigenere", "playfair", "rc4", "aes", "rsa", "diffie_hellman",
                    "elgamal", "md5", "sha1", "sha256", "sha512", "sha3", "pbkdf2", "brute_force",
                    "vigenere_breaker", "dh_mitm", "birthday_collision", "dictionary_attack"):
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
    assert len(algos) == 19
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

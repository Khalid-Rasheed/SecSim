"""Guard tests for the self-registering algorithm registry.

These fail loudly on the classic "forgot to wire it up" mistakes:
unregistered module, missing contract attrs, monolingual content,
or a simulate/analyze that crashes on valid input.
"""

import pathlib

import pytest

from app import create_app, db
from app.services.registry import REGISTRY, discover
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


def test_every_module_file_is_registered():
    discover()
    # precise check: each algorithm file (except __init__) registered exactly once
    root = pathlib.Path(__file__).parent.parent / "algorithms"
    files = {p.stem for p in root.rglob("*.py") if p.name != "__init__.py"}
    assert files == set(REGISTRY.keys()), f"files={files} registry={set(REGISTRY.keys())}"


STEP_KEYS = {"index", "title", "description", "snapshot", "highlight", "meta"}
SAMPLES = {
    "encryption": "Hello World",
    "hashing": "Hello World",
    "attack": "Khoor Zruog",
}

# Expected taxonomy: family/kind per algorithm id. Encryption entries
# sit in the symmetric/asymmetric tree; hashing entries in
# broken/secure/password kinds; attack entries stay flat.
EXPECTED_TAXONOMY = {
    "caesar": ("symmetric", "classical"),
    "vigenere": ("symmetric", "classical"),
    "playfair": ("symmetric", "classical"),
    "rc4": ("symmetric", "stream"),
    "aes": ("symmetric", "block"),
    "rsa": ("asymmetric", "factorization"),
    "diffie_hellman": ("asymmetric", "discrete"),
    "elgamal": ("asymmetric", "discrete"),
    "md5": ("hashing", "broken"),
    "sha1": ("hashing", "broken"),
    "sha256": ("hashing", "secure"),
    "sha512": ("hashing", "secure"),
    "sha3": ("hashing", "secure"),
    "pbkdf2": ("hashing", "password"),
    "brute_force": ("attack", None),
    "vigenere_breaker": ("attack", None),
    "dh_mitm": ("attack", None),
    "birthday_collision": ("attack", None),
    "dictionary_attack": ("attack", None),
}


def test_registry_contract_for_all(client):
    discover()
    assert len(REGISTRY) >= 19
    algos = {a["id"]: a for a in client.get("/api/algorithms").json}
    assert set(algos) == set(REGISTRY.keys())
    for algo_id, entry in REGISTRY.items():
        # meta is JSON-safe and complete
        meta = entry["meta"]
        assert meta["id"] == algo_id
        for field in ("type", "family", "kind", "security", "name", "description", "params", "complexity"):
            assert field in meta, (algo_id, field)
        assert meta["security"] in ("secure", "legacy", "broken", "educational"), algo_id
        # taxonomy placement matches the documented menu tree
        assert (meta["family"], meta["kind"]) == EXPECTED_TAXONOMY[algo_id], (algo_id, meta)
        if meta["type"] == "encryption":
            assert meta["family"] in ("symmetric", "asymmetric"), algo_id
            assert isinstance(meta["kind"], str) and meta["kind"], algo_id
        elif meta["type"] == "hashing":
            assert meta["family"] == "hashing", algo_id
            assert meta["kind"] in ("broken", "secure", "password"), algo_id
        else:
            assert meta["family"] == meta["type"], algo_id
            assert meta["kind"] is None, algo_id
        # simulate: valid input → unified steps
        sample = SAMPLES[meta["type"]]
        extra = {
            "key_size": 128,
            "key_text": "secret",
            "rsa_p": 61,
            "rsa_q": 53,
            "rsa_e": 17,
            "key": 3,
            "vigenere_key": "LEMON",
            "rc4_key": "secret",
            "dh_p": 23,
            "dh_g": 5,
            "dh_a": 6,
            "dh_b": 15,
            "mitm_e": 3,
            "mitm_f": 7,
            "collision_bits": 12,
            "elgamal_p": 2579,
            "elgamal_g": 2,
            "elgamal_x": 101,
            "elgamal_k": 7,
            "playfair_key": "MONARCHY",
            "pbkdf2_salt": "test-salt",
            "pbkdf2_iterations": 1000,
        }
        result, steps = entry["simulate"](sample, 3, "encrypt", extra)
        assert isinstance(result, str) and result
        assert len(steps) >= 2
        for i, s in enumerate(steps):
            assert set(s) >= STEP_KEYS, (algo_id, i)
            assert s["index"] == i, (algo_id, i)
            for lang_field in ("title", "description"):
                assert "ar" in s[lang_field] and "en" in s[lang_field], (algo_id, i, lang_field)
        # analyze: bilingual sections
        analysis = entry["analyze"](extra)
        for section in ("strengths", "weaknesses"):
            assert "ar" in analysis[section] and "en" in analysis[section], (algo_id, section)
        # detail endpoint mirrors registry
        detail = client.get(f"/api/algorithms/{algo_id}").json
        assert detail["details"] == entry["details"]
        assert detail["complexity"] == entry["meta"]["complexity"]


def test_unknown_algorithm_still_rejected(client):
    assert (
        client.post("/api/simulate", json={"algorithm": "rot13", "input": "x"}).status_code == 400
    )
    assert client.get("/api/algorithms/rot13").status_code == 404
    assert client.post("/api/analyze", json={"algorithm": "rot13"}).status_code == 400


def test_taxonomy_tree_groups_kinds(client):
    tree = client.get("/api/taxonomy").json
    assert [t["family"] for t in tree["tabs"]] == ["symmetric", "asymmetric", "hashing"]
    by_family = {t["family"]: t for t in tree["tabs"]}
    sym_kinds = {k["kind"] for k in by_family["symmetric"]["kinds"]}
    assert {"classical", "stream", "block"} <= sym_kinds
    asym_kinds = {k["kind"] for k in by_family["asymmetric"]["kinds"]}
    assert {"factorization", "discrete"} <= asym_kinds
    hash_kinds = {k["kind"] for k in by_family["hashing"]["kinds"]}
    assert {"broken", "secure", "password"} <= hash_kinds
    assert any(a["id"] == "brute_force" for a in tree["attacks"])


def test_security_tests_endpoint(client):
    r = client.post("/api/security-tests", json={"algorithm": "sha256", "input": "hello"})
    assert r.status_code == 200
    ids = {t["id"] for t in r.json["tests"]}
    assert {"entropy", "avalanche", "collision"} <= ids
    r2 = client.post("/api/security-tests", json={"algorithm": "caesar", "input": "Hello"})
    assert r2.status_code == 200
    assert any(t["id"] == "keyspace" for t in r2.json["tests"])
    r3 = client.post("/api/security-tests", json={"algorithm": "nope", "input": "x"})
    assert r3.status_code == 400


def test_compare_hashes_md5_vs_sha256(client):
    r = client.post("/api/compare", json={"comparisons": [
        {"algorithm": "md5", "input": "hello"},
        {"algorithm": "sha256", "input": "hello"},
    ]})
    assert r.status_code == 200
    assert [e["algorithm"] for e in r.json["results"]] == ["md5", "sha256"]
    bits = {e["algorithm"]: e["digest_bits"] for e in r.json["results"]}
    assert bits == {"md5": 128, "sha256": 256}
    for e in r.json["results"]:
        assert e["avalanche_pct"] is not None
        assert 0 <= e["avalanche_pct"] <= 100
    assert "ar" in r.json["verdict"] and "en" in r.json["verdict"]


def test_compare_aes_128_vs_256(client):
    r = client.post("/api/compare", json={"comparisons": [
        {"algorithm": "aes", "input": "Secret message",
         "parameters": {"key_text": "secret", "key_size": 128}},
        {"algorithm": "aes", "input": "Secret message",
         "parameters": {"key_text": "secret", "key_size": 256}},
    ]})
    assert r.status_code == 200
    key_bits = sorted(e["analysis_metrics"]["key_bits"] for e in r.json["results"])
    assert key_bits == [128, 256]
    assert r.json["results"][0]["result"] != r.json["results"][1]["result"]  # random IVs differ


def test_compare_rejects_bad_shapes(client):
    assert client.post("/api/compare", json={}).status_code == 400
    one = {"comparisons": [{"algorithm": "md5", "input": "x"}]}
    assert client.post("/api/compare", json=one).status_code == 400
    bad = {"comparisons": [{"algorithm": "nope", "input": "x"},
                           {"algorithm": "md5", "input": "x"}]}
    assert client.post("/api/compare", json=bad).status_code == 400

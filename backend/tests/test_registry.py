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
# must sit in the symmetric/asymmetric tree; hashing and attack
# entries carry their type as family with no subtype (shown flat).
EXPECTED_TAXONOMY = {
    "caesar": ("symmetric", "stream"),
    "aes": ("symmetric", "block"),
    "rsa": ("asymmetric", "factorization"),
    "sha256": ("hashing", None),
    "md5": ("hashing", None),
    "brute_force": ("attack", None),
}


def test_registry_contract_for_all(client):
    discover()
    assert len(REGISTRY) >= 6
    algos = {a["id"]: a for a in client.get("/api/algorithms").json}
    assert set(algos) == set(REGISTRY.keys())
    for algo_id, entry in REGISTRY.items():
        # meta is JSON-safe and complete
        meta = entry["meta"]
        assert meta["id"] == algo_id
        for field in ("type", "family", "kind", "name", "description", "params", "complexity"):
            assert field in meta, (algo_id, field)
        # taxonomy placement matches the documented menu tree
        assert (meta["family"], meta["kind"]) == EXPECTED_TAXONOMY[algo_id], (algo_id, meta)
        if meta["type"] == "encryption":
            assert meta["family"] in ("symmetric", "asymmetric"), algo_id
            assert isinstance(meta["kind"], str) and meta["kind"], algo_id
        else:
            assert meta["family"] == meta["type"], algo_id
            assert meta["kind"] is None, algo_id
        # simulate: valid input → unified steps
        sample = SAMPLES[meta["type"]]
        extra = {"key_size": 128, "key_text": "secret", "rsa_p": 61, "rsa_q": 53, "rsa_e": 17, "key": 3}
        result, steps = entry["simulate"](sample, 3, "encrypt", extra)
        assert isinstance(result, str) and result
        assert len(steps) >= 2
        for i, s in enumerate(steps):
            assert STEP_KEYS <= set(s), (algo_id, i)
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
    assert client.post("/api/simulate", json={"algorithm": "rot13", "input": "x"}).status_code == 400
    assert client.get("/api/algorithms/rot13").status_code == 404
    assert client.post("/api/analyze", json={"algorithm": "rot13"}).status_code == 400

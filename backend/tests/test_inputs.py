# -*- coding: utf-8 -*-
"""Input-matrix tests: Arabic, English, symbols, emoji, empty and long inputs."""
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


AR = "مرحبا بالعالم"
MIX = "Hello مرحبا 123"
SYM = "!@#$%^&*()_+-=[]{};:,.<>?"
EMOJI = "Hi \U0001f600\U0001f512"


def _sim(client, algo, text, **kw):
    return client.post("/api/simulate", json={"algorithm": algo, "input": text, **kw})


@pytest.mark.parametrize("text", [AR, MIX, SYM, EMOJI, ""])
def test_caesar_roundtrips_all_inputs(client, text):
    enc = _sim(client, "caesar", text, key=3)
    assert enc.status_code == 200
    dec = _sim(client, "caesar", enc.json["result"], key=3, mode="decrypt")
    assert dec.status_code == 200
    assert dec.json["result"] == text


@pytest.mark.parametrize("text", [AR, MIX, SYM, EMOJI, ""])
def test_aes_roundtrips_all_inputs(client, text):
    kw = {"key_text": "secret", "key_size": 128}
    enc = _sim(client, "aes", text, **kw)
    assert enc.status_code == 200
    dec = _sim(client, "aes", enc.json["result"], mode="decrypt", **kw)
    assert dec.status_code == 200
    assert dec.json["result"] == text


@pytest.mark.parametrize("text", [AR, MIX, SYM])
def test_rsa_roundtrips_supported_inputs(client, text):
    enc = _sim(client, "rsa", text)
    assert enc.status_code == 200
    dec = _sim(client, "rsa", enc.json["result"], mode="decrypt")
    assert dec.status_code == 200
    assert dec.json["result"] == text


def test_rsa_emoji_needs_bigger_primes(client):
    small = _sim(client, "rsa", EMOJI)
    assert small.status_code == 400
    assert "p and q" in small.json["error"]
    big = {"rsa_p": 1000003, "rsa_q": 1000033, "rsa_e": 65537}
    enc = _sim(client, "rsa", EMOJI, **big)
    assert enc.status_code == 200
    dec = _sim(client, "rsa", enc.json["result"], mode="decrypt", **big)
    assert dec.json["result"] == EMOJI


@pytest.mark.parametrize("algo,ln", [("sha256", 64), ("md5", 32)])
@pytest.mark.parametrize("text", [AR, MIX, SYM, EMOJI, ""])
def test_hashes_accept_all_inputs(client, algo, ln, text):
    r = _sim(client, algo, text)
    assert r.status_code == 200
    assert len(r.json["result"]) == ln


def test_hash_empty_string_known_vector(client):
    assert _sim(client, "sha256", "").json["result"] == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_brute_force_never_crashes(client):
    for text in (AR, MIX, SYM, EMOJI, ""):
        r = _sim(client, "brute_force", text)
        assert r.status_code == 200
        assert len(r.json["steps"]) == 27

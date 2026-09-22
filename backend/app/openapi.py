"""Machine-readable API contract, generated from code — never hand-edited.

The ``paths`` table is built from the live algorithm registry
(:mod:`app.services.registry`) plus the fixed route catalogue, so adding
an algorithm module automatically extends the served document. Served at
``GET /api/openapi.json`` (see :func:`app.create_app`). A guard test
(``tests/test_openapi.py``) asserts every registered ``/api/*`` rule —
except the spec itself — appears here, which is what keeps this file
from rotting like hand-written API docs do.
"""

STEP_SCHEMA = {
    "type": "object",
    "required": ["index", "title", "description", "snapshot", "highlight", "meta"],
    "properties": {
        "index": {"type": "integer"},
        "title": {"type": "object"},
        "description": {"type": "object"},
        "snapshot": {"type": "object"},
        "highlight": {"type": "array", "items": {"type": "integer"}},
        "meta": {"type": "object"},
    },
}

BILINGUAL = {"type": "object", "required": ["ar", "en"]}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {"error": {"type": "string"}},
}


def build_spec(algorithm_ids):
    """Assemble the OpenAPI 3.0 document for the given algorithm ids."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "SecSim API",
            "version": "1.0.0",
            "description": (
                "Interactive security-algorithms lab. Canonical base path "
                "is /api/v1; /api is kept as the legacy alias."
            ),
        },
        "servers": [{"url": "/api/v1"}, {"url": "/api"}],
        "paths": _paths(algorithm_ids),
        "components": {
            "schemas": {
                "Step": STEP_SCHEMA,
                "Bilingual": BILINGUAL,
                "Error": ERROR_SCHEMA,
                "SimulateRequest": {
                    "type": "object",
                    "required": ["algorithm", "input"],
                    "properties": {
                        "algorithm": {"type": "string", "enum": sorted(algorithm_ids)},
                        "input": {"type": "string"},
                        "key": {"description": "Caesar shift (default 3)"},
                        "mode": {"type": "string", "enum": ["encrypt", "decrypt"]},
                        "key_text": {"type": "string"},
                        "key_size": {"type": "integer", "enum": [128, 192, 256]},
                        "rsa_p": {"type": "integer"},
                        "rsa_q": {"type": "integer"},
                        "rsa_e": {"type": "integer"},
                        "vigenere_key": {"type": "string"},
                        "rc4_key": {"type": "string"},
                        "dh_p": {"type": "integer"},
                        "dh_g": {"type": "integer"},
                        "dh_a": {"type": "integer"},
                        "dh_b": {"type": "integer"},
                        "mitm_e": {"type": "integer"},
                        "mitm_f": {"type": "integer"},
                        "collision_bits": {"type": "integer", "minimum": 8, "maximum": 24},
                        "elgamal_p": {"type": "integer"},
                        "elgamal_g": {"type": "integer"},
                        "elgamal_x": {"type": "integer"},
                        "elgamal_k": {"type": "integer"},
                        "playfair_key": {"type": "string"},
                        "pbkdf2_salt": {"type": "string"},
                        "pbkdf2_iterations": {"type": "integer"},
                    },
                },
            },
            "securitySchemes": {
                "bearer": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            },
        },
    }


def _paths(algorithm_ids):  # noqa: C901 — catalogue, intentionally explicit
    ok = {"description": "Success"}
    err400 = {"description": "Bad request", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
    err401 = {"description": "Missing/invalid token", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
    err404 = {"description": "Not found", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
    bearer = [{"bearer": []}]
    return {
        "/health": {"get": {"summary": "Liveness probe", "responses": {"200": ok}}},
        "/algorithms": {
            "get": {
                "summary": "Algorithm catalog",
                "responses": {"200": ok},
            }
        },
        "/algorithms/{id}": {
            "get": {
                "summary": "Algorithm entry + bilingual reference guide",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "enum": sorted(algorithm_ids)},
                    }
                ],
                "responses": {"200": ok, "404": err404},
            }
        },
        "/taxonomy": {
            "get": {
                "summary": "Hierarchical tree: tabs (symmetric/asymmetric/hashing) + attacks",
                "responses": {"200": ok},
            }
        },
        "/security-tests": {
            "post": {
                "summary": "Live computed security tests for an algorithm on given input",
                "responses": {"200": ok, "400": err400},
            }
        },
        "/compare": {
            "post": {
                "summary": "Side-by-side comparison of 2..4 algorithms (results + verdict)",
                "responses": {"200": ok, "400": err400},
            }
        },
        "/auth/register": {
            "post": {
                "summary": "Register (email user@domain.tld, password 8+ chars with letter+digit)",
                "responses": {"201": ok, "400": err400, "409": err400, "429": err400},
            }
        },
        "/auth/login": {
            "post": {
                "summary": "Login, identical 401 for unknown email / wrong password",
                "responses": {"200": ok, "400": err400, "401": err401, "429": err400},
            }
        },
        "/auth/me": {
            "get": {
                "summary": "Token owner's profile",
                "security": bearer,
                "responses": {"200": ok, "401": err401, "404": err404},
            }
        },
        "/simulate": {
            "post": {
                "summary": "Run an algorithm, persist the run",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SimulateRequest"}
                        }
                    },
                },
                "responses": {"200": ok, "400": err400},
            }
        },
        "/analyze": {
            "post": {
                "summary": "Static security analysis without simulation",
                "responses": {"200": ok, "400": err400},
            }
        },
        "/history": {
            "get": {
                "summary": "Own runs, newest first, paged (?limit=&offset=)",
                "security": bearer,
                "responses": {"200": ok, "401": err401},
            }
        },
        "/history/{id}": {
            "get": {
                "summary": "One own run with full step trace",
                "security": bearer,
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": ok, "401": err401, "404": err404},
            }
        },
    }

"""Request schemas: single validation entry point for every endpoint.

Each ``parse_*`` helper takes raw client data and returns either a clean
dict or an error string — routes never validate inline. Centralising the
rules here keeps 400 messages consistent and gives the OpenAPI document
(``app.openapi``) one place to read request shapes from.

Conventions:
    - Missing/invalid field → ``(None, "<message>")``; the route answers 400.
    - Unknown extra keys are ignored (forward compatibility), except the
      explicit ``EXTRA_KEYS`` allow-list forwarded to the dispatcher.
    - Email is normalised (trim + lower-case) so "A@x.com" == "a@x.com".
"""
import re

# Practical email shape check (not a full RFC 5322 parser — that
# belongs to a dedicated library). Rejects missing "@", missing TLD,
# spaces and over-long input before anything touches the database.
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,}$")

# Password policy: at least 8 characters with both a letter and a
# digit. Deliberately modest for a teaching lab (no symbol mandates
# that drive users to `Password1!`), but far above a trivial minimum.
MIN_PASSWORD_LEN = 8

# Optional algorithm-specific fields accepted by POST /simulate and
# forwarded untouched into the dispatcher `extra` dict:
#   - aes: key_text (str), key_size (128|192|256)
#   - rsa: rsa_p, rsa_q, rsa_e (ints)
#   - vigenere: vigenere_key (str)
#   - rc4: rc4_key (str)
#   - diffie_hellman: dh_p, dh_g, dh_a, dh_b (ints)
#   - dh_mitm: dh_* plus mitm_e, mitm_f (ints, Eve's secrets)
#   - birthday_collision: collision_bits (8..24)
#   - elgamal: elgamal_p, elgamal_g, elgamal_x, elgamal_k (ints)
#   - playfair: playfair_key (str)
#   - pbkdf2: pbkdf2_salt (str), pbkdf2_iterations (int)
EXTRA_KEYS = (
    "key_text",
    "key_size",
    "rsa_p",
    "rsa_q",
    "rsa_e",
    "vigenere_key",
    "rc4_key",
    "dh_p",
    "dh_g",
    "dh_a",
    "dh_b",
    "mitm_e",
    "mitm_f",
    "collision_bits",
    "elgamal_p",
    "elgamal_g",
    "elgamal_x",
    "elgamal_k",
    "playfair_key",
    "pbkdf2_salt",
    "pbkdf2_iterations",
)

# History pagination bounds: generous enough for a lab, capped so one
# request can never dump the whole table.
HISTORY_DEFAULT_LIMIT = 50
HISTORY_MAX_LIMIT = 100


def password_error(password: str):
    """Return a policy-violation message, or None when acceptable."""
    if len(password) < MIN_PASSWORD_LEN:
        return f"password must be at least {MIN_PASSWORD_LEN} characters"
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        return "password must contain at least one letter and one digit"
    return None


def parse_register(data: dict):
    """Validate a registration body → (clean, error)."""
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    if not email or not password:
        return None, "email and password are required"
    if not EMAIL_RE.match(email):
        return None, "invalid email address"
    pw_error = password_error(password)
    if pw_error:
        return None, pw_error
    return {"email": email, "password": password, "name": name or None}, None


def parse_login(data: dict):
    """Validate a login body → (clean, error). Shape only — the service
    decides whether the credentials are correct (identical 401 either way)."""
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return None, "email and password are required"
    return {"email": email, "password": password}, None


def parse_simulate(data: dict):
    """Validate a simulation body → (clean, error)."""
    algorithm = data.get("algorithm")
    text = data.get("input", "")
    if not algorithm:
        return None, "algorithm is required"
    if text is None or not isinstance(text, str):
        return None, "input is required (may be empty string)"
    return {
        "algorithm": algorithm,
        "text": text,
        "key": data.get("key", 3),
        "mode": data.get("mode", "encrypt"),
        "extra": {k: data[k] for k in EXTRA_KEYS if k in data},
    }, None


def parse_analyze(data: dict):
    """Validate an analysis body → (clean, error)."""
    algorithm = data.get("algorithm")
    if not algorithm:
        return None, "algorithm is required"
    return {"algorithm": algorithm, "parameters": data.get("parameters", {}) or {}}, None


# Side-by-side comparison cap: enough for MD5 vs SHA-256 vs SHA-512
# triples, small enough that one request can never fan out.
COMPARE_MAX_ENTRIES = 4


def parse_compare(data: dict):
    """Validate a comparison body → (clean, error).

    Expected shape::

        {"comparisons": [{"algorithm": "md5", "input": "hello",
                          "parameters": {...}}, ...]}

    Each entry reuses the simulate contract (input defaults to ``""``,
    parameters default to ``{}``); unknown algorithms and domain
    rejections are reported by the route with the entry index.
    """
    items = data.get("comparisons")
    if not isinstance(items, list) or not (2 <= len(items) <= COMPARE_MAX_ENTRIES):
        return None, f"comparisons must be a list of 2..{COMPARE_MAX_ENTRIES} entries"
    clean = []
    for i, item in enumerate(items):
        if not isinstance(item, dict) or not item.get("algorithm"):
            return None, f"comparisons[{i}].algorithm is required"
        text = item.get("input", "")
        if text is None or not isinstance(text, str):
            return None, f"comparisons[{i}].input must be a string"
        params = item.get("parameters", {}) or {}
        if not isinstance(params, dict):
            return None, f"comparisons[{i}].parameters must be an object"
        clean.append({"algorithm": item["algorithm"], "text": text, "parameters": params})
    return {"comparisons": clean}, None


def parse_pagination(args):
    """Parse ?limit=&offset= query args → (limit, offset), always safe."""
    try:
        limit = int(args.get("limit", HISTORY_DEFAULT_LIMIT))
    except (TypeError, ValueError):
        limit = HISTORY_DEFAULT_LIMIT
    try:
        offset = int(args.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0
    limit = min(max(limit, 1), HISTORY_MAX_LIMIT)
    return limit, max(offset, 0)

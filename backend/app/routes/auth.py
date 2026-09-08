"""Authentication endpoints: register, login and current-user profile.

Routes:
    POST /api/auth/register: Create an account, return JWT + user (201).
    POST /api/auth/login: Verify credentials, return JWT + user (200).
    GET /api/auth/me: Return the token owner's profile (JWT required).

Abuse protection: ``register`` is capped at 5/min and ``login`` at
10/min per IP (Flask-Limiter; HTTP 429 afterwards), so credential
stuffing and mass account creation are throttled at the edge.

Token model: a signed JWT whose identity is the user's numeric id
(as a string), valid for ``JWT_ACCESS_TOKEN_EXPIRES`` (default 12h).
The frontend stores it in ``localStorage`` and sends it as
``Authorization: Bearer <token>``.
"""
import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, limiter
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

# Practical email shape check (not a full RFC 5322 parser — that
# belongs to a dedicated library). Rejects missing "@", missing TLD,
# spaces and over-long input before anything touches the database.
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,}$")

# Password policy: at least 8 characters with both a letter and a
# digit. Deliberately modest for a teaching lab (no symbol mandates
# that drive users to `Password1!`), but far above the old 6-char min.
MIN_PASSWORD_LEN = 8


def _password_error(password: str):
    """Validate ``password`` against the platform policy.

    Args:
        password: Plain-text candidate password.

    Returns:
        An error message string when the password is rejected,
        otherwise ``None``.
    """
    if len(password) < MIN_PASSWORD_LEN:
        return f"password must be at least {MIN_PASSWORD_LEN} characters"
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        return "password must contain at least one letter and one digit"
    return None


@auth_bp.post("/register")
@limiter.limit("5 per minute")
def register():
    """Create a new user account and immediately sign them in.

    Request JSON::

        {"email": "sara@mail.com", "password": "secret123", "name": "Sara"}

    Validation performed (first failure wins):
        - ``email`` and ``password`` are required (400 otherwise).
        - ``email`` must match a sane ``user@domain.tld`` shape
          (400 ``"invalid email address"`` otherwise).
        - ``password`` must satisfy the policy: ≥ 8 chars with a
          letter and a digit (400 otherwise).
        - ``email`` is lower-cased/trimmed and must be unique
          (409 ``"email already registered"`` otherwise).

    Rate limit:
        5 requests/minute per IP (429 afterwards) to block mass
        account creation.

    Returns:
        201 with ``{"token": <jwt>, "user": {...}}``.

    Example:
        >>> client.post("/api/auth/register",
        ...     json={"email": "a@a.com", "password": "secret123"})
        <201 with token + user>
    """
    data = request.get_json(force=True, silent=True) or {}
    # Normalise the email so "Sara@Mail.com" and "sara@mail.com" collide.
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "invalid email address"}), 400
    pw_error = _password_error(password)
    if pw_error:
        return jsonify({"error": pw_error}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409
    user = User(email=email, name=name or None)
    user.set_password(password)  # stores a salted hash, never the password
    db.session.add(user)
    db.session.commit()
    # Identity is the numeric id as a string (JWT "sub" must be a string).
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    """Verify credentials and issue a JWT.

    Request JSON::

        {"email": "sara@mail.com", "password": "secret123"}

    Security notes: both "unknown email" and "wrong password" return
    the identical 401 ``"invalid credentials"`` so attackers cannot
    enumerate registered emails; the 10/min/IP cap additionally slows
    online password guessing to a useless crawl.

    Rate limit:
        10 requests/minute per IP (429 afterwards).

    Returns:
        200 with ``{"token": <jwt>, "user": {...}}``;
        401 with ``{"error": "invalid credentials"}``.
    """
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()})


@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the profile of the token owner.

    Auth:
        Requires ``Authorization: Bearer <token>`` (401/422 otherwise —
        422 covers expired or malformed tokens, which the frontend
        treats as "session expired").

    Returns:
        200 with the user dict; 404 if the token's user no longer exists.
    """
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify(user.to_dict())

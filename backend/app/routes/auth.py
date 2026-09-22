"""Authentication endpoints: register, login and current-user profile.

Routes:
    POST /api/auth/register: Create an account, return JWT + user (201).
    POST /api/auth/login: Verify credentials, return JWT + user (200).
    GET /api/auth/me: Return the token owner's profile (JWT required).

Abuse protection: ``register`` is capped at 5/min and ``login`` at
10/min per IP (Flask-Limiter; HTTP 429 afterwards), so credential
stuffing and mass account creation are throttled at the edge.

Thin-route note: validation lives in :mod:`app.schemas`, persistence in
:app:mod:`app.services.auth_service`; handlers below only map between
HTTP and those layers.

Token model: a signed JWT whose identity is the user's numeric id
(as a string), valid for ``JWT_ACCESS_TOKEN_EXPIRES`` (default 12h).
The frontend stores it in ``localStorage`` and sends it as
``Authorization: Bearer <token>``.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app import limiter
from app.schemas import parse_login, parse_register
from app.services.auth_service import authenticate, create_user, get_user
from app.services.errors import ServiceError

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
@limiter.limit("5 per minute")
def register():
    """Create a new user account and immediately sign them in.

    Request JSON::

        {"email": "sara@mail.com", "password": "secret123", "name": "Sara"}

    Validation (first failure wins, all 400 except duplicates):
        - ``email`` and ``password`` are required.
        - ``email`` must match a sane ``user@domain.tld`` shape
          (``"invalid email address"`` otherwise).
        - ``password`` must satisfy the policy: ≥ 8 chars with a
          letter and a digit.
        - ``email`` must be unique (409 ``"email already registered"``).

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
    # `silent=True` turns malformed JSON into {} so we answer with our
    # own 400 message instead of raising.
    clean, error = parse_register(request.get_json(force=True, silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    try:
        user = create_user(clean["email"], clean["password"], clean["name"])
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
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
    clean, error = parse_login(request.get_json(force=True, silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    user = authenticate(clean["email"], clean["password"])
    if not user:
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
    user = get_user(get_jwt_identity())
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify(user.to_dict())

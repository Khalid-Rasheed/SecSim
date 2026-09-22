"""Auth service: user lifecycle without any HTTP in sight.

All persistence and credential checks live here; routes only translate
results to status codes. Token *minting* stays in the route layer because
it is transport (JWT), not domain logic.
"""
from app import db
from app.models.user import User
from app.services.errors import ServiceError


def create_user(email: str, password: str, name=None) -> User:
    """Persist a new user (email must already be validated + unique-checked).

    Raises:
        ServiceError: 409 when the lower-cased email is already taken
            (checked here as well so concurrent inserts fail loudly
            instead of violating the UNIQUE constraint silently).
    """
    if User.query.filter_by(email=email).first():
        raise ServiceError("email already registered", 409)
    user = User(email=email, name=name)
    user.set_password(password)  # stores a salted hash, never the password
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email: str, password: str):
    """Return the user when credentials match, else None.

    Unknown email and wrong password are intentionally indistinguishable
    (both → None → identical 401) so emails cannot be enumerated.
    """
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None
    return user


def get_user(user_id: int):
    """Return a user by id, or None when missing/invalid."""
    try:
        return User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None

"""User account model: credentials plus profile fields.

Passwords are never stored — only a Werkzeug salted hash
(see :meth:`User.set_password`). The public shape is defined by
:meth:`User.to_dict`, which is what the auth endpoints return.
"""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """Registered SecSim user who can own simulation history rows.

    Attributes:
        id: Primary key; also embedded (as a string) in JWT tokens.
        name: Optional display name shown in the UI.
        email: Unique, lower-cased login identifier (indexed).
        password_hash: Werkzeug salted password hash — write-only.
        created_at: UTC signup timestamp.
        simulations: Related :class:`Simulation` rows (lazy-loaded).
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # One user → many saved simulations (Simulation.user_id FK).
    simulations = db.relationship("Simulation", backref="user", lazy=True)

    def set_password(self, password: str):
        """Hash ``password`` (salted, via Werkzeug) and store the hash.

        Args:
            password: Plain-text password; never persisted itself.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a login attempt against the stored hash.

        Uses constant-time comparison internally. Returns ``False``
        for wrong passwords without revealing whether the email exists
        (callers combine both checks into "invalid credentials").

        Args:
            password: Plain-text candidate password.

        Returns:
            True when the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize the safe public profile (never the password hash).

        Returns:
            Dict with ``id``, ``name``, ``email`` and ISO ``created_at``.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

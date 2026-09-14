"""Simulation history model: one persisted run of ``POST /api/simulate``.

Every simulation — anonymous or authenticated — is stored, so the lab
keeps a full audit trail. Rows with ``user_id = NULL`` are anonymous;
``GET /api/history`` only ever returns the caller's own rows.
"""

from datetime import UTC, datetime

from app import db


class Simulation(db.Model):
    """A single executed simulation with its inputs and full step trace.

    Attributes:
        id: Primary key, returned as ``id`` by ``POST /api/simulate``.
        user_id: Owner's :class:`User` id, or ``None`` for anonymous runs.
        algorithm: Algorithm id (``"caesar"``, ``"aes"``, ...).
        input_text: Raw user input the algorithm ran on.
        params: JSON dict of run parameters
            (``{"key": 3, "mode": "encrypt", ...}``).
        result: Final output string (ciphertext / plaintext / digest).
        steps: JSON list of step dicts following the unified schema
            (``index`` / ``title{ar,en}`` / ``description{ar,en}`` /
            ``snapshot`` / ``highlight`` / ``meta``).
        duration_ms: Measured wall-clock execution time in milliseconds.
        created_at: UTC timestamp of the run (history sort key).
    """

    __tablename__ = "simulations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    algorithm = db.Column(db.String(50), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    params = db.Column(db.JSON, nullable=True)
    result = db.Column(db.Text, nullable=True)
    steps = db.Column(db.JSON, nullable=True)
    duration_ms = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def to_dict(self, include_steps=False):
        """Serialize the record for history endpoints.

        Args:
            include_steps: When True, embed the full ``steps`` trace
                (used by the detail endpoint). When False (default),
                return only ``steps_count`` to keep list responses light.

        Returns:
            Dict with ``id``, ``algorithm``, ``input``, ``params``,
            ``result``, ``duration_ms``, ``created_at`` plus either
            ``steps`` or ``steps_count``.
        """
        data = {
            "id": self.id,
            "algorithm": self.algorithm,
            "input": self.input_text,
            "params": self.params or {},
            "result": self.result,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_steps:
            data["steps"] = self.steps or []
        else:
            data["steps_count"] = len(self.steps or [])
        return data

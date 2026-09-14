"""Model package: re-export ORM classes for convenient imports.

Importing this package registers both models with SQLAlchemy, so
``from app.models import User, Simulation`` (or importing the
submodules directly) is enough for migrations and queries.
"""

from app import db  # noqa: F401  (re-exported for backward compatibility)
from app.models.simulation import Simulation  # noqa: F401
from app.models.user import User  # noqa: F401

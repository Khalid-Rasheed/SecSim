"""Application configuration.

All settings are read from environment variables (see ``backend/.env``,
whose defaults live in ``backend/.env.example``) with safe development
fallbacks so the app boots with zero setup.

Attributes:
    SECRET_KEY: Flask session / signing secret. Override in production.
    JWT_SECRET_KEY: Secret used to sign JWT access tokens. Override in
        production — anyone holding it can forge tokens.
    JWT_ACCESS_TOKEN_EXPIRES: Lifetime of login tokens (default 12h,
        overridable via ``JWT_ACCESS_HOURS``). The frontend detects
        expiry (HTTP 401/422) and routes back to login with a clear
        "session expired" notice.
    RATELIMIT_STORAGE_URI: Where rate-limit counters live. In-memory
        by default (single process); point at Redis (e.g.
        ``redis://localhost:6379``) when running multiple workers.
    RATELIMIT_DEFAULT: Global safety net applied to every ``/api/*``
        route (default ``200/minute`` per IP).
    SQLALCHEMY_DATABASE_URI: Database URL. Defaults to a local SQLite
        file (``secsim.db``); set ``DATABASE_URL`` for Postgres/MySQL.
    SQLALCHEMY_TRACK_MODIFICATIONS: Always ``False`` — disables the
        event system that only wastes memory.

Example:
    Set a custom database before launching::

        $env:DATABASE_URL = "postgresql://user:pw@localhost/secsim"
        py run.py
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load ``backend/.env`` into the process environment before reading below.
load_dotenv()


class Config:
    """Base configuration shared by development, tests and production."""

    SECRET_KEY = os.getenv("SECRET_KEY", "secsim-dev-secret-key-32-chars-minimum!")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secsim-jwt-secret-key-32-chars-minimum!")
    # Explicit (not the 15-minute library default): long enough for a lab
    # session, short enough that a stolen token expires the same day.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_HOURS", "12")))
    # Rate limiting (Flask-Limiter). Memory storage suits a single dev
    # process; production with gunicorn workers should set RATELIMIT_URL
    # to a shared Redis so counters are consistent across workers.
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_URL", "memory://")
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per minute")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///secsim.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

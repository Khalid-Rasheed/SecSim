"""Flask application factory for SecSim.

This package wires together extensions, blueprints and error handling.
Create the app via :func:`create_app` (production code and tests both
use this single entry point)::

    from app import create_app
    app = create_app()

Extension instances (``db``, ``migrate``, ``jwt``, ``limiter``) are created here
unbound and initialised inside the factory, which keeps imports
cycle-free: routes import ``db`` from this package, and this package
imports routes only inside the factory function.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

# Unbound extensions — bound to the app inside create_app().
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
# Abuse shield: per-IP sliding-window counters (memory by default,
# Redis via RATELIMIT_URL in production). Auth routes add stricter
# per-endpoint limits on top of the global default below.
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per minute"])


def create_app(config_class=Config):
    """Build and configure a Flask application instance.

    Steps performed:
        1. Load settings from ``config_class``.
        2. Initialise SQLAlchemy, Flask-Migrate, JWT, CORS and the rate
           limiter (storage from ``RATELIMIT_STORAGE_URI``).
        3. Register the ``auth`` / ``algorithms`` / ``simulation`` /
           ``analysis`` blueprints under ``/api/*``.
        4. Install JSON error handlers (400/404/405/500) so API clients
           — including browsers enforcing CORS — always receive a
           readable JSON body with CORS headers attached, instead of
           an opaque HTML error page.
        5. Create all tables (convenience for SQLite dev runs;
           production schema changes should go through migrations).

    Args:
        config_class: Configuration object (defaults to
            :class:`config.Config`). Tests pass a subclass pointing
            at an in-memory SQLite database.

    Returns:
        The configured :class:`flask.Flask` application.

    Example:
        >>> app = create_app()
        >>> client = app.test_client()
        >>> client.get("/api/health").json
        {'status': 'ok', 'service': 'SecSim'}
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    # Public API: any origin may call /api/* (the API is stateless and
    # authorises via Bearer tokens, never cookies, so a wildcard is safe).
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Imported here (not at top level) to avoid circular imports:
    # models need `db`, which only exists after the lines above.
    from app.models.simulation import Simulation  # noqa: F401
    from app.models.user import User  # noqa: F401
    from app.routes.algorithms import algorithms_bp
    from app.routes.analysis import analysis_bp
    from app.routes.auth import auth_bp
    from app.routes.simulation import simulation_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(algorithms_bp, url_prefix="/api")
    app.register_blueprint(simulation_bp, url_prefix="/api")
    app.register_blueprint(analysis_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        """Liveness probe used by scripts, containers and the frontend.

        Returns:
            ``{"status": "ok", "service": "SecSim"}`` with HTTP 200.
        """
        return {"status": "ok", "service": "SecSim"}

    # JSON error responses (instead of HTML pages) so API clients —
    # including browsers enforcing CORS — always get a readable body
    # with CORS headers attached by flask-cors.
    @app.errorhandler(400)
    def bad_request(e):
        """Return ``{"error": "bad request"}`` for malformed requests."""
        return jsonify({"error": "bad request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        """Return ``{"error": "not found"}`` for unknown routes/ids."""
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        """Return ``{"error": "method not allowed"}`` for wrong verbs."""
        return jsonify({"error": "method not allowed"}), 405

    @app.errorhandler(429)
    def rate_limited(e):
        """Return JSON (not HTML) when Flask-Limiter rejects a caller.

        The message stays generic on purpose — no reset timers are
        leaked to potential attackers.
        """
        return jsonify({"error": "rate limit exceeded, try again later"}), 429

    @app.errorhandler(500)
    def internal_error(e):
        """Catch-all: hide tracebacks, return a generic JSON error."""
        return jsonify({"error": "internal server error"}), 500

    with app.app_context():
        db.create_all()

    return app

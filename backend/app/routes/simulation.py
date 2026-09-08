"""Simulation endpoints: run algorithms and browse saved history.

Routes:
    POST /api/simulate: Execute any registered algorithm on user input
        and persist the run (anonymously, or linked to the caller when
        a valid JWT is supplied).
    GET /api/history: List the caller's own past runs (JWT required).
    GET /api/history/<id>: Fetch one run with its full step trace
        (JWT required, owner-only).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
from app import db
from app.models.simulation import Simulation
from app.services.simulator import run_simulation

simulation_bp = Blueprint("simulation", __name__)

# Optional algorithm-specific fields accepted from the client and
# forwarded untouched into the dispatcher `extra` dict:
#   - aes: key_text (str), key_size (128|192|256)
#   - rsa: rsa_p, rsa_q, rsa_e (ints)
EXTRA_KEYS = ("key_text", "key_size", "rsa_p", "rsa_q", "rsa_e")


@simulation_bp.post("/simulate")
def simulate():
    """Run an algorithm and persist the result as a history record.

    Request JSON (all fields optional except ``algorithm``)::

        {
          "algorithm": "caesar",      # required: registry id
          "input": "Hello World",     # required (may be "")
          "key": 3,                   # caesar shift (default 3)
          "mode": "encrypt",          # "encrypt" | "decrypt"
          "key_text": "secret",       # aes only
          "key_size": 128,            # aes only: 128 | 192 | 256
          "rsa_p": 61,                # rsa only (with rsa_q, rsa_e)
        }

    Auth is optional: when the request carries a valid Bearer token
    the run is linked to that user (visible in their history);
    otherwise it is stored anonymously (``user_id = NULL``). An
    invalid/expired token never blocks the simulation — the run is
    simply saved without an owner.

    Returns:
        200 with ``{id, algorithm, result, steps[], metrics{time_ms,
        steps}, analysis{...}}``; 400 with ``{"error": ...}`` for
        missing input or algorithm-level ``ValueError`` rejections
        (bad key size, bad ciphertext format, unknown algorithm...).
    """
    # `silent=True` turns malformed JSON into {} so we can answer
    # with our own 400 message instead of raising.
    data = request.get_json(force=True, silent=True) or {}
    algorithm = data.get("algorithm")
    text = data.get("input", "")
    key = data.get("key", 3)
    mode = data.get("mode", "encrypt")
    # Pick only known extra keys — anything else is ignored, never stored.
    extra = {k: data[k] for k in EXTRA_KEYS if k in data}

    if not algorithm:
        return jsonify({"error": "algorithm is required"}), 400
    if text is None or not isinstance(text, str):
        return jsonify({"error": "input is required (may be empty string)"}), 400
    try:
        result, steps, metrics, analysis = run_simulation(algorithm, text, key, mode, extra)
    except ValueError as e:
        # Expected domain errors (unknown algorithm, bad params) → 400.
        # Unexpected exceptions propagate to the 500 JSON handler.
        return jsonify({"error": str(e)}), 400

    # Optional auth: save history with user if a valid JWT was provided.
    # `optional=True` means "no token" is fine; any verification failure
    # (expired/forged token) is swallowed and the run stays anonymous.
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        ident = get_jwt_identity()
        user_id = int(ident) if ident is not None else None
    except Exception:
        user_id = None

    record = Simulation(
        user_id=user_id,
        algorithm=algorithm,
        input_text=text,
        params={"key": key, "mode": mode, **extra},
        result=result,
        steps=steps,
        duration_ms=metrics["time_ms"],
    )
    db.session.add(record)
    db.session.commit()

    return jsonify(
        {
            "id": record.id,
            "algorithm": algorithm,
            "result": result,
            "steps": steps,
            "metrics": metrics,
            "analysis": analysis,
        }
    )


@simulation_bp.get("/history")
@jwt_required()
def history():
    """List the authenticated user's runs, newest first (max 50).

    Auth:
        Requires ``Authorization: Bearer <token>`` (401 otherwise).

    Returns:
        200 with a JSON array of records serialized *without* steps
        (each carries ``steps_count`` instead) to keep the payload small.
    """
    ident = get_jwt_identity()
    rows = (
        Simulation.query.filter_by(user_id=int(ident))
        .order_by(Simulation.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([r.to_dict() for r in rows])


@simulation_bp.get("/history/<int:sim_id>")
@jwt_required()
def history_detail(sim_id: int):
    """Fetch one history record including its full step trace.

    Args:
        sim_id: The record id returned by ``POST /api/simulate``.

    Auth:
        Requires Bearer token; users can only read their own rows —
        any other id (or a missing row) yields 404, never 403, so
        record ids of other users cannot be probed.

    Returns:
        200 with the record (``steps`` embedded); 404 with
        ``{"error": "not found"}``.
    """
    ident = get_jwt_identity()
    row = Simulation.query.filter_by(id=sim_id, user_id=int(ident)).first()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row.to_dict(include_steps=True))

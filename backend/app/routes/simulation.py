"""Simulation endpoints: run algorithms and browse saved history.

Routes:
    POST /api/simulate: Execute any registered algorithm on user input
        and persist the run (anonymously, or linked to the caller when
        a valid JWT is supplied).
    GET /api/history: List the caller's own past runs, paged (JWT required).
    GET /api/history/<id>: Fetch one run with its full step trace
        (JWT required, owner-only).

Thin-route note: validation lives in :mod:`app.schemas`, persistence in
:app:mod:`app.services.history_service`, execution in
:mod:`app.services.simulator`; handlers below only map between HTTP
and those layers.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request

from app.schemas import parse_pagination, parse_simulate
from app.services.history_service import get_run, list_runs, save_run
from app.services.simulator import run_simulation

simulation_bp = Blueprint("simulation", __name__)


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
    clean, error = parse_simulate(request.get_json(force=True, silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    try:
        result, steps, metrics, analysis = run_simulation(
            clean["algorithm"], clean["text"], clean["key"], clean["mode"], clean["extra"]
        )
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

    record = save_run(
        user_id,
        clean["algorithm"],
        clean["text"],
        clean["key"],
        clean["mode"],
        clean["extra"],
        result,
        steps,
        metrics["time_ms"],
    )
    return jsonify(
        {
            "id": record.id,
            "algorithm": clean["algorithm"],
            "result": result,
            "steps": steps,
            "metrics": metrics,
            "analysis": analysis,
        }
    )


@simulation_bp.get("/history")
@jwt_required()
def history():
    """List the authenticated user's runs, newest first, paged.

    Query args:
        ``limit`` (default 50, max 100), ``offset`` (default 0).

    Auth:
        Requires ``Authorization: Bearer <token>`` (401 otherwise).

    Returns:
        200 with ``{total, limit, offset, items[]}``; items are
        serialized *without* steps (each carries ``steps_count``)
        to keep the payload small.
    """
    limit, offset = parse_pagination(request.args)
    rows, total = list_runs(get_jwt_identity(), limit, offset)
    return jsonify(
        {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [r.to_dict() for r in rows],
        }
    )


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
    row = get_run(sim_id, get_jwt_identity())
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row.to_dict(include_steps=True))

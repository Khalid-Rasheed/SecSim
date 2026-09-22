"""History service: persistence queries for simulation runs.

Owns every Simulation query (save / list / owner-scoped fetch) so routes
stay thin and the rules — newest-first, owner-only reads, bounded pages —
live in exactly one place.
"""
from app import db
from app.models.simulation import Simulation


def save_run(user_id, algorithm, text, key, mode, extra, result, steps, duration_ms) -> Simulation:
    """Persist one simulation run; ``user_id`` may be None (anonymous)."""
    record = Simulation(
        user_id=user_id,
        algorithm=algorithm,
        input_text=text,
        params={"key": key, "mode": mode, **(extra or {})},
        result=result,
        steps=steps,
        duration_ms=duration_ms,
    )
    db.session.add(record)
    db.session.commit()
    return record


def list_runs(user_id: int, limit: int, offset: int):
    """Return (rows, total) for one user, newest first, bounded page."""
    base = Simulation.query.filter_by(user_id=int(user_id))
    total = base.count()
    rows = base.order_by(Simulation.created_at.desc()).limit(limit).offset(offset).all()
    return rows, total


def get_run(sim_id: int, user_id: int):
    """Return one run owned by ``user_id``, else None.

    Deliberately no 403 path: other users' ids look identical to
    missing ids (404), so record ids cannot be probed.
    """
    return Simulation.query.filter_by(id=sim_id, user_id=int(user_id)).first()

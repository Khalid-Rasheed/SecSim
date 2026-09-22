"""Algorithm catalog endpoints: list entries and full reference guides.

Routes:
    GET /api/algorithms: Lightweight catalog of every registered
        algorithm (metadata + complexity, no DETAILS).
    GET /api/algorithms/<id>: Full entry for one algorithm, including
        its bilingual ``details`` reference guide (overview, history,
        how-it-works, parameters, security, uses).

Both read from the self-registering :mod:`app.services.registry`
(via :mod:`app.services.simulator`), so adding a module file under
``algorithms/`` automatically extends this catalog — no route edits.
"""

from flask import Blueprint, jsonify

from app.services.simulator import get_algorithm_detail, get_taxonomy, list_algorithms

algorithms_bp = Blueprint("algorithms", __name__)


@algorithms_bp.get("/algorithms")
def get_algorithms():
    """List all registered algorithms (catalog view).

    Returns:
        200 with ``[{id, type, name{ar,en}, description{ar,en},
        params, keyspace, complexity}]`` ordered by registry ``order``.
    """
    return jsonify(list_algorithms())


@algorithms_bp.get("/taxonomy")
def get_taxonomy_tree():
    """Return the hierarchical taxonomy tree.

    Returns:
        200 with ``{tabs: [{family, name{ar,en}, kinds: [{kind, name,
        items: [meta]}]}], attacks: [meta]}`` — drives the 3-tab UI
        (symmetric | asymmetric | hashing) plus the attack lab.
    """
    return jsonify(get_taxonomy())


@algorithms_bp.get("/algorithms/<algo_id>")
def get_algorithm(algo_id: str):
    """Return one algorithm with its full bilingual reference guide.

    Args:
        algo_id: Registry id, e.g. ``"caesar"``, ``"aes"``, ``"rsa"``,
            ``"sha256"``, ``"md5"``, ``"brute_force"``.

    Returns:
        200 with the catalog entry plus ``details{overview, history,
        how_it_works, parameters, security, uses}``; 404 with
        ``{"error": ...}`` for unknown ids.
    """
    try:
        return jsonify(get_algorithm_detail(algo_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

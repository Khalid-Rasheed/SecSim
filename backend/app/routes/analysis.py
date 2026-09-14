"""Standalone analysis endpoint: security review without simulation.

Route:
    POST /api/analyze: Return the static security analysis
    (strengths, weaknesses, metrics, complexity) for an algorithm —
    useful for theory pages that need no input text and no step trace.
"""

from flask import Blueprint, jsonify, request

from app.services.simulator import analyze_algorithm, list_algorithms

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.post("/analyze")
def analyze():
    """Return the static security analysis for one algorithm.

    Request JSON::

        {"algorithm": "rsa", "parameters": {"rsa_p": 61, "rsa_q": 53}}

    The optional ``parameters`` dict is forwarded to the algorithm's
    ``analyze()`` so metrics can reflect concrete values (e.g. RSA
    key size in bits, AES round count for a given key size).

    Returns:
        200 with ``{"algorithm": <id>, "analysis": {...}}``;
        400 with ``{"error": ...}`` for a missing/unsupported
        algorithm or invalid parameters.
    """
    data = request.get_json(force=True, silent=True) or {}
    algorithm = data.get("algorithm")
    if not algorithm:
        return jsonify({"error": "algorithm is required"}), 400
    if algorithm not in {a["id"] for a in list_algorithms()}:
        return jsonify({"error": f"Unsupported algorithm: {algorithm}"}), 400
    params = data.get("parameters", {}) or {}
    try:
        return jsonify({"algorithm": algorithm, "analysis": analyze_algorithm(algorithm, params)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

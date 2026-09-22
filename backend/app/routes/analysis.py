"""Standalone analysis endpoint: security review without simulation.

Route:
    POST /api/analyze: Return the static security analysis
    (strengths, weaknesses, metrics, complexity) for an algorithm —
    useful for theory pages that need no input text and no step trace.
"""

from flask import Blueprint, jsonify, request

from app.schemas import parse_analyze
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
    clean, error = parse_analyze(data)
    if error:
        return jsonify({"error": error}), 400
    algorithm, params = clean["algorithm"], clean["parameters"]
    if algorithm not in {a["id"] for a in list_algorithms()}:
        return jsonify({"error": f"Unsupported algorithm: {algorithm}"}), 400
    try:
        return jsonify({"algorithm": algorithm, "analysis": analyze_algorithm(algorithm, params)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

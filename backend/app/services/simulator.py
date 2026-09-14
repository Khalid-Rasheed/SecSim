"""Central dispatcher: validate input, run an algorithm, measure time.

Design: algorithms self-register via :mod:`app.services.registry`, so
this module knows no algorithm by name — every call goes through
:func:`registry.lookup`. To add an algorithm, drop a new module under
``algorithms/`` with a ``register(...)`` call (see ``README``,
"Adding an algorithm"); it is picked up automatically at import time
by the :func:`registry.discover` call below.

Every simulation returns the same tuple::

    (result, steps, metrics, analysis)

- ``result``: final output string (ciphertext / plaintext / digest).
- ``steps``: list of step dicts in the unified schema —
  ``index`` / ``title{ar,en}`` / ``description{ar,en}`` / ``snapshot``
  / ``highlight`` / ``meta`` — rendered by the frontend step player.
- ``metrics``: ``{"time_ms": <wall-clock>, "steps": <count>}``.
- ``analysis``: static security review ``{strengths, weaknesses,
  metrics, complexity}``.
"""

import time

from app.services.registry import discover, lookup, ordered

# Import every module under algorithms/{encryption,hashing,attacks} so
# each one's register(...) call executes exactly once at startup.
discover()


def list_algorithms():
    """Return catalog metadata for every registered algorithm.

    Returns:
        List of ``{id, type, name{ar,en}, description{ar,en}, params,
        keyspace, complexity}`` dicts in registry ``order`` (teaching
        order: classical → modern → attacks). Powers
        ``GET /api/algorithms``.
    """
    return [entry["meta"] for entry in ordered()]


def get_algorithm_detail(algorithm: str):
    """Return one algorithm's catalog entry plus its reference guide.

    Args:
        algorithm: Registry id (e.g. ``"caesar"``, ``"sha256"``).

    Raises:
        ValueError: If ``algorithm`` is not registered.

    Returns:
        Dict merging the catalog entry with ``details{overview,
        history, how_it_works, parameters, security, uses}``. Powers
        ``GET /api/algorithms/<id>``.
    """
    entry = lookup(algorithm)
    return {**entry["meta"], "details": entry["details"]}


def analyze_algorithm(algorithm: str, extra: dict | None = None):
    """Run only the static security analysis (no simulation).

    Args:
        algorithm: Registry id.
        extra: Optional parameter overrides forwarded to the
            algorithm's ``analyze()`` (e.g. ``{"key_size": 256}`` so
            AES reports 14 rounds instead of the default 10).

    Raises:
        ValueError: If ``algorithm`` is not registered.

    Returns:
        ``{strengths{ar,en}, weaknesses{ar,en}, metrics, complexity}``.
        Powers ``POST /api/analyze``.
    """
    entry = lookup(algorithm)
    return entry["analyze"](extra or {})


def run_simulation(
    algorithm: str, text: str, key=3, mode: str = "encrypt", extra: dict | None = None
):
    """Execute a full simulation: run, time, and analyse.

    Args:
        algorithm: Registry id (e.g. ``"caesar"``, ``"aes"``,
            ``"brute_force"``).
        text: Raw user input (plaintext, ciphertext or text to hash).
        key: Legacy positional slot kept for the uniform contract
            ``simulate(text, key, mode, extra)``. Caesar reads it as
            the shift; other algorithms take their parameters from
            ``extra`` instead (see each module's ``simulate``).
        mode: ``"encrypt"`` (default) or ``"decrypt"``. Hashing and
            attack modules ignore it.
        extra: Algorithm-specific parameters, e.g.
            ``{"key_text": ..., "key_size": 128}`` for AES or
            ``{"rsa_p": 61, "rsa_q": 53, "rsa_e": 17}`` for RSA.

    Raises:
        ValueError: Unknown algorithm, or any domain rejection raised
            by the algorithm itself (bad key size, undecryptable
            input, oversized characters for the RSA modulus...).

    Returns:
        Tuple ``(result, steps, metrics, analysis)`` as described in
        the module docstring. Powers ``POST /api/simulate``.

    Example:
        >>> run_simulation("caesar", "Hello", 3, "encrypt", {})[0]
        'Khoor'
    """
    entry = lookup(algorithm)
    start = time.perf_counter()
    # `text or ""` normalises None → "" so algorithms never see None.
    result, steps = entry["simulate"](text or "", key, mode or "encrypt", extra or {})
    duration_ms = (time.perf_counter() - start) * 1000
    metrics = {"time_ms": round(duration_ms, 3), "steps": len(steps)}
    # Static analysis runs alongside (cheap); `key` is merged in so
    # Caesar's report can echo the effective shift.
    analysis = entry["analyze"]({**(extra or {}), "key": key})
    return result, steps, metrics, analysis

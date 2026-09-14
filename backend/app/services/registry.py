"""Self-registering algorithm registry (the live plugin system).

How it works:
    1. Each module under ``algorithms/{encryption,hashing,attacks}/``
       ends with a single ``register(...)`` call describing itself.
    2. :func:`discover` imports every such module, which executes
       those calls and fills :data:`REGISTRY`.
    3. The rest of the backend (routes, dispatcher, tests) only talks
       to :func:`lookup` / :func:`ordered` — never to algorithm
       modules directly.

Adding a new algorithm = one new module file, zero edits elsewhere:

    1. Create ``algorithms/<family>/myalgo.py``.
    2. Define ``COMPLEXITY``, ``DETAILS``, ``simulate()``, ``analyze()``.
    3. End the file with ``register("myalgo", type=..., ...)``.
    4. Guard tests in ``tests/test_registry.py`` verify the contract
       automatically (registration, bilingual content, step schema).

Registry entry shape::

    {
      "meta": {"id", "type", "family", "kind", "name", "description",
               "params", "keyspace", "complexity"},
      "details": <bilingual reference guide>,
      "simulate": <callable(text, key, mode, extra) -> (result, steps)>,
      "analyze": <callable(extra) -> analysis dict>,
      "order": <int teaching order>,
    }

Taxonomy (drives the frontend dropdown and simulator grouping):
    - type="encryption" → family "symmetric" (kinds: "stream",
      "block") or "asymmetric" (kinds: "factorization", ...).
    - type="hashing" → family "hashing", kind None (listed flat).
    - type="attack" → family "attack", kind None (listed flat).
"""

import importlib
import pkgutil
import sys

# id -> registry entry (see module docstring for the entry shape).
REGISTRY = {}

# Every algorithm module must expose these four attributes; missing
# ones fail fast at import time with a clear ImportError.
_REQUIRED_ATTRS = ("simulate", "analyze", "COMPLEXITY", "DETAILS")


def algorithm(
    id, *, type, name, description, params, keyspace=None, order=100, family=None, kind=None
):
    """Attach metadata to an already-imported module object; validate.

    This is the decorator form of registration; prefer
    :func:`register` (which targets the calling module) at the end of
    algorithm files.

    Args:
        id: Unique algorithm id used in URLs and API payloads
            (e.g. ``"caesar"``).
        type: One of ``"encryption"`` | ``"hashing"`` | ``"attack"`` —
            drives frontend icons, sample inputs and test matrices.
        name: Bilingual display name ``{"ar": ..., "en": ...}``.
        description: Bilingual one-liner ``{"ar": ..., "en": ...}``.
        params: Parameter names the simulator UI should collect
            (e.g. ``["key", "mode"]``).
        keyspace: Keyspace hint for teaching (``25``, ``"2^128+"``,
            ``"toy"``, or ``None`` for hashes).
        order: Teaching order in catalog listings (lower first).
        family: Taxonomy family for menu grouping — ``"symmetric"`` /
            ``"asymmetric"`` for encryption, ``"hashing"`` / ``"attack"``
            otherwise (mirrors ``type`` there).
        kind: Subtype within the family — e.g. ``"stream"`` / ``"block"``
            under symmetric, ``"factorization"`` under asymmetric;
            ``None`` for hashing/attack entries (shown flat).

    Raises:
        ImportError: If the module misses a required attribute or the
            ``id`` is already registered (duplicate).

    Returns:
        A decorator that registers the module and returns it unchanged.
    """

    def wrap(module):
        missing = [a for a in _REQUIRED_ATTRS if not hasattr(module, a)]
        if missing:
            raise ImportError(f"algorithm '{id}' is missing: {', '.join(missing)}")
        if id in REGISTRY:
            raise ImportError(f"duplicate algorithm id: '{id}'")
        REGISTRY[id] = {
            "meta": {
                "id": id,
                "type": type,
                "family": family,
                "kind": kind,
                "name": name,
                "description": description,
                "params": params,
                "keyspace": keyspace,
                "complexity": module.COMPLEXITY,
            },
            "details": module.DETAILS,
            "simulate": module.simulate,
            "analyze": module.analyze,
            "order": order,
        }
        return module

    return wrap


def register(id, **meta):
    """Register the calling module (use at the end of an algorithm file).

    Introspects one stack frame to find the caller's module object,
    then delegates to :func:`algorithm`. Keyword arguments are the
    metadata documented there (``type``, ``family``, ``kind``,
    ``name``, ``description``, ``params``, ``keyspace``, ``order``).

    Args:
        id: Unique algorithm id.
        **meta: Registry metadata (see :func:`algorithm`).

    Returns:
        The caller's module object, registered in :data:`REGISTRY`.

    Example:
        At the end of ``algorithms/encryption/caesar.py``::

            register(
                "caesar",
                type="encryption",
                family="symmetric",
                kind="stream",
                name={"ar": "قيصر", "en": "Caesar"},
                description={...},
                params=["key", "mode"],
                keyspace=25,
                order=10,
            )
    """
    caller = sys._getframe(1).f_globals["__name__"]
    return algorithm(id, **meta)(sys.modules[caller])


def discover():
    """Import every module under algorithms/{encryption,hashing,attacks}/.

    Importing triggers each module's ``register(...)`` call
    (self-registration). Safe to call multiple times (re-import is a
    no-op, and ``register`` would raise on true duplicates, which
    would indicate two files claiming the same id).
    """
    for package in ("algorithms.encryption", "algorithms.hashing", "algorithms.attacks"):
        try:
            sub = importlib.import_module(package)
        except ImportError:
            continue
        for info in pkgutil.iter_modules(sub.__path__, sub.__name__ + "."):
            importlib.import_module(info.name)


def lookup(algorithm: str):
    """Fetch one registry entry by id.

    Args:
        algorithm: Registry id (e.g. ``"aes"``).

    Raises:
        ValueError: If the id is not registered. Routes translate
            this into 400/404 responses.

    Returns:
        The registry entry dict (see module docstring for its shape).
    """
    try:
        return REGISTRY[algorithm]
    except KeyError:
        raise ValueError(f"Unsupported algorithm: {algorithm}") from None


def ordered():
    """Return all registry entries sorted by teaching ``order``.

    Returns:
        List of entry dicts, lowest ``order`` first — this ordering
        drives ``GET /api/algorithms`` and the simulator UI.
    """
    return [REGISTRY[k] for k in sorted(REGISTRY, key=lambda k: REGISTRY[k]["order"])]

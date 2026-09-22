"""Shared security-test helpers: computed (not static) analysis.

These power POST /api/security-tests — the interactive layer the user
asked for. Every function is pure, fast and dependency-free so both
algorithm modules (for ``analyze()`` metrics) and the security route
(for live per-input tests) can share them.

Conventions:
    - All helpers return JSON-safe primitives.
    - Human-readable durations are returned bilingual ``{ar, en}``.
    - ``None`` inputs degrade gracefully (empty text → entropy 0).
"""

import hashlib
import math


# Assumed attacker speed for crack-time estimates: 10 billion
# guesses/second (single modern GPU vs fast hashes; conservative
# for slow KDFs — the estimate is labelled as such in the UI).
GUESSES_PER_SECOND = 10_000_000_000


def shannon_entropy_bits(text: str) -> float:
    """Shannon entropy of ``text`` in bits (total, not per-char).

    Args:
        text: Input string (any language).

    Returns:
        Total entropy rounded to 2 decimals. Empty text → 0.0.
    """
    if not text:
        return 0.0
    freq: dict[str, int] = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(text)
    ent_per_char = -sum((c / n) * math.log2(c / n) for c in freq.values())
    return round(ent_per_char * n, 2)


def charset_entropy_bits(text: str) -> float:
    """Upper-bound keyspace-style entropy: len * log2(charset).

    Charset is inferred from the characters actually used (lower/upper/
    digits/symbols/arabic/other-unicode). Useful as a password-strength
    style gauge next to the true Shannon value.
    """
    if not text:
        return 0.0
    pool = 0
    if any("a" <= c <= "z" for c in text):
        pool += 26
    if any("A" <= c <= "Z" for c in text):
        pool += 26
    if any(c.isdigit() for c in text):
        pool += 10
    if any(" " <= c <= "/" or ":" <= c <= "@" or "[" <= c <= "`" or "{" <= c <= "~" for c in text):
        pool += 32
    if any("\u0600" <= c <= "\u06ff" for c in text):
        pool += 40
    if any(ord(c) > 127 and not ("\u0600" <= c <= "\u06ff") for c in text):
        pool += 60
    if pool <= 1:
        return 0.0
    return round(len(text) * math.log2(pool), 2)


def _human_duration(seconds: float) -> dict:
    """Format a duration in seconds as a bilingual human string."""
    if seconds < 1:
        return {"ar": "أقل من ثانية", "en": "less than a second"}
    units_en = [("century", 3_155_760_000), ("year", 31_557_600), ("day", 86400),
                ("hour", 3600), ("minute", 60), ("second", 1)]
    units_ar = {"century": "قرن", "year": "سنة", "day": "يوم",
                "hour": "ساعة", "minute": "دقيقة", "second": "ثانية"}
    for name, size in units_en:
        if seconds >= size:
            v = seconds / size
            if v >= 1_000_000:
                return {"ar": f"≈ {v:,.0f} {units_ar[name]}", "en": f"≈ {v:,.0f} {name}s"}
            if v >= 100:
                return {"ar": f"≈ {v:,.0f} {units_ar[name]}", "en": f"≈ {v:,.0f} {name}s"}
            return {"ar": f"≈ {v:,.1f} {units_ar[name]}", "en": f"≈ {v:,.1f} {name}s"}
    return {"ar": "أقل من ثانية", "en": "less than a second"}


def crack_estimate(keyspace: int | None) -> dict | None:
    """Estimate brute-force time for ``keyspace`` at GUESSES_PER_SECOND.

    Returns ``None`` for unknown/huge-non-numeric keyspaces (e.g. "toy").
    """
    if not isinstance(keyspace, int) or keyspace <= 0:
        return None
    seconds = (keyspace / 2) / GUESSES_PER_SECOND  # average case
    return {
        "keyspace": keyspace,
        "guesses_per_second": GUESSES_PER_SECOND,
        "seconds_avg": seconds,
        "human": _human_duration(seconds),
    }


def avalanche_pct(hex_a: str, hex_b: str) -> float | None:
    """Fraction of differing bits between two hex digests (0..100)."""
    try:
        a = bytes.fromhex(hex_a)
        b = bytes.fromhex(hex_b)
    except (ValueError, TypeError):
        return None
    if len(a) != len(b) or not a:
        return None
    diff_bits = sum(bin(x ^ y).count("1") for x, y in zip(a, b))
    return round(diff_bits / (len(a) * 8) * 100, 2)


def flip_first_char(text: str) -> str:
    """Return ``text`` with the first character flipped by one bit.

    Used for the live avalanche demo: hash(text) vs hash(flipped).
    Empty text → "a" vs "b" fallback so the demo never breaks.
    """
    if not text:
        return "b"
    first = text[0]
    flipped = chr(ord(first) ^ 1)
    return flipped + text[1:]


def hash_hex(algo: str, data: bytes) -> str | None:
    """Hash ``data`` with a hashlib name, returning hex or None."""
    try:
        h = hashlib.new(algo, data)
    except (ValueError, TypeError):
        return None
    return h.hexdigest()


def collision_bound_years(digest_bits: int) -> dict:
    """Birthday-bound operations (≈2^(bits/2)) with a human label."""
    ops = 2 ** (digest_bits // 2)
    # At 1e10 hashes/s, years = ops / rate / seconds-per-year
    years = ops / GUESSES_PER_SECOND / 31_557_600
    return {"operations": f"2^{digest_bits // 2}", "human": _human_duration(years * 31_557_600)}

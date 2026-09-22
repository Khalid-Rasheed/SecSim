"""Birthday collision finder on truncated SHA-256 (live demo).

Hashes ``"<base>#<nonce>"`` with SHA-256, truncates the digest to
``collision_bits`` bits (default 20, max 24) and stores seen values
until two different inputs share one truncated digest — a REAL
collision, found by the actual birthday search, not staged.

The verdict compares the attempt count with the theoretical
``≈ 2^(n/2)`` birthday bound, making visible why a 256-bit digest
means 128-bit collision security (and why MD5/SHA-1 fell).

Safety: attempts are capped (fail-fast ValueError past the cap);
truncation is capped at 24 bits so the demo always finishes in
seconds. Full-size digests are untouched — this never "breaks" SHA-256.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"birthday_collision"``.
"""

import hashlib

from app.services.registry import register

COMPLEXITY = {
    "time": "O(2^(n/2))",
    "space": "O(2^(n/2))",
    "n": {"ar": "بتات الملخص المبتور", "en": "truncated digest bits"},
    "note": {
        "ar": "جذر تربيعي لا خطي: مضاعفة البتات تُربّع العمل — لهذا تحتاج الملخصات ضعف بتات مستوى الأمان",
        "en": "Square-root, not linear: doubling bits squares the work — why digests need twice the bits of their security level",
    },
}

DETAILS = {
    "overview": {
        "ar": "مفارقة عيد الميلاد applied: التصادم يصل احتمال 50% عند ~2^(n/2) محاولة لا 2^n. نُثبتها بإيجاد تصادم حقيقي على نسخة مبتورة من SHA-256 (20 بت افتراضياً) — ثم نُسقط النتيجة على الأحجام الحقيقية.",
        "en": "The birthday paradox applied: collisions hit 50% at ~2^(n/2) tries, not 2^n. We prove it by finding a REAL collision on truncated SHA-256 (20 bits by default) — then scale the lesson to real sizes.",
    },
    "history": {
        "ar": "المفارقة وُلدت في نظرية الاحتمالات (1930s) ودخلت التشفير مع هجمات عيد الميلاد على الهاش. SHAttered (2017) كان عملياً هجوم عيد ميلاد مُحسّناً ضد SHA-1 بكلفة ~2^63.",
        "en": "Born in probability theory (1930s), the paradox entered crypto as birthday attacks on hashes. SHAttered (2017) was effectively an optimized birthday attack on SHA-1 at ~2^63 cost.",
    },
    "how_it_works": {
        "ar": [
            "اختر n بت (20 افتراضياً، 24 كحد أقصى) — مساحة القيم 2^n.",
            "جرّب '<النص>#1' و'<النص>#2' ... واحسب SHA-256 لكل واحد مع بتر أول n بت.",
            "خزّن كل قيمة: أول تكرار = تصادم حقيقي بين دخلين مختلفين.",
            "قارن عدد المحاولات مع التوقع النظري 2^(n/2) — ثم تخيل n=256.",
        ],
        "en": [
            "Pick n bits (20 default, 24 max) — value space is 2^n.",
            "Try '<text>#1', '<text>#2', … hashing each with SHA-256 and truncating to n bits.",
            "Store every value: the first repeat is a REAL collision between different inputs.",
            "Compare attempts with the 2^(n/2) theory — then imagine n=256.",
        ],
    },
    "parameters": {
        "ar": [{"name": "collision_bits", "desc": "بتات البتر: 8..24 (الافتراضي 20 للسرعة)."}],
        "en": [{"name": "collision_bits", "desc": "Truncation bits: 8..24 (default 20 for speed)."}],
    },
    "security": {
        "ar": "الدرس المزدوج: (1) أي هاش n-بت يملك أمان تصادم 2^(n/2) فقط — لهذا MD5 (2^64) سقط عملياً وSHA-1 (2^80) لحقه. (2) SHA-256 الكامل (2^128) خارج كل قدرة حسابية — البتر هنا للعرض فقط.",
        "en": "The double lesson: (1) any n-bit hash has only 2^(n/2) collision security — why MD5 (2^64) fell in practice and SHA-1 (2^80) followed. (2) Full SHA-256 (2^128) is beyond all computing power — truncation here is display-only.",
    },
    "uses": {
        "ar": [
            "تجسيد مفارقة عيد الميلاد",
            "فهم سبب موت MD5 وSHA-1",
            "تقدير أحجام الملخصات الآمنة",
        ],
        "en": [
            "Making the birthday paradox tangible",
            "Understanding why MD5 and SHA-1 died",
            "Sizing safe digests",
        ],
    },
}

_DEFAULT_BITS = 20
_MAX_BITS = 24
_MIN_BITS = 8
# First attempts shown one-by-one as trace steps; the rest of the
# search runs silently (a 20-bit search needs ~1000 hashes — no one
# wants a 1000-step tape, and history rows stay small).
_TRACED_HASHES = 5


def _truncated(base: str, nonce: int, bits: int) -> tuple[str, int]:
    candidate = f"{base}#{nonce}"
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    return candidate, int(digest, 16) >> (256 - bits)


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    extra = extra or {}
    try:
        bits = int(extra.get("collision_bits", _DEFAULT_BITS))
    except (TypeError, ValueError):
        raise ValueError("collision_bits must be an integer")
    if not _MIN_BITS <= bits <= _MAX_BITS:
        raise ValueError(f"collision_bits must be within {_MIN_BITS}..{_MAX_BITS}")
    base = text or "secsim"
    space = 2 ** bits
    expected = 2 ** (bits // 2)

    steps = [
        {
            "index": 0,
            "title": {"ar": "إعداد البحث", "en": "Search setup"},
            "description": {
                "ar": f"بتر SHA-256 إلى {bits} بت: مساحة {space:,} قيمة — التوقع النظري ≈ {expected:,} محاولة (2^{bits // 2})",
                "en": f"Truncate SHA-256 to {bits} bits: {space:,} values — theory expects ≈ {expected:,} tries (2^{bits // 2})",
            },
            "snapshot": {"bits": bits, "space": space, "expected_tries": expected, "base": base},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    ]
    seen: dict[int, str] = {}
    attempts = 0
    cap = max(50 * expected, 1000)
    collision: tuple[str, str, int] | None = None
    nonce = 0
    while collision is None:
        nonce += 1
        attempts += 1
        if attempts > cap:
            raise ValueError("search exceeded safety cap — try fewer collision_bits")
        candidate, value = _truncated(base, nonce, bits)
        if value in seen:
            collision = (seen[value], candidate, value)
            break
        seen[value] = candidate
        if nonce <= _TRACED_HASHES:
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"تجربة {nonce}", "en": f"Try {nonce}"},
                    "description": {
                        "ar": f"'{candidate}' ← {value:0{bits}b} ({bits} بت) — جديد، يُخزَّن",
                        "en": f"'{candidate}' → {value:0{bits}b} ({bits} bits) — new, stored",
                    },
                    "snapshot": {"nonce": nonce, "candidate": candidate, "value": value},
                    "highlight": [nonce % 8],
                    "meta": {"phase": "search", "nonce": nonce},
                }
            )
    first, second, value = collision
    if attempts > _TRACED_HASHES + 1:
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"... {attempts - _TRACED_HASHES - 1} تجربة صامتة", "en": f"... {attempts - _TRACED_HASHES - 1} silent tries"},
                "description": {
                    "ar": "نفس التجزئة والتخزين لكل مرشح حتى أول تكرار",
                    "en": "Same hash-and-store per candidate until the first repeat",
                },
                "snapshot": {"silent_tries": attempts - _TRACED_HASHES - 1},
                "highlight": [],
                "meta": {"phase": "search"},
            }
        )
    ratio = round(attempts / expected, 2) if expected else 0
    result = f"{first} ⟷ {second}  (0x{value:0{(bits + 3) // 4}x})"
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "تصادم حقيقي!", "en": "Real collision!"},
            "description": {
                "ar": f"'{first}' و'{second}' يتشاركان القيمة بعد {attempts:,} محاولة (التوقع {expected:,} — النسبة {ratio})",
                "en": f"'{first}' and '{second}' share the value after {attempts:,} tries (theory {expected:,} — ratio {ratio})",
            },
            "snapshot": {"first": first, "second": second, "value": value,
                         "attempts": attempts, "expected": expected, "result": result},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return result, steps


def analyze(extra=None):
    return {
        "strengths": {
            "ar": ["البرهان عملي لا نظري: تصادم حقيقي محسوب أمامك", "النسبة للنظرية تُقاس لا تُحفظ"],
            "en": ["Practical not theoretical proof: a real computed collision", "The theory ratio is measured, not memorized"],
        },
        "weaknesses": {
            "ar": ["البتر للعرض فقط — SHA-256 الكامل (2^128) عصيّ على كل الحواسيب", "الذاكرة تنمو مع البحث (جدول القيم)"],
            "en": ["Truncation is display-only — full SHA-256 (2^128) defies all computers", "Memory grows with the search (value table)"],
        },
        "metrics": {"default_bits": _DEFAULT_BITS, "max_bits": _MAX_BITS},
        "complexity": COMPLEXITY,
    }


register(
    "birthday_collision",
    type="attack",
    family="attack",
    kind=None,
    security="educational",
    name={"ar": "تصادم عيد الميلاد", "en": "Birthday Collision"},
    description={
        "ar": "تصادم حقيقي على SHA-256 مبتور — إثبات حد 2^(n/2)",
        "en": "Real collision on truncated SHA-256 — the 2^(n/2) bound proven",
    },
    params=["collision_bits"],
    keyspace=None,
    order=63,
)

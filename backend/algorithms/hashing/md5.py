"""MD5 hashing with educational step trace. BROKEN — teaching/comparison only.

MD5 is cryptographically dead (practical collisions since 2004, abused
in the Flame attack in 2012). It exists in SecSim solely so learners
can hash the same input with MD5 and SHA-256 side by side and SEE that
a broken 128-bit digest looks just as "random" as a sound one — the
lesson being that output appearance says nothing about security.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"md5"`` at the bottom of this
file (see :mod:`app.services.registry`). Never use for passwords,
signatures or integrity that matters.
"""

import hashlib

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(1)",
    "n": {"ar": "عدد بايتات الدخل", "en": "number of input bytes"},
    "note": {
        "ar": "64 عملية ثابتة لكل كتلة وحالة ثابتة 128-بت — نفس تعقيد SHA-256 لكن بأمان مكسور",
        "en": "Fixed 64 ops per block with a fixed 128-bit state — same complexity as SHA-256 but broken security",
    },
}

DETAILS = {
    "overview": {
        "ar": "دالة تجزئة 128-بت كانت معيار التسعينيات: سريعة وبصمة قصيرة (32 خانة). اليوم مثال حي على أن السرعة والانتشار لا يعوّضان الكسر الرياضي — موجودة هنا للمقارنة والتعليم فقط.",
        "en": "A 128-bit hash that ruled the 1990s: fast with a short digest (32 hex chars). Today it is a living lesson that speed and ubiquity can't compensate mathematical breakage — kept here for comparison and teaching only.",
    },
    "history": {
        "ar": "صممها رون ريفست سنة 1991 خلفاً لـ MD4. بدأت الشقوق 1996، ثم زلزلها باحثون صينيون بقيادة وانغ شياوياو سنة 2004 بتصادمات عملية، وأجهز عليها استخدامها في هجوم Flame سنة 2012 بتزوير شهادات مايكروسوفت.",
        "en": "Designed by Ron Rivest in 1991 as MD4's successor. Cracks appeared in 1996, then Xiaoyun Wang's team shook it in 2004 with practical collisions, and the Flame attack finished it in 2012 by forging Microsoft certificates.",
    },
    "how_it_works": {
        "ar": [
            "حشو مشابه لـ SHA (مضاعفات 512-بت) مع حالة من 4 كلمات 32-بت فقط.",
            "64 عملية موزعة على 4 جولات بدوال (F وG وH وI) مع إزاحات وثوابت جيبية.",
            "تُجمَع النواتج على الحالة لتُنتج ملخص 128-بت.",
            "قِصَر الحالة (128-بت) يجعل التصادمات أسهل بكثير من SHA-256.",
        ],
        "en": [
            "SHA-like padding (512-bit multiples) but only four 32-bit state words.",
            "64 operations across 4 rounds with F, G, H, I functions, rotations and sine constants.",
            "Outputs accumulate into the state to yield the 128-bit digest.",
            "The short 128-bit state makes collisions far easier than SHA-256.",
        ],
    },
    "parameters": {
        "ar": [{"name": "input", "desc": "النص المراد تجزئته فقط."}],
        "en": [{"name": "input", "desc": "Just the text to hash."}],
    },
    "security": {
        "ar": "مكسورة عملياً: تُصنَع تصادمات متعمدة خلال ثوانٍ على حاسب عادي. ممنوعة للكلمات والتوقيعات والشهادات — استخدم SHA-256 على الأقل. بقاؤها المقبول الوحيد: فحص سلامة غير أمني لأنظمة قديمة.",
        "en": "Practically broken: engineered collisions in seconds on commodity hardware. Forbidden for passwords, signatures and certificates — use SHA-256 at minimum. Its only acceptable remnant: non-security checksums in legacy systems.",
    },
    "uses": {
        "ar": [
            "بصمات ملفات قديمة (غير أمنية)",
            "مقارنة تعليمية مع SHA-256 في هذه المنصة",
            "تحديد مكررات في أنظمة أرشيف قديمة",
        ],
        "en": [
            "Legacy file fingerprints (non-security)",
            "Teaching comparison with SHA-256 on this platform",
            "Duplicate detection in old archives",
        ],
    },
}


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    """Hash text with MD5 while tracing encode/pad/compress phases.

    Mirrors the SHA-256 trace shape step-for-step (``encode`` →
    ``padding`` → one ``compress`` step per 512-bit block → ``done``)
    so the two digests compare directly in the UI. Real hashing runs
    inside :mod:`hashlib`.

    Args:
        text: Text to hash (UTF-8 encoded first).
        key: Legacy positional slot for the uniform contract (ignored).
        mode: Accepted for the uniform contract (ignored — one-way).
        extra: Accepted for the uniform contract (ignored).

    Returns:
        Tuple ``(digest, steps)`` where ``digest`` is the 32-char
        lowercase hex string.

    Example:
        >>> simulate("Hello")[0]
        '8b1a9953c4611296a827abf8c47804d7'
    """
    data = (text or "").encode("utf-8")
    bit_len = len(data) * 8
    padded_len = ((len(data) + 9 + 63) // 64) * 64
    n_blocks = max(1, padded_len // 64)
    steps = [
        {
            "index": 0,
            "title": {"ar": "ترميز الدخل", "en": "Encode input"},
            "description": {
                "ar": f"تحويل '{text}' إلى UTF-8: {len(data)} بايت ({bit_len} بت)",
                "en": f"Encode '{text}' as UTF-8: {len(data)} bytes ({bit_len} bits)",
            },
            "snapshot": {"bytes": len(data), "bits": bit_len},
            "highlight": [],
            "meta": {"phase": "encode"},
        },
        {
            "index": 1,
            "title": {"ar": "الحشو (Padding)", "en": "Padding"},
            "description": {
                "ar": f"الطول بعد الحشو {padded_len} بايت = {n_blocks} كتلة (512 بت لكل كتلة)",
                "en": f"Padded length {padded_len} bytes = {n_blocks} block(s) of 512 bits",
            },
            "snapshot": {"padded_bytes": padded_len, "blocks": n_blocks},
            "highlight": [],
            "meta": {"phase": "padding"},
        },
    ]
    for b in range(n_blocks):
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"ضغط الكتلة {b + 1}", "en": f"Compress block {b + 1}"},
                "description": {
                    "ar": f"64 عملية على 4 جولات (F,G,H,I) فوق حالة 128-بت — الكتلة {b + 1}/{n_blocks}",
                    "en": f"64 operations over 4 rounds (F,G,H,I) on 128-bit state — block {b + 1}/{n_blocks}",
                },
                "snapshot": {"block": b + 1, "of": n_blocks, "rounds": 4, "ops": 64},
                "highlight": [b],
                "meta": {"phase": "compress", "block": b},
            }
        )
    digest = hashlib.md5(data).hexdigest()
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "الملخص النهائي", "en": "Final digest"},
            "description": {"ar": f"MD5('{text}') = {digest}", "en": f"MD5('{text}') = {digest}"},
            "snapshot": {"digest": digest, "bits": 128},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return digest, steps


def analyze(extra=None):
    """Return the static security review for MD5 (verdict: broken).

    Args:
        extra: Accepted for the uniform contract (ignored).

    Returns:
        ``{strengths{ar,en}, weaknesses{ar,en}, metrics{digest_bits:
        128, status: "broken"}, complexity}`` — the ``status`` flag
        lets the UI badge MD5 as broken wherever it appears.
    """
    return {
        "strengths": {
            "ar": ["سريع ومناسب للفحص غير الأمني (checksums)"],
            "en": ["Fast, fine for non-security checksums"],
        },
        "weaknesses": {
            "ar": [
                "مكسور عملياً: تصادمات متعمدة خلال ثوانٍ",
                "ممنوع للكلمات والتوقيعات — استخدم SHA-256 على الأقل",
            ],
            "en": [
                "Practically broken: engineered collisions in seconds",
                "Forbidden for passwords/signatures — use SHA-256+",
            ],
        },
        "metrics": {"digest_bits": 128, "status": "broken"},
        "complexity": COMPLEXITY,
    }


# Self-registration: makes "md5" visible to the dispatcher, the
# /api/algorithms catalog and the contract guard tests — no other file
# needs editing when this module changes.
register(
    "md5",
    type="hashing",
    family="hashing",
    kind="broken",
    security="broken",
    name={"ar": "MD5", "en": "MD5"},
    description={
        "ar": "دالة تجزئة مكسورة — للمقارنة والتعليم فقط",
        "en": "Broken hash — comparison and teaching only",
    },
    params=[],
    keyspace=None,
    order=40,
)

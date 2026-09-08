"""SHA-256 hashing with educational step trace (padding / blocks / digest).

Shows the pipeline honestly — UTF-8 encode → 512-bit padding → one
64-round compression step per block → 256-bit hex digest — while the
real compression runs inside :mod:`hashlib` (reimplementing SHA-256 by
hand would add risk, not teaching value).

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"sha256"`` at the bottom of this
file (see :mod:`app.services.registry`).
"""
import hashlib

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(1)",
    "n": {"ar": "عدد بايتات الدخل", "en": "number of input bytes"},
    "note": {
        "ar": "64 جولة ثابتة لكل كتلة وحالة ثابتة 256-بت — زمن خطي وذاكرة إضافية ثابتة",
        "en": "Fixed 64 rounds per block with a fixed 256-bit state — linear time, constant extra space",
    },
}

DETAILS = {
    "overview": {
        "ar": "دالة تجزئة تُحوّل أي دخل إلى بصمة ثابتة 256-بت (64 خانة ست عشرية). اتجاه واحد: سهلة الحساب ومستحيلة العكس عملياً، وأي تغيير طفيف في الدخل يقلب نصف البتات تقريباً (أثر الانهيار الجليدي).",
        "en": "A hash function mapping any input to a fixed 256-bit fingerprint (64 hex chars). One-way: cheap to compute, infeasible to invert, and any tiny input change flips about half the bits (avalanche effect).",
    },
    "history": {
        "ar": "من عائلة SHA-2 التي نشرتها NSA عبر NIST سنة 2001. ورثت العرش بعد تقادم SHA-1 (الذي كُسر عملياً سنة 2017 بهجوم SHAttered) وأصبحت معيار السلامة الرقمية.",
        "en": "Part of the SHA-2 family published by the NSA via NIST in 2001. It inherited the throne as SHA-1 aged out (practically broken in 2017 by SHAttered) and became the digital-integrity standard.",
    },
    "how_it_works": {
        "ar": [
            "يُرمَّز الدخل بـ UTF-8 ثم يُحشى ليصبح مضاعف 512-بت مع إلحاق الطول الأصلي.",
            "تُعالَج كل كتلة 512-بت عبر 64 جولة بدالة ضغط (بنية Davies-Meyer) فوق حالة من 8 كلمات 32-بت.",
            "تُستخدم ثوابت الجولات المشتقة من جذور الأعداد الأولية وقيم البدء القياسية.",
            "تُدمَج الحالة النهائية لتُنتج الملخص 256-بت بصيغة ست عشرية.",
        ],
        "en": [
            "Input is UTF-8 encoded, then padded to a multiple of 512 bits with the original length appended.",
            "Each 512-bit block runs 64 rounds of a compression function (Davies–Meyer structure) over eight 32-bit words.",
            "Round constants derived from prime roots and standard seed values are used.",
            "The final state is concatenated into the 256-bit hex digest.",
        ],
    },
    "parameters": {
        "ar": [{"name": "input", "desc": "النص المراد تجزئته فقط — لا مفاتيح ولا أوضاع."}],
        "en": [{"name": "input", "desc": "Just the text to hash — no keys or modes."}],
    },
    "security": {
        "ar": "مقاومة قوية للصورة المسبقة والتصادم حتى اليوم، لكن: لا تخزن بها كلمات المرور مباشرة (سريعة فيُجرَّب عليها؛ استخدم bcrypt/Argon2 مع ملح)، وانتبه لتمديد الطول عند تصميم البروتوكولات (استخدم HMAC).",
        "en": "Strong preimage and collision resistance to date, but: never store passwords with it directly (it's fast, so guessable — use bcrypt/Argon2 with salt), and mind length-extension in protocol design (use HMAC).",
    },
    "uses": {
        "ar": ["سلاسل الكتل (بتكوين)", "سلامة الملفات والتحميلات", "نظام git لتحديد الكائنات", "الرموز والتواقيع عبر HMAC"],
        "en": ["Blockchains (Bitcoin)", "File and download integrity", "Git object addressing", "Tokens and signatures via HMAC"],
    },
}


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    """Hash text with SHA-256 while tracing encode/pad/compress phases.

    Emits an ``encode`` step (byte/bit counts + hex preview), a
    ``padding`` step (the ``((len + 9 + 63) // 64) * 64`` length math:
    1 byte for the ``1``-bit, 8 bytes for the 64-bit length suffix),
    one ``compress`` step per 512-bit block, and the ``done`` digest —
    all in the unified SecSim step schema.

    Args:
        text: Text to hash (any language — UTF-8 encoded first).
        key: Legacy positional slot for the uniform contract (ignored —
            hashes take no key).
        mode: Accepted for the uniform contract (ignored — hashing is
            one-way, there is no decrypt mode).
        extra: Accepted for the uniform contract (ignored).

    Returns:
        Tuple ``(digest, steps)`` where ``digest`` is the 64-char
        lowercase hex string.

    Example:
        >>> simulate("Hello")[0]
        '185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969'
    """
    data = text.encode("utf-8")
    bit_len = len(data) * 8

    # SHA-256 padding explanation
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
            "snapshot": {"bytes": len(data), "bits": bit_len, "hex_preview": data[:32].hex()},
            "highlight": [],
            "meta": {"phase": "encode"},
        },
        {
            "index": 1,
            "title": {"ar": "الحشو (Padding)", "en": "Padding"},
            "description": {
                "ar": f"إضافة بت 1 ثم أصفار ثم الطول (64 بت) ليصبح الطول {padded_len} بايت = {n_blocks} كتلة (512 بت لكل كتلة)",
                "en": f"Append 1-bit, zeros, then 64-bit length → {padded_len} bytes = {n_blocks} block(s) of 512 bits",
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
                    "ar": f"تطبيق 64 جولة (دالة الضغط Davies-Meyer على الحالة 256-بت) للكتلة {b + 1}/{n_blocks}",
                    "en": f"Run 64 rounds (Davies-Meyer compression on 256-bit state) for block {b + 1}/{n_blocks}",
                },
                "snapshot": {"block": b + 1, "of": n_blocks, "rounds": 64},
                "highlight": [b],
                "meta": {"phase": "compress", "block": b},
            }
        )

    digest = hashlib.sha256(data).hexdigest()
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "الملخص النهائي", "en": "Final digest"},
            "description": {
                "ar": f"SHA-256('{text}') = {digest}",
                "en": f"SHA-256('{text}') = {digest}",
            },
            "snapshot": {"digest": digest, "bits": 256},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return digest, steps


def analyze(extra=None):
    """Return the static security review for SHA-256.

    Args:
        extra: Accepted for the uniform contract (ignored — the
            review does not depend on parameters).

    Returns:
        ``{strengths{ar,en}, weaknesses{ar,en}, metrics{digest_bits:
        256, rounds: 64}, complexity}`` — weaknesses stress that fast
        hashes must not store passwords directly (use bcrypt/Argon2).
    """
    return {
        "strengths": {
            "ar": ["مقاومة عالية للتصادم والصورة المسبقة", "معيار معتمد وواسع الاستخدام"],
            "en": ["Strong preimage/collision resistance", "Standardized, widely used"],
        },
        "weaknesses": {
            "ar": ["غير مناسب لتخزين كلمات المرور وحده (يحتاج salt + KDF مثل bcrypt)"],
            "en": ["Not enough alone for password storage (needs salt + KDF like bcrypt)"],
        },
        "metrics": {"digest_bits": 256, "rounds": 64},
        "complexity": COMPLEXITY,
    }


# Self-registration: makes "sha256" visible to the dispatcher, the
# /api/algorithms catalog and the contract guard tests — no other file
# needs editing when this module changes.
register(
    "sha256",
    type="hashing",
    name={"ar": "SHA-256", "en": "SHA-256"},
    description={
        "ar": "دالة تجزئة آمنة 256-بت",
        "en": "Secure 256-bit hash function",
    },
    params=[],
    keyspace=None,
    order=40,
)

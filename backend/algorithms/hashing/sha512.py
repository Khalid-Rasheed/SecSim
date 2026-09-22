"""SHA-512 hashing with educational step trace (padding / blocks / digest).

Same SHA-2 pipeline as SHA-256 (UTF-8 encode → 1024-bit padding → one
80-round compression step per block → 512-bit hex digest), real
compression inside :mod:`hashlib`. Included so learners can compare
digest sizes side by side: 128 (MD5) vs 160 (SHA-1) vs 256 (SHA-256)
vs 512 (SHA-512) — and see why the birthday bound doubles with bits.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"sha512"``.
"""

import hashlib

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(1)",
    "n": {"ar": "عدد بايتات الدخل", "en": "number of input bytes"},
    "note": {
        "ar": "80 جولة ثابتة لكل كتلة 1024-بت وحالة ثابتة 512-بت — زمن خطي وذاكرة إضافية ثابتة",
        "en": "Fixed 80 rounds per 1024-bit block with a fixed 512-bit state — linear time, constant extra space",
    },
}

DETAILS = {
    "overview": {
        "ar": "دالة تجزئة تُحوّل أي دخل إلى بصمة ثابتة 512-بت (128 خانة ست عشرية). الأخ الأكبر لـ SHA-256 بنفس العائلة: كتل أكبر (1024-بت) و80 جولة وحد عيد ميلاد 2^256 — الأقوى نظرياً في عائلة SHA-2.",
        "en": "A hash function mapping any input to a fixed 512-bit fingerprint (128 hex chars). SHA-256's bigger sibling in the same family: larger blocks (1024-bit), 80 rounds, and a 2^256 birthday bound — the theoretically strongest of SHA-2.",
    },
    "history": {
        "ar": "من عائلة SHA-2 (NIST سنة 2001) مع SHA-256. صُممت للأنظمة 64-بت (كلمات 64-بت) فتكون أسرع من SHA-256 على المعالجات الحديثة رغم الملخص الأطول، ولم يُرصد لها أي كسر عملي.",
        "en": "Part of the SHA-2 family (NIST 2001) alongside SHA-256. Designed for 64-bit systems (64-bit words), so it runs faster than SHA-256 on modern CPUs despite the longer digest; no practical break on record.",
    },
    "how_it_works": {
        "ar": [
            "يُرمَّز الدخل بـ UTF-8 ثم يُحشى ليصبح مضاعف 1024-بت مع إلحاق الطول (128 بت).",
            "تُعالَج كل كتلة 1024-بت عبر 80 جولة بدالة ضغط فوق حالة من 8 كلمات 64-بت.",
            "تُستخدم ثوابت الجولات وقيم البدء القياسية لعائلة SHA-2.",
            "تُدمَج الحالة النهائية لتُنتج الملخص 512-بت بصيغة ست عشرية.",
        ],
        "en": [
            "Input is UTF-8 encoded, then padded to a multiple of 1024 bits with the length appended (128 bits).",
            "Each 1024-bit block runs 80 rounds of a compression function over eight 64-bit words.",
            "Standard SHA-2 round constants and seed values are used.",
            "The final state is concatenated into the 512-bit hex digest.",
        ],
    },
    "parameters": {
        "ar": [{"name": "input", "desc": "النص المراد تجزئته فقط — لا مفاتيح ولا أوضاع."}],
        "en": [{"name": "input", "desc": "Just the text to hash — no keys or modes."}],
    },
    "security": {
        "ar": "مقاومة ممتازة للصورة المسبقة والتصادم (حد 2^256)، لكن نفس محاذير SHA-256: لا تخزن بها كلمات المرور مباشرة (استخدم Argon2/PBKDF2 مع ملح)، وانتبه لتمديد الطول (استخدم HMAC).",
        "en": "Excellent preimage and collision resistance (2^256 bound), but the same caveats as SHA-256: never store passwords in it directly (use Argon2/PBKDF2 with salt), and mind length-extension (use HMAC).",
    },
    "uses": {
        "ar": [
            "سلامة الملفات عالية الأمان",
            "الشهادات والتوقيعات طويلة الأمد",
            "مقارنة أحجام الملخصات تعليمياً",
            "اشتقاق المفاتيح عبر HMAC",
        ],
        "en": [
            "High-security file integrity",
            "Long-lived certificates and signatures",
            "Teaching digest-size comparison",
            "Key derivation via HMAC",
        ],
    },
}


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    data = text.encode("utf-8")
    bit_len = len(data) * 8

    # SHA-512 padding: 1 byte for the `1`-bit + 16 bytes for the 128-bit
    # length suffix, over 128-byte (1024-bit) blocks.
    padded_len = ((len(data) + 17 + 127) // 128) * 128
    n_blocks = max(1, padded_len // 128)

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
                "ar": f"إضافة بت 1 ثم أصفار ثم الطول (128 بت) ليصبح الطول {padded_len} بايت = {n_blocks} كتلة (1024 بت لكل كتلة)",
                "en": f"Append 1-bit, zeros, then 128-bit length → {padded_len} bytes = {n_blocks} block(s) of 1024 bits",
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
                    "ar": f"تطبيق 80 جولة فوق الحالة 512-بت (8 كلمات 64-بت) للكتلة {b + 1}/{n_blocks}",
                    "en": f"Run 80 rounds over the 512-bit state (eight 64-bit words) for block {b + 1}/{n_blocks}",
                },
                "snapshot": {"block": b + 1, "of": n_blocks, "rounds": 80},
                "highlight": [b],
                "meta": {"phase": "compress", "block": b},
            }
        )

    digest = hashlib.sha512(data).hexdigest()
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "الملخص النهائي", "en": "Final digest"},
            "description": {
                "ar": f"SHA-512('{text}') = {digest}",
                "en": f"SHA-512('{text}') = {digest}",
            },
            "snapshot": {"digest": digest, "bits": 512},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return digest, steps


def analyze(extra=None):
    return {
        "strengths": {
            "ar": ["أقوى حد عيد ميلاد في SHA-2 (2^256)", "أسرع من SHA-256 على معالجات 64-بت"],
            "en": ["Strongest SHA-2 birthday bound (2^256)", "Faster than SHA-256 on 64-bit CPUs"],
        },
        "weaknesses": {
            "ar": ["غير مناسب لتخزين كلمات المرور وحده (يحتاج salt + KDF مثل Argon2)"],
            "en": ["Not enough alone for password storage (needs salt + KDF like Argon2)"],
        },
        "metrics": {"digest_bits": 512, "rounds": 80},
        "complexity": COMPLEXITY,
    }


register(
    "sha512",
    type="hashing",
    family="hashing",
    kind="secure",
    security="secure",
    name={"ar": "SHA-512", "en": "SHA-512"},
    description={
        "ar": "دالة تجزئة آمنة 512-بت — الأقوى في SHA-2",
        "en": "Secure 512-bit hash function — strongest of SHA-2",
    },
    params=[],
    keyspace=None,
    order=45,
)

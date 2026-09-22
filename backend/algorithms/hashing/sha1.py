"""SHA-1 hashing (broken) with educational step trace.

Same Merkle–Damgård pipeline as MD5/SHA-256 (encode → pad → 80-step
compression per 512-bit block → 160-bit hex digest), real compression
inside :mod:`hashlib`. Included to teach WHY it retired: SHAttered
(2017) produced a practical collision, browsers/OSs removed it.

Contract: ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` / ``analyze()``,
self-registers as ``"sha1"``.
"""

import hashlib

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(1)",
    "n": {"ar": "عدد بايتات الدخل", "en": "number of input bytes"},
    "note": {
        "ar": "80 خطوة ثابتة لكل كتلة وحالة 160-بت — خطي بذاكرة ثابتة",
        "en": "Fixed 80 steps per block with 160-bit state — linear time, constant space",
    },
}

DETAILS = {
    "overview": {
        "ar": "دالة تجزئة 160-بت من عائلة SHA. كانت معيار السلامة والتوقيعات لعقدين، ثم سقطت: تصادم عملي موثق (SHAttered 2017) يعني أن مهاجماً يستطيع صناعة ملفين مختلفين بنفس البصمة.",
        "en": "A 160-bit SHA hash. The integrity/signature standard for two decades, then it fell: a practical collision (SHAttered 2017) means an attacker can craft two different files with the same digest.",
    },
    "history": {
        "ar": "نشرتها NSA عبر NIST سنة 1995. بدأت الشكوك 2005 (هجمات وانغ)، ثم جاء SHAttered (غوغل 2017: تصادم حقيقي بكلفة ~110 سنة-GPU) فأُسقطت من المتصفحات والشهادات.",
        "en": "Published by NSA via NIST in 1995. Doubts began 2005 (Wang's attacks), then SHAttered (Google 2017: a real collision at ~110 GPU-years) removed it from browsers and certificates.",
    },
    "how_it_works": {
        "ar": [
            "يُرمَّز الدخل UTF-8 ويُحشى لمضاعف 512-بت مع الطول.",
            "كل كتلة تمر بـ 80 خطوة فوق 5 كلمات 32-بت (160-بت).",
            "تُدمَج الحالة النهائية في ملخص 40 خانة ست عشرية.",
            "التصادم المثبت: ملفا PDF مختلفان بنفس بصمة SHA-1 (SHAttered).",
        ],
        "en": [
            "UTF-8 encode, pad to a 512-bit multiple with length.",
            "Each block runs 80 steps over five 32-bit words (160 bits).",
            "Final state concatenates into a 40-hex-char digest.",
            "The proven collision: two different PDFs sharing one SHA-1 (SHAttered).",
        ],
    },
    "parameters": {
        "ar": [{"name": "input", "desc": "النص المراد تجزئته فقط — لا مفاتيح."}],
        "en": [{"name": "input", "desc": "Just the text to hash — no keys."}],
    },
    "security": {
        "ar": "مكسور وممنوع للسلامة والتوقيعات والشهادات منذ 2017. يُقبل فقط للتحقق من ملفات قديمة أو HMAC غير تصادمي — والجديد كله SHA-256 على الأقل.",
        "en": "Broken and forbidden for integrity/signatures/certs since 2017. Only acceptable for verifying old files or non-collision HMAC — all new work needs SHA-256+.",
    },
    "uses": {
        "ar": ["درس في موت الخوارزميات", "التحقق من أرشيف قديم", "git تاريخياً (ينتقل لـ SHA-256)"],
        "en": ["Case study in algorithm death", "Verifying old archives", "Git historically (migrating to SHA-256)"],
    },
}


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    data = (text or "").encode("utf-8")
    padded_len = ((len(data) + 9 + 63) // 64) * 64
    n_blocks = max(1, padded_len // 64)
    steps = [
        {
            "index": 0,
            "title": {"ar": "ترميز الدخل", "en": "Encode input"},
            "description": {
                "ar": f"تحويل '{text}' إلى UTF-8: {len(data)} بايت",
                "en": f"Encode '{text}' as UTF-8: {len(data)} bytes",
            },
            "snapshot": {"bytes": len(data), "hex_preview": data[:32].hex()},
            "highlight": [],
            "meta": {"phase": "encode"},
        },
        {
            "index": 1,
            "title": {"ar": "الحشو (Padding)", "en": "Padding"},
            "description": {
                "ar": f"الحشو إلى {padded_len} بايت = {n_blocks} كتلة",
                "en": f"Padded to {padded_len} bytes = {n_blocks} block(s)",
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
                    "ar": f"80 خطوة فوق حالة 160-بت — الكتلة {b + 1}/{n_blocks}",
                    "en": f"80 steps over 160-bit state — block {b + 1}/{n_blocks}",
                },
                "snapshot": {"block": b + 1, "of": n_blocks, "steps": 80},
                "highlight": [b],
                "meta": {"phase": "compress", "block": b},
            }
        )
    digest = hashlib.sha1(data).hexdigest()
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "الملخص النهائي", "en": "Final digest"},
            "description": {"ar": f"SHA-1('{text}') = {digest}", "en": f"SHA-1('{text}') = {digest}"},
            "snapshot": {"digest": digest, "bits": 160},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return digest, steps


def analyze(extra=None):
    return {
        "strengths": {
            "ar": ["سريع — يصلح للفحص غير الأمني للأرشيف القديم"],
            "en": ["Fast — fine for non-security checks of old archives"],
        },
        "weaknesses": {
            "ar": [
                "تصادم عملي موثق (SHAttered 2017)",
                "ممنوع للشهادات والتوقيعات والسلامة منذ 2017",
                "160-بت تعني حد عيد ميلاد 2^80 فقط",
            ],
            "en": [
                "Practical documented collision (SHAttered 2017)",
                "Forbidden for certs/signatures/integrity since 2017",
                "160 bits means only a 2^80 birthday bound",
            ],
        },
        "metrics": {"digest_bits": 160, "status": "broken (SHAttered 2017)"},
        "complexity": COMPLEXITY,
    }


register(
    "sha1",
    type="hashing",
    family="hashing",
    kind="broken",
    security="broken",
    name={"ar": "SHA-1", "en": "SHA-1"},
    description={
        "ar": "تجزئة 160-بت مكسورة (SHAttered) — للتعليم فقط",
        "en": "Broken 160-bit hash (SHAttered) — teaching only",
    },
    params=[],
    keyspace=None,
    order=42,
)

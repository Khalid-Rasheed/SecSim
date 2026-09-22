"""SHA3-256 (Keccak) hashing with educational step trace.

Sponge construction (absorb → squeeze), unlike SHA-2's Merkle–Damgård —
NIST's insurance policy (2015): completely different internals, so a
breakthrough against SHA-2 is unlikely to affect SHA-3. Real squeezing
inside :mod:`hashlib` (``sha3_256``).

Contract: ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` / ``analyze()``,
self-registers as ``"sha3"``.
"""

import hashlib

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(1)",
    "n": {"ar": "عدد بايتات الدخل", "en": "number of input bytes"},
    "note": {
        "ar": "دالة إسفنج Keccak-f[1600] بجولات ثابتة — زمن خطي وحالة ثابتة",
        "en": "Keccak-f[1600] sponge with fixed rounds — linear time, fixed state",
    },
}

DETAILS = {
    "overview": {
        "ar": "SHA3-256: تجزئة 256-بت ببنية إسفنجية (امتصاص ثم عصر) لا سلسلة كتل. ليست بديلاً إلزامياً لـ SHA-256 بل بوليصة تأمين: داخلية مختلفة تماماً فلا يسقط الاثنان معاً.",
        "en": "SHA3-256: a 256-bit sponge hash (absorb then squeeze), not a block chain. Not a mandatory SHA-256 replacement but an insurance policy: totally different internals, so both won't fall together.",
    },
    "history": {
        "ar": "مسابقة NIST (2007-2012) فاز بها Keccak (بيرتين ورفاقه) واعتُمد معيار FIPS 202 سنة 2015. لم يُرصد له أي كسر عملي حتى اليوم.",
        "en": "NIST competition (2007–2012) won by Keccak (Bertoni et al.), standardized as FIPS 202 in 2015. No practical break to date.",
    },
    "how_it_works": {
        "ar": [
            "امتصاص: تُقطَّع الرسالة وتُخلط في حالة 1600-بت (معدل 1088 + سعة 512).",
            "تبديل Keccak-f بـ 24 جولة (θ, ρ, π, χ, ι).",
            "عصر: يُستخرج أول 256 بت كملخص (64 خانة).",
            "مقاوم لتمديد الطول بطبيعته — على عكس SHA-256 الخام.",
        ],
        "en": [
            "Absorb: message blocks mix into a 1600-bit state (rate 1088 + capacity 512).",
            "Keccak-f permutation, 24 rounds (θ, ρ, π, χ, ι).",
            "Squeeze: first 256 bits out as the digest (64 hex chars).",
            "Naturally length-extension resistant — unlike raw SHA-256.",
        ],
    },
    "parameters": {
        "ar": [{"name": "input", "desc": "النص المراد تجزئته فقط — لا مفاتيح."}],
        "en": [{"name": "input", "desc": "Just the text to hash — no keys."}],
    },
    "security": {
        "ar": "آمن ومقاوم لتمديد الطول. لا حاجة للهجرة من SHA-256 إليه — استخدم أياً منهما؛ المهم تجنب MD5 وSHA-1 وعدم تخزين كلمات المرور بتجزئة سريعة.",
        "en": "Secure and length-extension resistant. No need to migrate from SHA-256 — either is fine; what matters is avoiding MD5/SHA-1 and never storing passwords in a fast hash.",
    },
    "uses": {
        "ar": ["سلامة الملفات", "البلوك تشين الحديثة", "بديل احتياطي لـ SHA-2"],
        "en": ["File integrity", "Modern blockchains", "Backup to SHA-2"],
    },
}


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    data = (text or "").encode("utf-8")
    rate = 136  # 1088 bits for SHA3-256
    n_blocks = max(1, (len(data) + rate) // rate)
    steps = [
        {
            "index": 0,
            "title": {"ar": "الامتصاص", "en": "Absorb"},
            "description": {
                "ar": f"تقطيع '{text}' ({len(data)} بايت) إلى {n_blocks} مقطع بمعدل 1088-بت وخلطها في حالة 1600-بت",
                "en": f"Split '{text}' ({len(data)} bytes) into {n_blocks} 1088-bit chunks, mix into 1600-bit state",
            },
            "snapshot": {"bytes": len(data), "chunks": n_blocks, "rate_bits": 1088},
            "highlight": [],
            "meta": {"phase": "absorb"},
        },
        {
            "index": 1,
            "title": {"ar": "التبديل Keccak-f", "en": "Keccak-f permutation"},
            "description": {
                "ar": "24 جولة (θ ثم ρ ثم π ثم χ ثم ι) بعد كل مقطع",
                "en": "24 rounds (θ, ρ, π, χ, ι) after each chunk",
            },
            "snapshot": {"rounds": 24, "state_bits": 1600},
            "highlight": [],
            "meta": {"phase": "permute"},
        },
    ]
    digest = hashlib.sha3_256(data).hexdigest()
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "العصر والملخص", "en": "Squeeze digest"},
            "description": {"ar": f"SHA3-256('{text}') = {digest}", "en": f"SHA3-256('{text}') = {digest}"},
            "snapshot": {"digest": digest, "bits": 256},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return digest, steps


def analyze(extra=None):
    return {
        "strengths": {
            "ar": ["مقاوم لتمديد الطول بطبيعته", "داخلية مختلفة عن SHA-2 (تنويع المخاطر)"],
            "en": ["Naturally length-extension resistant", "Different internals from SHA-2 (risk diversification)"],
        },
        "weaknesses": {
            "ar": ["دعم مكتبات أقل انتشاراً من SHA-256", "غير مناسب لكلمات المرور وحده (سريع)"],
            "en": ["Less ubiquitous library support than SHA-256", "Not enough alone for passwords (fast)"],
        },
        "metrics": {"digest_bits": 256, "rounds": 24, "state_bits": 1600},
        "complexity": COMPLEXITY,
    }


register(
    "sha3",
    type="hashing",
    family="hashing",
    kind="secure",
    security="secure",
    name={"ar": "SHA3-256", "en": "SHA3-256"},
    description={
        "ar": "تجزئة إسفنجية آمنة 256-بت (Keccak)",
        "en": "Secure 256-bit sponge hash (Keccak)",
    },
    params=[],
    keyspace=None,
    order=46,
)

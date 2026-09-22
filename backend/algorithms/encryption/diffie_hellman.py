"""Diffie-Hellman key exchange (educational, small numbers).

Alice and Bob agree on public (p, g), pick secrets (a, b), exchange
A = g^a mod p and B = g^b mod p, and both derive s = g^(ab) mod p.

Teaching only: tiny primes are trivially breakable via discrete log.
Unauthenticated DH is vulnerable to man-in-the-middle (Eve substitutes
her own values) — the simulator shows the math; the MITM lesson lives
in DETAILS/security + the attack lab.

simulate(): ``text`` is ignored (key exchange needs no message);
parameters come from ``extra`` (dh_p, dh_g, dh_a, dh_b). Result is the
shared secret as a decimal string.
"""

from app.services.registry import register

COMPLEXITY = {
    "time": "O(log p)",
    "space": "O(1)",
    "n": {"ar": "حجم المعامل p بالبت", "en": "modulus size in bits"},
    "note": {
        "ar": "أسّ modularي واحد لكل طرف (~log p ضربات) — رخيص هنا، وثقيل بمفاتيح حقيقية 2048+ بت",
        "en": "One modular exponentiation per party (~log p multiplications) — cheap here, heavy at real 2048+ bits",
    },
}

DETAILS = {
    "overview": {
        "ar": "بروتوكول ديفي-هيلمان (1976): يتفق طرفان على سر مشترك عبر قناة علنية دون تبادل مسبق. كل منهما ينشر قيمة عامة ويحتفظ بسره، والمعجزة الرياضية أن الطرفين يصلان لنفس السر.",
        "en": "Diffie–Hellman (1976): two parties agree on a shared secret over a public channel with no prior secret. Each publishes a value and keeps a secret; the mathematical miracle is both land on the same secret.",
    },
    "history": {
        "ar": "أول نظام بالمفتاح العام (ديفي وهيلمان 1976) — فتح عصر التشفير الحديث ومهد لـ RSA. الأعداد هنا صغيرة للعرض؛ الواقع يستخدم 2048+ بت أو منحنيات إهليجية.",
        "en": "The first public-key system (Diffie & Hellman 1976) — opened modern cryptography and paved the way for RSA. Numbers here are tiny for display; reality uses 2048+ bits or elliptic curves.",
    },
    "how_it_works": {
        "ar": [
            "اتفقا علناً على p (أولي) و g (مولد).",
            "تختار Alice سر a وتحسب A = g^a mod p؛ وBob سر b ويحسب B = g^b mod p.",
            "يتبادلا A و B علناً.",
            "تحسب Alice السر s = B^a mod p ويحسب Bob السر s = A^b mod p — متساويان رياضياً.",
            "استخدما s (بعد اشتقاق) مفتاح جلسة لـ AES.",
        ],
        "en": [
            "Publicly agree on p (prime) and g (generator).",
            "Alice picks secret a, computes A = g^a mod p; Bob picks b, computes B = g^b mod p.",
            "They exchange A and B openly.",
            "Alice computes s = B^a mod p, Bob computes s = A^b mod p — mathematically equal.",
            "Derive an AES session key from s.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "dh_p", "desc": "المعامل الأولي (الافتراضي 23 للعرض)."},
            {"name": "dh_g", "desc": "المولد (الافتراضي 5)."},
            {"name": "dh_a", "desc": "سر Alice (الافتراضي 6)."},
            {"name": "dh_b", "desc": "سر Bob (الافتراضي 15)."},
        ],
        "en": [
            {"name": "dh_p", "desc": "Prime modulus (default 23 for display)."},
            {"name": "dh_g", "desc": "Generator (default 5)."},
            {"name": "dh_a", "desc": "Alice's secret (default 6)."},
            {"name": "dh_b", "desc": "Bob's secret (default 15)."},
        ],
    },
    "security": {
        "ar": "الأمان مبني على صعوبة اللوغاريتم المنفصل — لكن هذه الأعداد الصغيرة تُكسر ذهنياً. الأخطر: DH دون مصادقة عُرضة لرجل-في-الوسط (Eve تستبدل القيم). الواقع: 2048+ بت + مصادقة + اشتقاق (HKDF) ثم AES.",
        "en": "Security rests on discrete-log hardness — but these tiny numbers break mentally. Worse: unauthenticated DH falls to man-in-the-middle (Eve substitutes values). Reality: 2048+ bits + authentication + KDF (HKDF), then AES.",
    },
    "uses": {
        "ar": ["تبادل مفاتيح TLS", "إشارة Signal", "أساس بروتوكولات الجلسات"],
        "en": ["TLS key exchange", "Signal protocol", "Basis of session protocols"],
    },
}


def _params(extra: dict):
    extra = extra or {}
    try:
        p = int(extra.get("dh_p", 23))
        g = int(extra.get("dh_g", 5))
        a = int(extra.get("dh_a", 6))
        b = int(extra.get("dh_b", 15))
    except (TypeError, ValueError):
        raise ValueError("dh_p, dh_g, dh_a, dh_b must be integers")
    if p < 5:
        raise ValueError("dh_p must be a prime ≥ 5 (try 23)")
    if not (1 <= g < p):
        raise ValueError("dh_g must satisfy 1 ≤ g < p")
    if a < 1 or b < 1:
        raise ValueError("secrets dh_a and dh_b must be ≥ 1")
    return p, g, a, b


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    p, g, a, b = _params(extra or {})
    A = pow(g, a, p)
    B = pow(g, b, p)
    s_alice = pow(B, a, p)
    s_bob = pow(A, b, p)
    assert s_alice == s_bob
    s = s_alice
    steps = [
        {
            "index": 0,
            "title": {"ar": "اتفاق علني", "en": "Public agreement"},
            "description": {
                "ar": f"المعامل p={p} والمولد g={g} — علنيان ويُرسلان مكشوفين",
                "en": f"Modulus p={p}, generator g={g} — public, sent in the clear",
            },
            "snapshot": {"p": p, "g": g},
            "highlight": [],
            "meta": {"phase": "setup"},
        },
        {
            "index": 1,
            "title": {"ar": "أسرار خاصة", "en": "Private secrets"},
            "description": {
                "ar": f"Alice تختار a={a} (سري) وBob يختار b={b} (سري) — لا يُرسلان أبداً",
                "en": f"Alice picks a={a} (secret), Bob picks b={b} (secret) — never sent",
            },
            "snapshot": {"a": a, "b": b},
            "highlight": [],
            "meta": {"phase": "secrets"},
        },
        {
            "index": 2,
            "title": {"ar": "القيم العامة", "en": "Public values"},
            "description": {
                "ar": f"A = g^a mod p = {g}^{a} mod {p} = {A} | B = g^b mod p = {g}^{b} mod {p} = {B} — يُتبادلان علناً",
                "en": f"A = g^a mod p = {g}^{a} mod {p} = {A} | B = g^b mod p = {g}^{b} mod {p} = {B} — exchanged openly",
            },
            "snapshot": {"A": A, "B": B},
            "highlight": [],
            "meta": {"phase": "exchange"},
        },
        {
            "index": 3,
            "title": {"ar": "السر المشترك", "en": "Shared secret"},
            "description": {
                "ar": f"Alice: s = B^a mod p = {B}^{a} mod {p} = {s} | Bob: s = A^b mod p = {A}^{b} mod {p} = {s} — متطابقان!",
                "en": f"Alice: s = B^a mod p = {B}^{a} mod {p} = {s} | Bob: s = A^b mod p = {A}^{b} mod {p} = {s} — match!",
            },
            "snapshot": {"shared_secret": s, "result": str(s)},
            "highlight": [],
            "meta": {"phase": "done"},
        },
    ]
    return str(s), steps


def analyze(extra=None):
    p, _, _, _ = _params({**(extra or {}), "dh_a": (extra or {}).get("dh_a", 6),
                          "dh_b": (extra or {}).get("dh_b", 15)})
    bits = p.bit_length()
    return {
        "strengths": {
            "ar": ["لا حاجة لقناة سرية مسبقة", "أساس كل تبادل مفاتيح حديث"],
            "en": ["No pre-shared secret needed", "Basis of all modern key exchange"],
        },
        "weaknesses": {
            "ar": [
                f"هذا المعامل ({bits} بت) يُكسر فوراً باللوغاريتم المنفصل",
                "دون مصادقة: عُرضة لرجل-في-الوسط",
                "السر الخام ليس مفتاحاً — يحتاج اشتقاق HKDF",
            ],
            "en": [
                f"This modulus ({bits} bits) breaks instantly via discrete log",
                "Without authentication: MITM-vulnerable",
                "Raw secret is not a key — needs HKDF derivation",
            ],
        },
        "metrics": {"p_bits": bits, "real_world_min_bits": 2048},
        "complexity": COMPLEXITY,
    }


register(
    "diffie_hellman",
    type="encryption",
    family="asymmetric",
    kind="discrete",
    security="educational",
    name={"ar": "ديفي-هيلمان", "en": "Diffie-Hellman"},
    description={
        "ar": "تبادل مفاتيح بلوغاريتم منفصل — أعداد صغيرة للتعليم",
        "en": "Discrete-log key exchange — tiny teaching numbers",
    },
    params=["dh_p", "dh_g", "dh_a", "dh_b"],
    keyspace="toy",
    order=32,
)

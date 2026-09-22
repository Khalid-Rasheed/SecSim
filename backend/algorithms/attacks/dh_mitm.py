"""Man-in-the-middle on unauthenticated Diffie-Hellman (Eve's demo).

Eve sits on the channel: she swaps Alice's and Bob's public values for
her own (E = g^e to Alice, F = g^f to Bob), so Alice derives s1 with
Eve and Bob derives a DIFFERENT s2 with Eve. Eve holds both and reads
everything. The demo encrypts Alice's message with a toy XOR under s1
so Eve's decryption visibly succeeds while Bob's visibly garbles.

Params (all ints): dh_p, dh_g, dh_a, dh_b (the honest parties) plus
mitm_e, mitm_f (Eve's secrets toward Alice and Bob). ``text`` is the
message Alice sends. Result is Eve's recovered plaintext.

Teaching only — the fix (authenticated DH: signatures/certs) is the
moral of DETAILS/security.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"dh_mitm"``.
"""

from app.services.registry import register

COMPLEXITY = {
    "time": "O(log p)",
    "space": "O(1)",
    "n": {"ar": "حجم المعامل p بالبت", "en": "modulus size in bits"},
    "note": {
        "ar": "بضع عمليات أسّ modularية فقط — الهجوم رخيص لأن القناة غير موثقة لا لأن الرياضيات ضعيفة",
        "en": "Just a few modular exponentiations — the attack is cheap because the channel is unauthenticated, not because the math is weak",
    },
}

DETAILS = {
    "overview": {
        "ar": "رجل-في-الوسط على ديفي-هيلمان: المهاجمة Eve لا تكسر الرياضيات بل تستبدل القيم العامة أثناء transit. يتفق كل طرف على سر معها هي (سرّان مختلفان!) فتقرأ كل شيء وتُمرر ما تشاء.",
        "en": "Man-in-the-middle on Diffie–Hellman: Eve never breaks the math — she substitutes the public values in transit. Each party agrees on a secret with HER (two different secrets!) so she reads everything and forwards what she likes.",
    },
    "history": {
        "ar": "حذر ديفي وهيلمان أنفسهما من غياب المصادقة منذ ورقة 1976. كل بروتوكولات TLS الحديثة تضيف توقيعات وشهادات لهذا السبب بالذات — الدرس مطبّق في كل اتصال HTTPS.",
        "en": "Diffie and Hellman themselves warned about missing authentication in their 1976 paper. Every modern TLS protocol adds signatures and certificates for exactly this reason — the lesson runs inside each HTTPS connection.",
    },
    "how_it_works": {
        "ar": [
            "يتبادل Alice وBob قيمهما A وB — فتعترضهما Eve وتستبدلهما بقيمها E وF.",
            "تحسب Alice السر s1 مع Eve (ظانةً أنه مع Bob)، ويحسب Bob السر s2 مع Eve — مختلفان!",
            "تحسب Eve السرّين معاً (تعرف e وf) فتملك مفاتيح الطرفين.",
            "تشفر Alice رسالتها بـ s1؛ تفكها Eve بنسختها من s1، بينما يفشل Bob (معه s2) — والدليل مرئي.",
        ],
        "en": [
            "Alice and Bob exchange A and B — Eve intercepts and substitutes her own E and F.",
            "Alice derives secret s1 with Eve (thinking it is Bob); Bob derives a DIFFERENT s2 with Eve.",
            "Eve computes both secrets (she knows e and f) — holding both parties' keys.",
            "Alice encrypts her message under s1; Eve decrypts with her copy of s1 while Bob (holding s2) fails — visibly proven.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "dh_p و dh_g و dh_a و dh_b", "desc": "معاملات الطرفين الشرعيين (مثل تبادل DH)."},
            {"name": "mitm_e و mitm_f", "desc": "سرّا Eve تجاه Alice وBob (الافتراضي 3 و7)."},
        ],
        "en": [
            {"name": "dh_p & dh_g & dh_a & dh_b", "desc": "The honest parties' parameters (like a DH exchange)."},
            {"name": "mitm_e & mitm_f", "desc": "Eve's secrets toward Alice and Bob (defaults 3 and 7)."},
        ],
    },
    "security": {
        "ar": "الهجوم ينجح دائماً ضد DH غير الموثق — مهما كبرت المفاتيح. العلاج الوحيد: مصادقة القيم العامة (توقيعات رقمية وشهادات كما في TLS). السرية الأمامية لا تنفع هنا لأن Eve حاضرة لحظة التبادل.",
        "en": "The attack always succeeds against unauthenticated DH — no matter the key size. The only cure: authenticating the public values (signatures and certificates as in TLS). Forward secrecy does not help here because Eve is present at exchange time.",
    },
    "uses": {
        "ar": [
            "فهم سبب شهادات TLS",
            "عروض أمن الشبكات",
            "التفريق بين السرية والمصادقة",
        ],
        "en": [
            "Understanding why TLS certificates exist",
            "Network-security demonstrations",
            "Distinguishing confidentiality from authentication",
        ],
    },
}


def _int(extra: dict, name: str, default: int) -> int:
    try:
        return int(extra.get(name, default))
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be an integer")


def _xor(data: bytes, key_byte: int) -> bytes:
    return bytes(b ^ key_byte for b in data)


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    extra = extra or {}
    p = _int(extra, "dh_p", 23)
    g = _int(extra, "dh_g", 5)
    a = _int(extra, "dh_a", 6)
    b = _int(extra, "dh_b", 15)
    e = _int(extra, "mitm_e", 3)
    f = _int(extra, "mitm_f", 7)
    if p < 5:
        raise ValueError("dh_p must be a prime ≥ 5 (try 23)")
    for name, v in (("dh_g", g),):
        if not (1 <= v < p):
            raise ValueError(f"{name} must satisfy 1 ≤ {name} < p")
    for name, v in (("dh_a", a), ("dh_b", b), ("mitm_e", e), ("mitm_f", f)):
        if v < 1:
            raise ValueError(f"{name} must be ≥ 1")

    message = text or ""
    A, B = pow(g, a, p), pow(g, b, p)   # honest values (never arrive)
    E, F = pow(g, e, p), pow(g, f, p)   # Eve's substitutes
    s_alice = pow(E, a, p)              # Alice thinks: shared with Bob
    s_bob = pow(F, b, p)                # Bob thinks: shared with Alice
    s_eve_a = pow(A, e, p)              # Eve's copy of s_alice
    s_eve_b = pow(B, f, p)              # Eve's copy of s_bob

    steps = [
        {
            "index": 0,
            "title": {"ar": "التبادل الشرعي (قبل الاعتراض)", "en": "Honest exchange (pre-intercept)"},
            "description": {
                "ar": f"A = g^a = {A} وB = g^b = {B} — لن يصلا أبداً",
                "en": f"A = g^a = {A} and B = g^b = {B} — they will never arrive",
            },
            "snapshot": {"A": A, "B": B, "p": p, "g": g},
            "highlight": [],
            "meta": {"phase": "setup"},
        },
        {
            "index": 1,
            "title": {"ar": "Eve تستبدل القيم", "en": "Eve substitutes values"},
            "description": {
                "ar": f"تُرسل Eve قيمها: E = g^e = {E} إلى Alice وF = g^f = {F} إلى Bob",
                "en": f"Eve sends her own: E = g^e = {E} to Alice and F = g^f = {F} to Bob",
            },
            "snapshot": {"E": E, "F": F, "mitm_e": e, "mitm_f": f},
            "highlight": [],
            "meta": {"phase": "intercept"},
        },
        {
            "index": 2,
            "title": {"ar": "سرّان مختلفان!", "en": "Two different secrets!"},
            "description": {
                "ar": f"Alice تشتق s1 = E^a = {s_alice} | Bob يشتق s2 = F^b = {s_bob} — غير متساويين!",
                "en": f"Alice derives s1 = E^a = {s_alice} | Bob derives s2 = F^b = {s_bob} — NOT equal!",
            },
            "snapshot": {"s_alice": s_alice, "s_bob": s_bob, "match": s_alice == s_bob},
            "highlight": [],
            "meta": {"phase": "secrets"},
        },
        {
            "index": 3,
            "title": {"ar": "Eve تملك السرّين", "en": "Eve holds both secrets"},
            "description": {
                "ar": f"Eve تحسب s1 = A^e = {s_eve_a} (مطابق!) وs2 = B^f = {s_eve_b} (مطابق!)",
                "en": f"Eve computes s1 = A^e = {s_eve_a} (match!) and s2 = B^f = {s_eve_b} (match!)",
            },
            "snapshot": {"eve_s1": s_eve_a, "eve_s2": s_eve_b,
                         "s1_match": s_eve_a == s_alice, "s2_match": s_eve_b == s_bob},
            "highlight": [],
            "meta": {"phase": "eve"},
        },
    ]

    # Toy encryption of Alice's message under s1; Eve reads it, Bob garbles.
    data = message.encode("utf-8")
    cipher = _xor(data, s_alice % 256)
    eve_plain = _xor(cipher, s_eve_a % 256).decode("utf-8")  # == message, Eve holds s1
    bob_try = _xor(cipher, s_bob % 256)
    try:
        bob_plain = bob_try.decode("utf-8")
        bob_ok = bob_plain == message
    except UnicodeDecodeError:
        bob_plain = bob_try.hex()
        bob_ok = False
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "قراءة Eve مقابل فشل Bob", "en": "Eve reads it, Bob fails"},
            "description": {
                "ar": f"رسالة Alice '{message}' ← Eve تقرأ '{eve_plain}' (ناجحة) | Bob يرى '{bob_plain[:32]}' ({'مطابق!' if bob_ok else 'مخرب — الدليل'})",
                "en": f"Alice's '{message}' → Eve reads '{eve_plain}' (success) | Bob sees '{bob_plain[:32]}' ({'match!' if bob_ok else 'garbled — proof'})",
            },
            "snapshot": {"cipher_hex": cipher.hex(), "eve_plaintext": eve_plain,
                         "bob_plaintext": bob_plain, "eve_success": eve_plain == message,
                         "result": eve_plain},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return eve_plain, steps


def analyze(extra=None):
    return {
        "strengths": {
            "ar": ["ينجح دائماً ضد أي DH غير موثق — مهما كبرت المفاتيح", "لا يحتاج كسر أي رياضيات"],
            "en": ["Always succeeds against any unauthenticated DH — regardless of key size", "Needs no math-breaking at all"],
        },
        "weaknesses": {
            "ar": ["يفشل فوراً مع مصادقة القيم (توقيعات/شهادات)", "يتطلب مهاجماً نشطاً على القناة لحظة التبادل"],
            "en": ["Fails instantly with value authentication (signatures/certs)", "Needs an active on-path attacker at exchange time"],
        },
        "metrics": {"needs_authentication": True, "breaks_math": False},
        "complexity": COMPLEXITY,
    }


register(
    "dh_mitm",
    type="attack",
    family="attack",
    kind=None,
    security="educational",
    name={"ar": "رجل-في-الوسط على DH", "en": "DH Man-in-the-Middle"},
    description={
        "ar": "Eve تستبدل قيم DH وتقرأ كل شيء — درس المصادقة",
        "en": "Eve swaps DH values and reads everything — the authentication lesson",
    },
    params=["dh_p", "dh_g", "dh_a", "dh_b", "mitm_e", "mitm_f"],
    keyspace=None,
    order=62,
)

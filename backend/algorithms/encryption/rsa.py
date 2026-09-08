"""RSA with small educational primes (default p=61, q=53 per PRD).

Encrypts character-by-character: c = m^e mod n. Teaching only —
tiny keys are trivially factorable. Plaintext chars must satisfy m < n.

Wire format: encrypt returns space-separated integers (e.g. ``"3000
3179"`` for ``"Hi"``) and decrypt takes that same string back
(commas are also accepted as separators).

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"rsa"`` at the bottom of this
file (see :mod:`app.services.registry`).
"""

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n · log e)",
    "space": "O(n)",
    "n": {"ar": "عدد أحرف الرسالة", "en": "number of message characters"},
    "note": {
        "ar": "كل حرف يكلف أسّاً modularياً (~log e ضربات) — أثقل بكثير من التشفير المتماثل لكل حرف",
        "en": "Each character costs one modular exponentiation (~log e multiplications) — far heavier per char than symmetric ciphers",
    },
}

DETAILS = {
    "overview": {
        "ar": "أشهر تشفير بالمفتاح العام: مفتاح عام (e, n) يشفر به الجميع، ومفتاح خاص (d, n) يفك به مالكه فقط. الأمان مبني على صعوبة تحليل جداء عددين أوليين كبيرين إلى عوامله.",
        "en": "The most famous public-key cipher: a public key (e, n) anyone can encrypt with, and a private key (d, n) only its owner decrypts with. Security rests on the hardness of factoring the product of two large primes.",
    },
    "history": {
        "ar": "نُشر سنة 1977 بأسماء ريفست وشامير وأدلمان في MIT بعد فكرة ديفي-هيلمان (1976). لاحقاً تبيّن أن كليفورد كوكس في المخابرات البريطانية اكتشفه سراً سنة 1973. مثال المنصة (p=61 وq=53) هو المثال التعليمي الأشهر عالمياً.",
        "en": "Published in 1977 by Rivest, Shamir and Adleman at MIT, following the Diffie–Hellman idea (1976). Clifford Cocks of GCHQ had secretly discovered it in 1973. This platform's example (p=61, q=53) is the world's most famous teaching example.",
    },
    "how_it_works": {
        "ar": [
            "اختر عددين أوليين p وq واحسب n = p×q و φ(n) = (p−1)(q−1).",
            "اختر الأس العام e (أولي نسبياً مع φ) واحسب الخاص d = e⁻¹ mod φ.",
            "التشفير: لكل رمز m احسب c = m^e mod n.",
            "الفك: لكل قيمة c احسب m = c^d mod n ثم أعد الرموز.",
            "انشر (e, n) واحتفظ بـ d سراً.",
        ],
        "en": [
            "Pick primes p and q; compute n = p×q and φ(n) = (p−1)(q−1).",
            "Choose public exponent e (coprime to φ) and compute private d = e⁻¹ mod φ.",
            "Encrypt: for each code m compute c = m^e mod n.",
            "Decrypt: for each c compute m = c^d mod n, then restore symbols.",
            "Publish (e, n); keep d secret.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "p و q", "desc": "عددان أوليان (الافتراضي 61 و53 ← n=3233 للتعليم فقط)."},
            {"name": "e", "desc": "الأس العام (الافتراضي 17 ويجب أن يكون أولياً نسبياً مع φ)."},
            {"name": "mode", "desc": "encrypt لنص عادي أو decrypt لقيم مفصولة بمسافات."},
        ],
        "en": [
            {"name": "p & q", "desc": "Two primes (default 61 and 53 → n=3233, teaching only)."},
            {"name": "e", "desc": "Public exponent (default 17, must be coprime to φ)."},
            {"name": "mode", "desc": "encrypt for plaintext or decrypt for space-separated values."},
        ],
    },
    "security": {
        "ar": "مفاتيح اللعب هنا (12 بت) تُحلَّل ذهنياً تقريباً. الواقع يتطلب 2048+ بت وحشو OAEP (التشفير الخام يسرب التكرار كما ترى في المحاكاة) وحماية من هجمات التوقيت. الحوسبة الكمومية (خوارزمية شور) تهدده نظرياً مستقبلاً.",
        "en": "These toy keys (12 bits) factor almost mentally. Reality needs 2048+ bits and OAEP padding (raw encryption leaks frequency, as the simulator shows) plus timing-attack defenses. Quantum computing (Shor's algorithm) threatens it in theory long-term.",
    },
    "uses": {
        "ar": ["تبادل مفاتيح الجلسات", "التوقيعات الرقمية والشهادات", "البريد المشفر", "المصادقة في البطاقات الذكية"],
        "en": ["Session-key exchange", "Digital signatures and certificates", "Encrypted email", "Smart-card authentication"],
    },
}


def _egcd(a: int, b: int):
    """Extended Euclidean algorithm: gcd plus Bézout coefficients.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        Tuple ``(g, x, y)`` with ``g = gcd(a, b)`` and ``a*x + b*y = g``.

    Example:
        >>> _egcd(17, 3120)
        (1, -367, 2)
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def _modinv(a: int, m: int) -> int:
    """Modular inverse of ``a`` modulo ``m`` (derives the private key).

    Args:
        a: Public exponent ``e``.
        m: ``phi(n) = (p-1)(q-1)``.

    Raises:
        ValueError: If ``e`` is not coprime to ``phi(n)`` (then no
            private exponent exists and the key pair is invalid).

    Returns:
        ``d`` with ``e*d ≡ 1 (mod phi)``, normalised to ``0..m-1``.

    Example:
        >>> _modinv(17, 3120)  # classic p=61, q=53 pair
        2753
    """
    g, x, _ = _egcd(a, m)
    if g != 1:
        raise ValueError("e must be coprime to φ(n)")
    return x % m


def _keygen(p: int, q: int, e: int):
    """Derive the RSA key pair from primes and a public exponent.

    Computes ``n = p*q``, ``phi = (p-1)(q-1)`` and the private
    exponent ``d = e⁻¹ mod phi``. Primality of ``p``/``q`` is NOT
    checked (teaching demo — callers pass known primes).

    Args:
        p: First prime (default 61).
        q: Second prime (default 53).
        e: Public exponent, coprime to ``phi`` (default 17).

    Raises:
        ValueError: Propagated from :func:`_modinv` for a bad ``e``.

    Returns:
        Tuple ``(n, phi, d)``.

    Example:
        >>> _keygen(61, 53, 17)
        (3233, 3120, 2753)
    """
    n = p * q
    phi = (p - 1) * (q - 1)
    d = _modinv(e, phi)
    return n, phi, d


def simulate(text: str, key=17, mode: str = "encrypt", extra=None):
    """Run toy RSA encryption/decryption with a per-character trace.

    Emits a ``keygen`` step first (showing ``p, q → n, phi → e, d``),
    then one step per character (``m^e mod n`` on encrypt, ``c^d mod
    n`` on decrypt) and a final summary step — all in the unified
    SecSim step schema.

    Args:
        text: Plaintext to encrypt, or space/comma-separated integers
            (an earlier encrypt result) to decrypt.
        key: Legacy positional slot for the uniform contract; the real
            parameters come from ``extra`` (kept for dispatcher
            compatibility, ignored here).
        mode: ``"encrypt"`` (default) or ``"decrypt"``.
        extra: ``{"rsa_p": 61, "rsa_q": 53, "rsa_e": 17}``. Characters
            with ``ord(ch) >= n`` are rejected — raise the primes to
            encrypt wider characters (e.g. emoji needs ~20-bit primes).

    Raises:
        ValueError: Bad exponent (not coprime to phi); malformed
            decrypt input; or a character too large for the modulus
            (message names the offending char and suggests bigger
            primes). Surfaced by the API as HTTP 400.

    Returns:
        Tuple ``(result, steps)``: space-separated cipher integers (or
        recovered text) plus the trace.

    Example:
        >>> simulate("Hi", 17, "encrypt", {})[0]
        '3000 3179'
    """
    extra = extra or {}
    p, q, e = int(extra.get("rsa_p", 61)), int(extra.get("rsa_q", 53)), int(extra.get("rsa_e", 17))
    n, phi, d = _keygen(p, q, e)
    steps = [
        {
            "index": 0,
            "title": {"ar": "توليد المفاتيح", "en": "Key generation"},
            "description": {
                "ar": f"p={p} و q={q} ← n={n} و φ(n)={phi} ← e={e} و d={d}",
                "en": f"p={p}, q={q} → n={n}, φ(n)={phi} → e={e}, d={d}",
            },
            "snapshot": {"p": p, "q": q, "n": n, "phi": phi, "e": e, "d": d},
            "highlight": [],
            "meta": {"phase": "keygen"},
        }
    ]

    if mode == "decrypt":
        try:
            cipher = [int(x) for x in (text or "").replace(",", " ").split()]
        except Exception:
            raise ValueError("decrypt expects space/comma separated integers")
        chars = []
        for i, c in enumerate(cipher):
            m = pow(c, d, n)
            chars.append(chr(m))
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"فك القيمة {i + 1}", "en": f"Decrypt value {i + 1}"},
                    "description": {
                        "ar": f"{c}^{d} mod {n} = {m} ← '{chr(m)}'",
                        "en": f"{c}^{d} mod {n} = {m} → '{chr(m)}'",
                    },
                    "snapshot": {"c": c, "m": m, "char": chr(m)},
                    "highlight": [i],
                    "meta": {"phase": "decrypt", "position": i},
                }
            )
        result = "".join(chars)
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": "النص المستعاد", "en": "Recovered text"},
                "description": {"ar": f"النتيجة: '{result}'", "en": f"Result: '{result}'"},
                "snapshot": {"result": result},
                "highlight": [],
                "meta": {"phase": "done"},
            }
        )
        return result, steps

    chars = []
    for i, ch in enumerate(text or ""):
        m = ord(ch)
        if m >= n:
            raise ValueError(
                f"char {ch!r} (code {m}) needs n > {m} — increase primes p and q"
            )
        c = pow(m, e, n)
        chars.append(c)
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"تشفير الحرف {i + 1}", "en": f"Encrypt char {i + 1}"},
                "description": {
                    "ar": f"'{ch}'={m} ← {m}^{e} mod {n} = {c}",
                    "en": f"'{ch}'={m} → {m}^{e} mod {n} = {c}",
                },
                "snapshot": {"char": ch, "m": m, "c": c},
                "highlight": [i],
                "meta": {"phase": "encrypt", "position": i},
            }
        )
    result = " ".join(str(c) for c in chars)
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "النتيجة المشفرة", "en": "Encrypted result"},
            "description": {"ar": "القيم مفصولة بمسافات — انسخها لفك التشفير", "en": "Space-separated values — copy them to decrypt"},
            "snapshot": {"result": result, "public_key": {"e": e, "n": n}},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return result, steps


def analyze(extra=None):
    """Return the static security review, sized to the actual modulus.

    Args:
        extra: Optional dict; reads ``rsa_p``/``rsa_q`` (defaults
            61/53) to compute the real modulus bit-length.

    Returns:
        ``{strengths{ar,en}, weaknesses{ar,en}, metrics{n_bits,
        real_world_min_bits: 2048}, complexity}`` — the weakness list
        always flags how far the toy key is from the 2048-bit minimum.
    """
    extra = extra or {}
    p, q = int(extra.get("rsa_p", 61)), int(extra.get("rsa_q", 53))
    bits = (p * q).bit_length()
    return {
        "strengths": {
            "ar": ["الأمان مبني على صعوبة تحليل الأعداد الكبيرة", "المفتاح العام يُنشر بأمان"],
            "en": ["Security rests on hardness of factoring large numbers", "Public key can be shared openly"],
        },
        "weaknesses": {
            "ar": [f"هذه المفاتيح التعليمية ({bits} بت) تُكسر فوراً بالتحليل", "الاستخدام الحقيقي يتطلب 2048+ بت وحشو OAEP", "التشفير حرفاً بحرف يسرب التكرار"],
            "en": [f"These toy keys ({bits} bits) factor instantly", "Real use needs 2048+ bits and OAEP padding", "Char-by-char encryption leaks frequency"],
        },
        "metrics": {"n_bits": bits, "real_world_min_bits": 2048},
        "complexity": COMPLEXITY,
    }


# Self-registration: makes "rsa" visible to the dispatcher, the
# /api/algorithms catalog and the contract guard tests — no other file
# needs editing when this module changes.
register(
    "rsa",
    type="encryption",
    name={"ar": "RSA", "en": "RSA"},
    description={
        "ar": "تشفير بالمفتاح العام — مفاتيح صغيرة للتعليم فقط",
        "en": "Public-key encryption — tiny teaching keys only",
    },
    params=["p", "q", "e", "mode"],
    keyspace="toy",
    order=30,
)

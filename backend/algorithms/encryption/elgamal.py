"""ElGamal encryption (educational, small numbers).

Public key (p, g, y=g^x), private key x. Encryption picks an ephemeral
k per message: c1 = g^k mod p, c2 = m·y^k mod p. Decryption recovers
m = c2·(c1^x)^-1 mod p. Each character encrypts as one pair, so the
ciphertext is inherently randomized (same letter → different pair).

Teaching only: tiny primes fall to discrete log instantly, raw
textbook mapping leaks frequency like RSA, and reusing k across two
messages leaks the plaintext ratio. Real systems need 2048+ bits,
hybrid (ECIES-style) construction and hashed mapping.

Wire format: encrypt returns space-separated ``"c1,c2"`` pairs and
decrypt takes that same string back.
"""

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n · log p)",
    "space": "O(n)",
    "n": {"ar": "عدد أحرف الرسالة", "en": "number of message characters"},
    "note": {
        "ar": "كل حرف يكلف أسّين modularيين — أثقل من المتماثل، والناتج يتضاعف (زوج لكل حرف)",
        "en": "Each character costs two modular exponentiations — heavier than symmetric, and output doubles (a pair per char)",
    },
}

DETAILS = {
    "overview": {
        "ar": "تشفير الجمل بالمفتاح العام: مفتاح عام (p,g,y) يشفر به الجميع ومفتاح خاص x يفك به مالكه. الأمان مبني على صعوبة اللوغاريتم المنفصل، والتشفير عشوائي بطبيعته (نفس الحرف يعطي زوجاً مختلفاً كل مرة).",
        "en": "ElGamal public-key encryption: public key (p, g, y) anyone encrypts with, private key x only its owner decrypts with. Security rests on discrete-log hardness, and encryption is randomized by design (same letter → a different pair each time).",
    },
    "history": {
        "ar": "نشره طاهر الجمل سنة 1985 فوق فكرة ديفي-هيلمان، وأصبح أساس التوقيعات الرقمية (DSA) والتشفير الهجين. أعداد المنصة صغيرة للعرض؛ الواقع يستخدم 2048+ بت أو منحنيات إهليجية.",
        "en": "Published by Taher ElGamal in 1985 on top of the Diffie–Hellman idea; it became the basis of digital signatures (DSA) and hybrid encryption. This platform's numbers are tiny for display; reality uses 2048+ bits or elliptic curves.",
    },
    "how_it_works": {
        "ar": [
            "اختر p أولياً وg مولداً وسر x، وانشر y = g^x mod p.",
            "للتشفير اختر k عشوائياً (لمرة واحدة!) واحسب c1 = g^k وc2 = m·y^k.",
            "أرسل الزوج (c1,c2) لكل حرف — نفس الحرف يعطي زوجاً مختلفاً.",
            "للفك احسب s = c1^x ثم m = c2·s⁻¹ mod p.",
            "لا تعِد استخدام k أبداً: زوجان بنفس k يكشفان نسبة النصين.",
        ],
        "en": [
            "Pick prime p, generator g and secret x; publish y = g^x mod p.",
            "To encrypt, pick a fresh random k (one-time!) and compute c1 = g^k, c2 = m·y^k.",
            "Send the pair (c1,c2) per character — the same letter gives a different pair.",
            "To decrypt, compute s = c1^x, then m = c2·s⁻¹ mod p.",
            "Never reuse k: two pairs under one k reveal the plaintext ratio.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "elgamal_p", "desc": "المعامل الأولي (الافتراضي 2579 — للتعليم فقط)."},
            {"name": "elgamal_g", "desc": "المولد (الافتراضي 2)."},
            {"name": "elgamal_x", "desc": "المفتاح الخاص (الافتراضي 101)."},
            {"name": "elgamal_k", "desc": "العشوائي المؤقت k (الافتراضي 7 — لمرة واحدة!)."},
            {"name": "mode", "desc": "encrypt لنص عادي أو decrypt لأزواج c1,c2."},
        ],
        "en": [
            {"name": "elgamal_p", "desc": "Prime modulus (default 2579 — teaching only)."},
            {"name": "elgamal_g", "desc": "Generator (default 2)."},
            {"name": "elgamal_x", "desc": "Private key (default 101)."},
            {"name": "elgamal_k", "desc": "Ephemeral random k (default 7 — one-time!)."},
            {"name": "mode", "desc": "encrypt for plaintext or decrypt for c1,c2 pairs."},
        ],
    },
    "security": {
        "ar": "هذه الأعداد الصغيرة تُكسر فوراً باللوغاريتم المنفصل، والتشفير الخام حرفاً بحرف يسرب التكرار، وإعادة استخدام k كارثية. الواقع: 2048+ بت + k عشوائي حقيقي + بناء هجين + حشو.",
        "en": "These tiny numbers break instantly via discrete log, raw char-by-char encryption leaks frequency, and k reuse is catastrophic. Reality: 2048+ bits + truly random k + hybrid construction + padding.",
    },
    "uses": {
        "ar": ["أساس DSA للتوقيعات", "التشفير الهجين", "تعليم العشوائية في التشفير العام"],
        "en": ["Basis of DSA signatures", "Hybrid encryption", "Teaching randomness in public-key encryption"],
    },
}

# Max characters with individual trace steps; longer inputs get one
# summary step instead of an unbounded tape.
_MAX_TRACED_CHARS = 8


def _params(extra: dict):
    extra = extra or {}
    try:
        p = int(extra.get("elgamal_p", 2579))
        g = int(extra.get("elgamal_g", 2))
        x = int(extra.get("elgamal_x", 101))
        k = int(extra.get("elgamal_k", 7))
    except (TypeError, ValueError):
        raise ValueError("elgamal_p, elgamal_g, elgamal_x, elgamal_k must be integers")
    if p < 5:
        raise ValueError("elgamal_p must be a prime ≥ 5 (try 2579)")
    if not (1 <= g < p):
        raise ValueError("elgamal_g must satisfy 1 ≤ g < p")
    if not (1 <= x < p):
        raise ValueError("elgamal_x must satisfy 1 ≤ x < p")
    if not (1 <= k < p):
        raise ValueError("elgamal_k must satisfy 1 ≤ k < p")
    return p, g, x, k


def _modinv(a: int, m: int) -> int:
    g, x, _ = _egcd(a % m, m)
    if g != 1:
        raise ValueError("no modular inverse — check elgamal_p is prime")
    return x % m


def _egcd(a: int, b: int):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    p, g, x, k = _params(extra or {})
    if mode not in ("encrypt", "decrypt"):
        raise ValueError("mode must be 'encrypt' or 'decrypt'")
    y = pow(g, x, p)

    steps = [
        {
            "index": 0,
            "title": {"ar": "توليد المفاتيح", "en": "Key generation"},
            "description": {
                "ar": f"p={p} وg={g} علنيان | الخاص x={x} سري | العام y = g^x mod p = {y}",
                "en": f"p={p}, g={g} public | private x={x} secret | public y = g^x mod p = {y}",
            },
            "snapshot": {"p": p, "g": g, "y": y, "mode": mode},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    ]

    if mode == "encrypt":
        chars = list(text or "")
        for m in (ord(c) for c in chars):
            if m >= p:
                raise ValueError(
                    f"character code {m} ≥ p={p} — pick a bigger elgamal_p (like RSA's hint)"
                )
        c1 = pow(g, k, p)
        yk = pow(y, k, p)
        pairs: list[str] = []
        for i, ch in enumerate(chars):
            m = ord(ch)
            c2 = (m * yk) % p
            pairs.append(f"{c1},{c2}")
            if i >= _MAX_TRACED_CHARS:
                continue
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"تشفير الحرف {i + 1}", "en": f"Encrypt char {i + 1}"},
                    "description": {
                        "ar": f"'{ch}' (m={m}): c1 = g^k = {c1} | c2 = m·y^k = {m}×{yk} mod {p} = {c2}",
                        "en": f"'{ch}' (m={m}): c1 = g^k = {c1} | c2 = m·y^k = {m}×{yk} mod {p} = {c2}",
                    },
                    "snapshot": {"position": i, "char": ch, "m": m, "c1": c1, "c2": c2},
                    "highlight": [i],
                    "meta": {"phase": "encrypt", "position": i},
                }
            )
        if len(chars) > _MAX_TRACED_CHARS:
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"... {len(chars) - _MAX_TRACED_CHARS} أحرف أخرى", "en": f"... {len(chars) - _MAX_TRACED_CHARS} more chars"},
                    "description": {
                        "ar": "نفس الزوج (c1 ثابت لنفس k) مع c2 مختلف لكل حرف",
                        "en": "Same c1 (fixed k), different c2 per character",
                    },
                    "snapshot": {"remaining": len(chars) - _MAX_TRACED_CHARS},
                    "highlight": [],
                    "meta": {"phase": "encrypt"},
                }
            )
        result = " ".join(pairs)
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": "النتيجة المشفرة", "en": "Encrypted result"},
                "description": {
                    "ar": "الأزواج مفصولة بمسافات — انسخها لفك التشفير (لاحظ: نفس k ← نفس c1)",
                    "en": "Space-separated pairs — copy them to decrypt (note: same k → same c1)",
                },
                "snapshot": {"result": result, "public_key": {"p": p, "g": g, "y": y}},
                "highlight": [],
                "meta": {"phase": "done"},
            }
        )
        return result, steps

    # decrypt: parse "c1,c2 c1,c2 ..."
    raw = (text or "").strip().replace(",", " ")
    parts = raw.split()
    if len(parts) % 2 != 0:
        raise ValueError("decrypt expects space-separated c1,c2 pairs from encrypt")
    try:
        nums = [int(t) for t in parts]
    except ValueError:
        raise ValueError("decrypt expects space-separated c1,c2 pairs from encrypt")
    out: list[str] = []
    for i in range(0, len(nums), 2):
        c1, c2 = nums[i], nums[i + 1]
        s = pow(c1, x, p)
        m = (c2 * _modinv(s, p)) % p
        try:
            out.append(chr(m))
        except (ValueError, OverflowError):
            raise ValueError(f"recovered code {m} is not a valid character — wrong key?")
        if i // 2 < _MAX_TRACED_CHARS:
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"فك الزوج {i // 2 + 1}", "en": f"Decrypt pair {i // 2 + 1}"},
                    "description": {
                        "ar": f"({c1},{c2}): s = c1^x = {s} | m = c2·s⁻¹ mod {p} = '{out[-1]}'",
                        "en": f"({c1},{c2}): s = c1^x = {s} | m = c2·s⁻¹ mod {p} = '{out[-1]}'",
                    },
                    "snapshot": {"c1": c1, "c2": c2, "s": s, "char": out[-1]},
                    "highlight": [i // 2],
                    "meta": {"phase": "decrypt", "position": i // 2},
                }
            )
    result = "".join(out)
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "النص المستعاد", "en": "Recovered plaintext"},
            "description": {"ar": f"'{text[:32]}...' → '{result}'", "en": f"'{text[:32]}...' → '{result}'"},
            "snapshot": {"result": result},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return result, steps


def analyze(extra=None):
    p, _, _, _ = _params({**(extra or {}), "elgamal_x": (extra or {}).get("elgamal_x", 101),
                          "elgamal_k": (extra or {}).get("elgamal_k", 7)})
    bits = p.bit_length()
    return {
        "strengths": {
            "ar": ["التشفير عشوائي: نفس الحرف يعطي زوجاً مختلفاً كل مرة", "الأمان مبني على اللوغاريتم المنفصل"],
            "en": [
                "Randomized encryption: same letter gives a different pair each time",
                "Security rests on discrete-log hardness",
            ],
        },
        "weaknesses": {
            "ar": [
                f"هذا المعامل ({bits} بت) يُكسر فوراً باللوغاريتم المنفصل",
                "إعادة استخدام k تكشف نسبة النصوص",
                "الناتج ضعف الدخل (زوج لكل حرف) والواقع يحتاج 2048+ بت وبناء هجين",
            ],
            "en": [
                f"This modulus ({bits} bits) breaks instantly via discrete log",
                "Reusing k reveals plaintext ratios",
                "Output doubles input (pair per char); reality needs 2048+ bits + hybrid",
            ],
        },
        "metrics": {"p_bits": bits, "real_world_min_bits": 2048},
        "complexity": COMPLEXITY,
    }


register(
    "elgamal",
    type="encryption",
    family="asymmetric",
    kind="discrete",
    security="educational",
    name={"ar": "الجمل", "en": "ElGamal"},
    description={
        "ar": "تشفير بالمفتاح العام بلوغاريتم منفصل — أعداد صغيرة للتعليم",
        "en": "Discrete-log public-key encryption — tiny teaching numbers",
    },
    params=["elgamal_p", "elgamal_g", "elgamal_x", "elgamal_k", "mode"],
    keyspace="toy",
    order=34,
)

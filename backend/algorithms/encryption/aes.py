"""AES-CBC (educational) with per-block step trace.

Honest, simplified teaching flow: PKCS#7 padding -> manual CBC chaining
built on the ECB primitive so every XOR + block encryption is visible.
NOT production guidance: random IV per run, key derived by pad/truncate.

Wire format: encrypt returns ``"iv_hex:cipher_hex"`` and decrypt takes
that same string back. The IV is random per run, so encrypting the same
text twice yields different ciphertext (a visible CBC property).

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"aes"`` at the bottom of this
file (see :mod:`app.services.registry`).

Security warning: key handling here is deliberately naive (UTF-8 text
zero-padded/truncated to key length) to keep the demo readable. Real
systems must use cryptographically random keys and authenticated modes
(e.g. GCM) — never copy this key derivation.
"""
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from app.services.registry import register

ROUNDS = {16: 10, 24: 12, 32: 14}

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(n)",
    "n": {"ar": "عدد بايتات الدخل (الكتل = n÷16)", "en": "input bytes (blocks = n÷16)"},
    "note": {
        "ar": "عدد الجولات ثابت حسب حجم المفتاح (10/12/14) — التكلفة تنمو خطياً مع عدد الكتل",
        "en": "Round count is fixed per key size (10/12/14) — cost grows linearly with block count",
    },
}

DETAILS = {
    "overview": {
        "ar": "معيار التشفير المتقدم (AES) هو عماد التشفير المتماثل الحديث: يشفر كتلاً حجمها 128-بت بمفاتيح 128 أو 192 أو 256 بت عبر شبكة إبدال-تبديل من عدة جولات. نفس المفتاح يُستخدم للتشفير والفك.",
        "en": "The Advanced Encryption Standard (AES) is the backbone of modern symmetric encryption: it encrypts 128-bit blocks with 128, 192 or 256-bit keys through a multi-round substitution–permutation network. The same key encrypts and decrypts.",
    },
    "history": {
        "ar": "في 1997 طرح معهد NIST مسابقة علنية لاستبدال DES المتقادم، وفازت شيفرة Rijndael للباحثين دايمن ورايمن سنة 2000 واعتُمدت معياراً سنة 2001. صمدت منذ ذلك الحين أمام كل محاولات الكسر العملية.",
        "en": "In 1997 NIST launched an open contest to replace aging DES; the Rijndael cipher by Daemen and Rijmen won in 2000 and became the standard in 2001. It has resisted all practical attacks ever since.",
    },
    "how_it_works": {
        "ar": [
            "يُقسَّم الدخل إلى كتل 16 بايت مع حشو PKCS#7، ويُولَّد IV عشوائي لوضع CBC.",
            "تُوسَّع مفتاح الجلسة إلى مفاتيح جولات (Key Expansion).",
            "كل كتلة تمر بـ 10 أو 12 أو 14 جولة: إبدال البايتات (SubBytes)، إزاحة الصفوف (ShiftRows)، خلط الأعمدة (MixColumns ما عدا الأخيرة)، ثم XOR مع مفتاح الجولة (AddRoundKey).",
            "في CBC تُخلط كل كتلة مع ناتج سابقتها (XOR) قبل تشفيرها، فيختفي أي تكرار.",
            "الفك يعكس كل خطوة بنفس المفتاح ثم يُزال الحشو.",
        ],
        "en": [
            "Input is split into 16-byte blocks with PKCS#7 padding, and a random IV is generated for CBC mode.",
            "The session key is expanded into round keys (Key Expansion).",
            "Each block goes through 10, 12 or 14 rounds: SubBytes, ShiftRows, MixColumns (except last round), then XOR with the round key (AddRoundKey).",
            "In CBC each block is XORed with the previous output before encryption, hiding all repetition.",
            "Decryption inverts every step with the same key, then padding is removed.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "key_text", "desc": "نص المفتاح (يُكيَّف لطول الحجم المطلوب — للتعليم فقط، والصحيح توليد عشوائي آمن)."},
            {"name": "key_size", "desc": "طول المفتاح بالبت: 128 (10 جولات) أو 192 (12) أو 256 (14)."},
            {"name": "mode", "desc": "encrypt للتشفير أو decrypt لفك صيغة iv_hex:cipher_hex."},
        ],
        "en": [
            {"name": "key_text", "desc": "Key text (fit to the required size — teaching only; real keys must be securely random)."},
            {"name": "key_size", "desc": "Key length in bits: 128 (10 rounds), 192 (12) or 256 (14)."},
            {"name": "mode", "desc": "encrypt to encipher or decrypt to reverse an iv_hex:cipher_hex value."},
        ],
    },
    "security": {
        "ar": "آمن عملياً بمفتاح سليم، لكن الأمان ينهار بسوء الاستخدام: مفتاح ضعيف، IV متكرر، وضع ECB الذي يُظهر التكرار، أو غياب التوثيق (استخدم أوضاعاً موثقة مثل GCM). القنوات الجانبية تهدد التطبيقات لا الخوارزمية.",
        "en": "Practically secure with a sound key, but misuse destroys it: weak keys, reused IVs, ECB mode leaking patterns, or missing authentication (prefer authenticated modes like GCM). Side channels threaten implementations, not the cipher.",
    },
    "uses": {
        "ar": ["اتصالات TLS/HTTPS", "تشفير الأقراص (BitLocker وFileVault)", "شبكات WPA2/WPA3 اللاسلكية", "تشفير النسخ الاحتياطية وقواعد البيانات"],
        "en": ["TLS/HTTPS connections", "Full-disk encryption (BitLocker, FileVault)", "WPA2/WPA3 wireless", "Backup and database encryption"],
    },
}


def _fit_key(key_text: str, size: int) -> bytes:
    """Stretch/truncate key text to exactly ``size`` bytes (demo-grade).

    Short keys are zero-padded, long ones truncated. This is NOT a KDF
    (no salt, no stretching — use PBKDF2/Argon2 in real systems); it
    exists only so learners can type memorable words as keys.

    Args:
        key_text: Human-typed key material.
        size: Required length in bytes (16, 24 or 32).

    Returns:
        Exactly ``size`` bytes ready for ``AES.new``.
    """
    raw = (key_text or "").encode("utf-8")
    if len(raw) < size:
        raw = raw + b"\x00" * (size - len(raw))
    return raw[:size]


def _pkcs7(data: bytes) -> bytes:
    """Pad to a 16-byte multiple per PKCS#7 (pad byte value = pad length).

    Args:
        data: Raw plaintext bytes.

    Returns:
        Padded bytes whose length is a multiple of 16.

    Example:
        >>> _pkcs7(b"Hi")
        b'Hi\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e\x0e'
    """
    pad = 16 - (len(data) % 16)
    return data + bytes([pad] * pad)


def _unpad(data: bytes) -> bytes:
    """Strip PKCS#7 padding, validating the pad length first.

    Args:
        data: Decrypted bytes still carrying padding.

    Raises:
        ValueError: If the pad-length byte is outside ``1..16``
            (wrong key or corrupted ciphertext surface here).

    Returns:
        The original unpadded bytes.
    """
    pad = data[-1]
    if pad < 1 or pad > 16:
        raise ValueError("bad padding")
    return data[:-pad]


def _xor(a: bytes, b: bytes) -> bytes:
    """Byte-wise XOR of two equal-length blocks (the CBC chaining op).

    Args:
        a: First block (plaintext block on encrypt, decrypted block
            on decrypt).
        b: Second block (previous ciphertext, or the IV for block 0).

    Returns:
        ``bytes(x ^ y for each pair)``.
    """
    return bytes(x ^ y for x, y in zip(a, b))


def simulate(text: str, key: str = "secret", mode: str = "encrypt", extra=None):
    """Run AES-CBC encryption/decryption with a per-block step trace.

    Encrypt path: UTF-8 encode → PKCS#7 pad → random 16-byte IV →
    CBC-chain each block (XOR with previous ciphertext, then AES-ECB
    encrypt) → return ``"iv_hex:cipher_hex"``. Decrypt path reverses it
    and validates padding (failure means wrong key/corrupt data).

    Args:
        text: Plaintext to encrypt, or an ``"iv_hex:cipher_hex"``
            string (typically copy-pasted from an encrypt result) to
            decrypt.
        key: Fallback key text when ``extra`` carries no ``key_text``.
        mode: ``"encrypt"`` (default) or ``"decrypt"``.
        extra: ``{"key_text": str, "key_size": 128|192|256}`` —
            key size selects 10/12/14 rounds respectively.

    Raises:
        ValueError: Bad ``key_size``; malformed ``iv_hex:cipher_hex``
            input; non-block-aligned ciphertext; padding failure on
            decrypt (surfaced by the API as HTTP 400).

    Returns:
        Tuple ``(result, steps)``: the ``iv_hex:cipher_hex`` string (or
        recovered plaintext) plus setup + per-block + done steps in the
        unified schema.

    Example:
        >>> out, steps = simulate("Hello World", "secret", "encrypt", {"key_size": 128})
        >>> back, _ = simulate(out, "secret", "decrypt", {"key_size": 128})
        >>> back
        'Hello World'
    """
    extra = extra or {}
    key_text = str(extra.get("key_text", key if isinstance(key, str) else "secret"))
    key_size = int(extra.get("key_size", 128))
    if key_size not in (128, 192, 256):
        raise ValueError("key_size must be 128, 192 or 256")
    size = key_size // 8
    key = _fit_key(key_text, size)
    rounds = ROUNDS[size]
    steps = []

    if mode == "decrypt":
        try:
            iv_hex, ct_hex = (text or "").split(":", 1)
            iv, ct = bytes.fromhex(iv_hex.strip()), bytes.fromhex(ct_hex.strip())
        except Exception:
            raise ValueError("decrypt expects 'iv_hex:cipher_hex' (copy the encrypt result)")
        if len(ct) % 16 or not ct:
            raise ValueError("invalid ciphertext length")
        ecb = AES.new(key, AES.MODE_ECB)
        steps.append(
            {
                "index": 0,
                "title": {"ar": "الإعداد وفك السلسلة", "en": "Setup & unchain"},
                "description": {
                    "ar": f"AES-{key_size} ({rounds} جولة) — وضع CBC، طول المدخل {len(ct)} بايت = {len(ct)//16} كتلة",
                    "en": f"AES-{key_size} ({rounds} rounds) — CBC mode, {len(ct)} bytes = {len(ct)//16} blocks",
                },
                "snapshot": {"key_size": key_size, "rounds": rounds, "mode": "CBC", "iv": iv.hex(), "blocks": len(ct) // 16},
                "highlight": [],
                "meta": {"phase": "setup"},
            }
        )
        prev, out = iv, b""
        for b in range(len(ct) // 16):
            block = ct[b * 16:(b + 1) * 16]
            dec = ecb.decrypt(block)
            plain = _xor(dec, prev)
            out += plain
            prev = block
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"فك الكتلة {b + 1}", "en": f"Decrypt block {b + 1}"},
                    "description": {
                        "ar": f"فك الكتلة ثم XOR مع السابقة → {plain.hex()}",
                        "en": f"Decrypt block then XOR with previous → {plain.hex()}",
                    },
                    "snapshot": {"block": b + 1, "cipher": block.hex(), "plain": plain.hex()},
                    "highlight": [b],
                    "meta": {"phase": "decrypt", "block": b},
                }
            )
        try:
            result = _unpad(out).decode("utf-8")
        except Exception:
            raise ValueError("decryption failed — wrong key or corrupted data")
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": "إزالة الحشو", "en": "Remove padding"},
                "description": {"ar": f"النص المستعاد: '{result}'", "en": f"Recovered: '{result}'"},
                "snapshot": {"result": result},
                "highlight": [],
                "meta": {"phase": "done"},
            }
        )
        return result, steps

    data = (text or "").encode("utf-8")
    padded = _pkcs7(data)
    iv = get_random_bytes(16)
    ecb = AES.new(key, AES.MODE_ECB)
    n = len(padded) // 16
    steps.append(
        {
            "index": 0,
            "title": {"ar": "الحشو والإعداد", "en": "Padding & setup"},
            "description": {
                "ar": f"AES-{key_size} ({rounds} جولة) — {len(data)} بايت أصبحت {len(padded)} بعد حشو PKCS#7 = {n} كتلة، IV عشوائي",
                "en": f"AES-{key_size} ({rounds} rounds) — {len(data)} bytes padded (PKCS#7) to {len(padded)} = {n} blocks, random IV",
            },
            "snapshot": {"key_size": key_size, "rounds": rounds, "mode": "CBC", "iv": iv.hex(), "blocks": n},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    )
    prev, ct = iv, b""
    for b in range(n):
        block = padded[b * 16:(b + 1) * 16]
        xored = _xor(block, prev)
        enc = ecb.encrypt(xored)
        ct += enc
        prev = enc
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"تشفير الكتلة {b + 1}", "en": f"Encrypt block {b + 1}"},
                "description": {
                    "ar": f"XOR مع السابقة ثم تشفير الكتلة ({rounds} جولة) → {enc.hex()[:32]}…",
                    "en": f"XOR with previous then block encrypt ({rounds} rounds) → {enc.hex()[:32]}…",
                },
                "snapshot": {"block": b + 1, "plain": block.hex(), "xored": xored.hex(), "cipher": enc.hex()},
                "highlight": [b],
                "meta": {"phase": "encrypt", "block": b},
            }
        )
    result = iv.hex() + ":" + ct.hex()
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "النتيجة النهائية", "en": "Final result"},
            "description": {"ar": "الصيغة: iv_hex:cipher_hex", "en": "Format: iv_hex:cipher_hex"},
            "snapshot": {"result": result},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return result, steps


def analyze(extra=None):
    """Return the static security review for AES at the given key size.

    Args:
        extra: Optional dict; reads ``extra["key_size"]``
            (default 128) to report matching round counts.

    Returns:
        ``{strengths{ar,en}, weaknesses{ar,en}, metrics{key_bits,
        rounds, mode}, complexity}``.
    """
    key_size = int((extra or {}).get("key_size", 128))
    return {
        "strengths": {
            "ar": [f"AES-{key_size} معيار عالمي ولا يُكسر عملياً بمفتاح سليم", "وضع CBC يخفي تكرار الكتل"],
            "en": [f"AES-{key_size} is a global standard, infeasible to break with a sound key", "CBC hides block repetition"],
        },
        "weaknesses": {
            "ar": ["أي ضعف في توليد المفتاح أو الـ IV ينسف الأمان", "نسخة العرض تبسّط اشتقاق المفتاح — لا تستخدمها حقيقة"],
            "en": ["Weak key/IV generation destroys security", "This demo simplifies key handling — never use as-is"],
        },
        "metrics": {"key_bits": key_size, "rounds": ROUNDS.get(key_size // 8, 10), "mode": "CBC"},
        "complexity": COMPLEXITY,
    }


# Self-registration: makes "aes" visible to the dispatcher, the
# /api/algorithms catalog and the contract guard tests — no other file
# needs editing when this module changes.
register(
    "aes",
    type="encryption",
    name={"ar": "AES", "en": "AES"},
    description={
        "ar": "معيار التشفير المتقدم — وضع CBC بخطوات كل كتلة",
        "en": "Advanced Encryption Standard — CBC with per-block steps",
    },
    params=["key_text", "key_size", "mode"],
    keyspace="2^128+",
    order=20,
)

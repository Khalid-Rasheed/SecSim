"""RC4 (educational demo) with step-by-step trace.

Byte-oriented stream cipher: Key-Scheduling (KSA) builds a 256-byte
permutation from the key, then Pseudo-Random Generation (PRGA) emits
a keystream XORed with the data. Identical encrypt/decrypt operation.

WARNING: RC4 is broken (biases in the keystream, e.g. Fluhrer–Mantin–
Shamir). Included so learners can watch a real stream cipher and why
it must never be used — use ChaCha20 / AES-GCM instead.

Wire format: encrypt returns hex, decrypt takes hex back.
"""

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(1)",
    "n": {"ar": "عدد بايتات الدخل", "en": "number of input bytes"},
    "note": {
        "ar": "تهيئة S ثابتة (256 بايت) ثم بايت واحد لكل بايت دخل — خطي",
        "en": "Fixed 256-byte S setup, then one keystream byte per input byte — linear",
    },
}

DETAILS = {
    "overview": {
        "ar": "RC4 شيفرة انسيابية: تولّد تيار مفاتيح شبه عشوائي من المفتاح ثم تجمعه مع النص بـ XOR. نفس العملية للتشفير والفك. سريعة وبسيطة — ومكسورة.",
        "en": "RC4 is a stream cipher: it expands the key into a pseudo-random keystream XORed with the data. Same operation both ways. Fast and simple — and broken.",
    },
    "history": {
        "ar": "صممها رون ريفست سنة 1987 (سر تجاري حتى تسرب 1994). استُخدمت في WEP وTLS المبكر، ثم سُحبت بعد انحيازات مثبتة في التيار (2001-2013) وحُظرت في TLS سنة 2015 (RFC 7465).",
        "en": "Designed by Ron Rivest in 1987 (trade secret until the 1994 leak). Used in WEP and early TLS, then withdrawn after proven keystream biases (2001–2013) and banned from TLS in 2015 (RFC 7465).",
    },
    "how_it_works": {
        "ar": [
            "التهيئة KSA: رتّب S = [0..255] واخلطها بالمفتاح.",
            "التوليد PRGA: أنتج بايت تيار لكل بايت دخل (i,j وتبادل).",
            "اجمع كل بايت: C = P XOR K (والفك نفسه).",
            "لا تعِد استخدام نفس المفتاح/IV أبداً — التسرب هنا تعليمي.",
        ],
        "en": [
            "Setup (KSA): start S = [0..255], shuffle it with the key.",
            "Generate (PRGA): emit one keystream byte per input byte (i, j swaps).",
            "Combine: C = P XOR K (decryption is identical).",
            "Never reuse a key/IV — the leak here is the lesson.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "rc4_key", "desc": "نص المفتاح (أي طول — للتعليم فقط)."},
            {"name": "mode", "desc": "encrypt (يخرج hex) أو decrypt (يدخل hex)."},
        ],
        "en": [
            {"name": "rc4_key", "desc": "Key text (any length — teaching only)."},
            {"name": "mode", "desc": "encrypt (outputs hex) or decrypt (takes hex)."},
        ],
    },
    "security": {
        "ar": "مكسور: انحيازات إحصائية في البايتات الأولى وتسرب عند إعادة استخدام المفتاح، ولا سلامة (قابل للتشكيل). البديل: ChaCha20-Poly1305 أو AES-GCM.",
        "en": "Broken: statistical biases in early bytes, catastrophic on key reuse, and malleable (no integrity). Use ChaCha20-Poly1305 or AES-GCM instead.",
    },
    "uses": {
        "ar": ["فهم الشيفرات الانسيابية", "درس في سبب سحب RC4", "مقارنة مع ChaCha20"],
        "en": ["Understanding stream ciphers", "Case study in RC4's withdrawal", "Contrast with ChaCha20"],
    },
}


def _ksa(key: bytes) -> list[int]:
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    return s


def _prga(s: list[int], n: int) -> bytes:
    s = s[:]
    i = j = 0
    out = bytearray()
    for _ in range(n):
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out.append(s[(s[i] + s[j]) % 256])
    return bytes(out)


def _crypt(data: bytes, key_text: str) -> bytes:
    key = (key_text or "secret").encode("utf-8")
    if not key:
        raise ValueError("rc4_key must not be empty")
    return bytes(b ^ k for b, k in zip(data, _prga(_ksa(key), len(data))))


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    extra = extra or {}
    key_text = str(extra.get("rc4_key", "secret"))
    if mode not in ("encrypt", "decrypt"):
        raise ValueError("mode must be 'encrypt' or 'decrypt'")
    if mode == "encrypt":
        data = (text or "").encode("utf-8")
        show_in = f"{len(data)} bytes"
    else:
        try:
            data = bytes.fromhex((text or "").strip())
        except ValueError:
            raise ValueError("decrypt expects hex produced by encrypt")
        show_in = f"{len(data)} bytes (hex)"
    keystream = _prga(_ksa(key_text.encode("utf-8") or b"secret"), len(data))
    result_bytes = bytes(b ^ k for b, k in zip(data, keystream))

    steps = [
        {
            "index": 0,
            "title": {"ar": "الإعداد KSA", "en": "Setup (KSA)"},
            "description": {
                "ar": f"خلط S (256 بايت) بالمفتاح '{key_text}' — الدخل: {show_in}",
                "en": f"Shuffle S (256 bytes) with key '{key_text}' — input: {show_in}",
            },
            "snapshot": {"key": key_text, "input_bytes": len(data)},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    ]
    preview = min(len(data), 8)
    for i in range(preview):
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"بايت التيار {i + 1}", "en": f"Keystream byte {i + 1}"},
                "description": {
                    "ar": f"بايت الدخل {data[i]:02x} XOR تيار {keystream[i]:02x} = {result_bytes[i]:02x}",
                    "en": f"input byte {data[i]:02x} XOR stream {keystream[i]:02x} = {result_bytes[i]:02x}",
                },
                "snapshot": {"position": i, "in_byte": data[i], "stream": keystream[i],
                             "out_byte": result_bytes[i]},
                "highlight": [i],
                "meta": {"phase": "transform", "position": i},
            }
        )
    if len(data) > preview:
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"... {len(data) - preview} بايت أخرى", "en": f"... {len(data) - preview} more bytes"},
                "description": {
                    "ar": "نفس عملية XOR لكل بايت متبقٍ",
                    "en": "Same XOR for each remaining byte",
                },
                "snapshot": {"remaining": len(data) - preview},
                "highlight": [],
                "meta": {"phase": "transform"},
            }
        )
    if mode == "encrypt":
        result = result_bytes.hex()
    else:
        try:
            result = result_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("wrong key or corrupted hex — bytes are not valid UTF-8")
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "النتيجة النهائية", "en": "Final result"},
            "description": {
                "ar": f"الناتج ({len(result_bytes)} بايت): {result[:64]}{'...' if len(result) > 64 else ''}",
                "en": f"Output ({len(result_bytes)} bytes): {result[:64]}{'...' if len(result) > 64 else ''}",
            },
            "snapshot": {"result": result, "bytes": len(result_bytes)},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return result, steps


def analyze(extra=None):
    extra = extra or {}
    key_text = str(extra.get("rc4_key", "secret"))
    bits = len(key_text.encode("utf-8")) * 8
    return {
        "strengths": {
            "ar": ["بسيط وسريع — مثالي لفهم الشيفرات الانسيابية"],
            "en": ["Simple and fast — ideal for learning stream ciphers"],
        },
        "weaknesses": {
            "ar": [
                "انحيازات موثقة في التيار (FMS وغيرها)",
                "إعادة استخدام المفتاح تكشف النص (C1 XOR C2 = P1 XOR P2)",
                "لا يوفر سلامة — قابل للتشكيل",
            ],
            "en": [
                "Documented keystream biases (FMS et al.)",
                "Key reuse leaks plaintext (C1 XOR C2 = P1 XOR P2)",
                "No integrity — malleable",
            ],
        },
        "metrics": {"key_bytes": len(key_text.encode("utf-8")), "key_bits": bits,
                    "status": "broken — do not use"},
        "complexity": COMPLEXITY,
    }


register(
    "rc4",
    type="encryption",
    family="symmetric",
    kind="stream",
    security="broken",
    name={"ar": "RC4", "en": "RC4"},
    description={
        "ar": "شيفرة انسيابية تاريخية مكسورة — للتعليم فقط",
        "en": "Historic broken stream cipher — teaching only",
    },
    params=["rc4_key", "mode"],
    keyspace="2^(8·keylen)",
    order=14,
)

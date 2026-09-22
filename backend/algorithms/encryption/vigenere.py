"""Vigenère cipher with step-by-step trace (polyalphabetic substitution).

Each letter shifts by the corresponding key letter (A=0..Z=25),
repeating the key. Non-Latin chars pass through but still consume
no key position (classic variant: key advances only on Latin letters).

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"vigenere"``.
"""

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(n)",
    "n": {"ar": "عدد أحرف النص", "en": "number of text characters"},
    "note": {
        "ar": "عمل ثابت لكل حرف (إزاحة حسب حرف المفتاح) — خطي، لكن مساحة المفاتيح تنمو أسياً مع طول المفتاح",
        "en": "Constant work per character (shift by key letter) — linear, but keyspace grows exponentially with key length",
    },
}

DETAILS = {
    "overview": {
        "ar": "شيفرة فيجينير: تعميم لقيصر بمفتاح كلمة بدل إزاحة واحدة. كل حرف يُزاح بمقدار حرف المفتاح المقابل (A=0). كانت تُلقب «الشيفرة المستحيلة» لقرون قبل كسرها بتحليل كاسيسكي.",
        "en": "The Vigenère cipher: Caesar generalized with a keyword instead of one shift. Each letter shifts by its key letter (A=0). Called 'le chiffre indéchiffrable' for centuries until Kasiski broke it.",
    },
    "history": {
        "ar": "وُصفت سنة 1553 ثم نُسبت لفيجينير (1586). صمدت ~300 سنة حتى كسرها باباج وكاسيسكي (1850-1860) بإيجاد طول المفتاح من التكرارات ثم تحليل تكرار كل عمود كقيصر مستقل.",
        "en": "Described in 1553, attributed to Vigenère (1586). Stood ~300 years until Babbage and Kasiski (1850s-1860s) broke it by finding key length from repeats, then frequency-analyzing each column as Caesar.",
    },
    "how_it_works": {
        "ar": [
            "نظّف المفتاح (حروف لاتينية فقط، A=0 .. Z=25) وكرره على طول النص.",
            "لكل حرف لاتيني: C = (P + K) mod 26 للتشفير، وP = (C − K) mod 26 للفك.",
            "الرموز غير اللاتينية تُترك كما هي ولا تستهلك موضع مفتاح.",
            "الفك يعيد نفس الخطوات عكسياً بنفس المفتاح.",
        ],
        "en": [
            "Clean the key (Latin letters only, A=0..Z=25) and repeat it over the text.",
            "For each Latin letter: C = (P + K) mod 26 to encrypt, P = (C − K) mod 26 to decrypt.",
            "Non-Latin symbols pass through and consume no key position.",
            "Decryption replays the same steps in reverse with the same key.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "vigenere_key", "desc": "كلمة المفتاح (مثل LEMON). الأطول أقوى: المساحة 26^L."},
            {"name": "mode", "desc": "encrypt للتشفير أو decrypt للفك."},
        ],
        "en": [
            {"name": "vigenere_key", "desc": "Keyword (e.g. LEMON). Longer is stronger: keyspace 26^L."},
            {"name": "mode", "desc": "encrypt to encipher or decrypt to reverse."},
        ],
    },
    "security": {
        "ar": "مكسورة عملياً: طول المفتاح يُكتشف باختبار كاسيسكي/معامل التطابق ثم يُكسر كل عمود بتكرار الحروف. لا تستخدمها حقيقة — هي جسر تعليمي بين قيصر والحديث.",
        "en": "Practically broken: key length leaks via Kasiski/index-of-coincidence, then each column falls to frequency analysis. Never use it for real — it is a teaching bridge from Caesar to modern ciphers.",
    },
    "uses": {
        "ar": ["تعليم التشفير متعدد الأبجدية", "فهم هجمات كاسيسكي", "ألغاز تاريخية"],
        "en": ["Teaching polyalphabetic encryption", "Understanding Kasiski attacks", "Historical puzzles"],
    },
}


def _clean_key(key_text: str) -> list[int]:
    shifts = [ord(c.upper()) - 65 for c in (key_text or "") if c.isalpha() and c.isascii()]
    if not shifts:
        raise ValueError("vigenere_key must contain at least one Latin letter")
    return shifts


def _shift(ch: str, k: int) -> str:
    if "a" <= ch <= "z":
        return chr((ord(ch) - 97 + k) % 26 + 97)
    if "A" <= ch <= "Z":
        return chr((ord(ch) - 65 + k) % 26 + 65)
    return ch


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    extra = extra or {}
    key_text = str(extra.get("vigenere_key", "LEMON"))
    shifts = _clean_key(key_text)
    if mode not in ("encrypt", "decrypt"):
        raise ValueError("mode must be 'encrypt' or 'decrypt'")

    steps = [
        {
            "index": 0,
            "title": {"ar": "الإعداد الأولي", "en": "Setup"},
            "description": {
                "ar": f"النص: '{text}' | المفتاح: '{key_text}' ({len(shifts)} أحرف) | الوضع: {mode}",
                "en": f"Input: '{text}' | Key: '{key_text}' ({len(shifts)} letters) | Mode: {mode}",
            },
            "snapshot": {"key": key_text, "key_length": len(shifts), "mode": mode},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    ]
    out: list[str] = []
    key_pos = 0
    for i, ch in enumerate(text or ""):
        if ch.isalpha() and ch.isascii():
            k = shifts[key_pos % len(shifts)]
            if mode == "decrypt":
                k = (-k) % 26
            new_ch = _shift(ch, k)
            out.append(new_ch)
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"معالجة الحرف {i + 1}", "en": f"Process char {i + 1}"},
                    "description": {
                        "ar": f"'{ch}' + مفتاح '{chr(shifts[key_pos % len(shifts)] + 65)}' → '{new_ch}'",
                        "en": f"'{ch}' + key '{chr(shifts[key_pos % len(shifts)] + 65)}' → '{new_ch}'",
                    },
                    "snapshot": {"position": i, "char_in": ch, "char_out": new_ch,
                                 "key_char": chr(shifts[key_pos % len(shifts)] + 65)},
                    "highlight": [i],
                    "meta": {"phase": "transform", "position": i},
                }
            )
            key_pos += 1
        else:
            out.append(ch)
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"تمرير الرمز {i + 1}", "en": f"Pass through {i + 1}"},
                    "description": {
                        "ar": f"'{ch}' ليس حرفاً لاتينياً — يُترك كما هو",
                        "en": f"'{ch}' is not a Latin letter — unchanged",
                    },
                    "snapshot": {"position": i, "char_in": ch, "char_out": ch},
                    "highlight": [i],
                    "meta": {"phase": "transform", "position": i},
                }
            )
    result = "".join(out)
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "النتيجة النهائية", "en": "Final result"},
            "description": {"ar": f"'{text}' → '{result}'", "en": f"'{text}' → '{result}'"},
            "snapshot": {"current_text": result, "result": result},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return result, steps


def analyze(extra=None):
    extra = extra or {}
    key_text = str(extra.get("vigenere_key", "LEMON"))
    clean = [c for c in key_text if c.isalpha() and c.isascii()]
    L = len(clean) or 5
    try:
        keyspace = 26 ** L
    except OverflowError:
        keyspace = 10**30
    return {
        "strengths": {
            "ar": ["أقوى من قيصر بكثير (تعدد الأبجديات يخفي التكرار السطحي)"],
            "en": ["Far stronger than Caesar (polyalphabetic hides surface frequency)"],
        },
        "weaknesses": {
            "ar": [
                "طول المفتاح يتسرب عبر التكرارات (كاسيسكي)",
                "كل عمود يُكسر كقيصر مستقل",
                "المفتاح القصير أو المتكرر قاتل",
            ],
            "en": [
                "Key length leaks via repeats (Kasiski)",
                "Each column breaks as independent Caesar",
                "Short or repeating keys are fatal",
            ],
        },
        "metrics": {"key_length": L, "keyspace": keyspace, "key": key_text},
        "complexity": COMPLEXITY,
    }


register(
    "vigenere",
    type="encryption",
    family="symmetric",
    kind="classical",
    security="broken",
    name={"ar": "فيجينير", "en": "Vigenère"},
    description={
        "ar": "تشفير متعدد الأبجدية بكلمة مفتاح — مكسور تعليمياً",
        "en": "Polyalphabetic cipher with keyword — educational, broken",
    },
    params=["vigenere_key", "mode"],
    keyspace=26**5,
    order=12,
)

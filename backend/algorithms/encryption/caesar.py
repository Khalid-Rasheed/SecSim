"""Caesar cipher with step-by-step trace for educational simulation.

Shifts every Latin letter by a fixed key (``C = (P + k) mod 26``),
wrapping around the alphabet; digits, spaces, symbols and non-Latin
scripts (e.g. Arabic) pass through unchanged. Encryption and
decryption are the same operation with opposite shift signs.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"caesar"`` at the bottom of
this file (see :mod:`app.services.registry`).

Teaching status: completely insecure (25-key keyspace) — included so
learners can watch, break and measure a trivially weak cipher.
"""

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(n)",
    "n": {"ar": "عدد أحرف النص", "en": "number of text characters"},
    "note": {
        "ar": "عمل ثابت لكل حرف (إزاحة واحدة) — خطي تماماً",
        "en": "Constant work per character (one shift) — strictly linear",
    },
}

DETAILS = {
    "overview": {
        "ar": "شيفرة قيصر هي أبسط أنواع التشفير الإبدالي: كل حرف يُستبدل بالحرف الذي يليه بمسافة ثابتة (المفتاح) داخل الأبجدية. الحروف تلف حول نهاية الأبجدية، وأي رمز غير أبجدي يُترك كما هو.",
        "en": "The Caesar cipher is the simplest substitution cipher: each letter is replaced by the letter a fixed distance (the key) ahead in the alphabet. Letters wrap around, and non-letters are left untouched.",
    },
    "history": {
        "ar": "سُمّيت باسم يوليوس قيصر الذي استخدمها — وفق المؤرخين — بإزاحة 3 لحماية مراسلاته العسكرية في القرن الأول قبل الميلاد. وهي اليوم أول ما يُدرّس في علم التشفير.",
        "en": "Named after Julius Caesar, who reportedly used it with a shift of 3 to protect military correspondence in the 1st century BC. Today it is the first cipher taught in cryptography courses.",
    },
    "how_it_works": {
        "ar": [
            "اختر المفتاح k (من 1 إلى 25) واتجاه العملية (تشفير/فك).",
            "لكل حرف: انقله k مواضع للأمام (تشفير) أو للخلف (فك) مع الالتفاف حول الأبجدية: C = (P + k) mod 26.",
            "اترك المسافات والأرقام والرموز دون تغيير.",
            "النتيجة: نص مشفر يُفك بنفس المفتاح عكسياً.",
        ],
        "en": [
            "Pick key k (1–25) and the direction (encrypt/decrypt).",
            "For each letter: move k positions forward (encrypt) or backward (decrypt), wrapping around: C = (P + k) mod 26.",
            "Leave spaces, digits and symbols unchanged.",
            "Result: ciphertext reversible with the same key.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "key", "desc": "مقدار الإزاحة (0–25). المفتاح 3 هو الأشهر تاريخياً."},
            {"name": "mode", "desc": "encrypt للتشفير أو decrypt للفك (إزاحة عكسية)."},
        ],
        "en": [
            {"name": "key", "desc": "Shift amount (0–25). Key 3 is the historic classic."},
            {"name": "mode", "desc": "encrypt to encipher or decrypt to reverse the shift."},
        ],
    },
    "security": {
        "ar": "غير آمنة إطلاقاً: 25 مفتاحاً فقط تُجرَّب في أجزاء من الثانية، وتحليل تكرار الحروف يكشف النص حتى دون تجربة كل المفاتيح. لا تستخدمها لأي غرض حقيقي.",
        "en": "Completely insecure: only 25 keys to try in a fraction of a second, and letter-frequency analysis breaks it without even trying all keys. Never use it for anything real.",
    },
    "uses": {
        "ar": ["تعليم مبادئ التشفير", "الألغاز (مثل ROT13 بإزاحة 13)", "مدخل لفهم تحليل التكرار وهجمات القوة الغاشمة"],
        "en": ["Teaching cipher fundamentals", "Puzzles (e.g. ROT13 with shift 13)", "Gateway to frequency analysis and brute-force attacks"],
    },
}


def _shift_char(ch: str, shift: int) -> str:
    """Shift one character inside its alphabet, wrapping around.

    Only ASCII ``a-z`` / ``A-Z`` are shifted (via modular arithmetic);
    everything else — digits, punctuation, Arabic, emoji — is returned
    unchanged, which keeps encrypt/decrypt perfectly reversible on
    mixed-language text.

    Args:
        ch: Single character to transform.
        shift: Already-normalised shift in ``0..25``.

    Returns:
        The shifted character, or ``ch`` itself when non-Latin.

    Example:
        >>> _shift_char("H", 3)
        'K'
    """
    if "a" <= ch <= "z":
        return chr((ord(ch) - ord("a") + shift) % 26 + ord("a"))
    if "A" <= ch <= "Z":
        return chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))
    return ch


def simulate(text: str, key: int = 3, mode: str = "encrypt", extra=None):
    """Encrypt/decrypt text while recording one step per character.

    Emits a ``setup`` step, one ``transform`` step per input character
    (showing ``char_in → char_out`` plus the running output), and a
    final ``done`` step — each following the unified SecSim step schema
    (``index`` / ``title{ar,en}`` / ``description{ar,en}`` /
    ``snapshot`` / ``highlight`` / ``meta``).

    Args:
        text: Input string (plaintext for encrypt, ciphertext for decrypt).
        key: Shift amount; normalised with ``% 26`` (default 3, the
            historic classic). ``extra`` is accepted for the uniform
            ``simulate(text, key, mode, extra)`` contract but ignored.
        mode: ``"encrypt"`` shifts forward, ``"decrypt"`` shifts back.
        extra: Unused (contract compatibility).

    Returns:
        Tuple ``(result, steps)`` where ``result`` is the transformed
        string and ``steps`` is the trace (``len(text) + 2`` entries).

    Example:
        >>> simulate("Hello", 3, "encrypt")[0]
        'Khoor'
    """
    shift = int(key or 0) % 26
    if mode == "decrypt":
        shift = (-shift) % 26

    steps = []
    current = []

    steps.append(
        {
            "index": 0,
            "title": {"ar": "الإعداد الأولي", "en": "Setup"},
            "description": {
                "ar": f"النص المدخل: '{text}' | المفتاح: {key} | الإزاحة الفعلية: {shift} | الوضع: {mode}",
                "en": f"Input: '{text}' | Key: {key} | Effective shift: {shift} | Mode: {mode}",
            },
            "snapshot": {"current_text": "", "key": key, "shift": shift, "mode": mode},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    )

    for i, ch in enumerate(text):
        new_ch = _shift_char(ch, shift)
        current.append(new_ch)
        is_alpha = ch.isalpha()
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"معالجة الحرف {i + 1}", "en": f"Process char {i + 1}"},
                "description": {
                    "ar": (
                        f"'{ch}' → '{new_ch}'"
                        + (
                            f" (إزاحة {shift} داخل الأبجدية)"
                            if is_alpha
                            else " (ليس حرفاً — يُترك كما هو)"
                        )
                    ),
                    "en": (
                        f"'{ch}' → '{new_ch}'"
                        + (
                            f" (shift {shift} within alphabet)"
                            if is_alpha
                            else " (not a letter — unchanged)"
                        )
                    ),
                },
                "snapshot": {
                    "current_text": "".join(current),
                    "position": i,
                    "char_in": ch,
                    "char_out": new_ch,
                },
                "highlight": [i],
                "meta": {"phase": "transform", "position": i},
            }
        )

    result = "".join(current)
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "النتيجة النهائية", "en": "Final result"},
            "description": {
                "ar": f"'{text}' → '{result}'",
                "en": f"'{text}' → '{result}'",
            },
            "snapshot": {"current_text": result, "result": result},
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return result, steps


def analyze(extra=None):
    """Return the static security review for Caesar (educational).

    Args:
        extra: Optional dict; reads ``extra["key"]`` so the metrics
            echo the effective shift (defaults to 3).

    Returns:
        ``{strengths{ar,en}, weaknesses{ar,en}, metrics{keyspace, key},
        complexity}`` — the keyspace is always 25, the core lesson.
    """
    key = int((extra or {}).get("key", 3))
    return {
        "strengths": {
            "ar": ["بسيط وسريع ومناسب للتعليم"],
            "en": ["Simple, fast, good for teaching"],
        },
        "weaknesses": {
            "ar": [
                "مساحة مفاتيح صغيرة (25 فقط) — يُكسر بالقوة الغاشمة بسهولة",
                "ضعيف أمام تحليل التكرار",
                "لا يصلح لأي استخدام حقيقي",
            ],
            "en": [
                "Tiny keyspace (25) — trivially brute-forced",
                "Vulnerable to frequency analysis",
                "Not suitable for real use",
            ],
        },
        "metrics": {"keyspace": 25, "key": key % 26},
        "complexity": COMPLEXITY,
    }


# Self-registration: makes "caesar" visible to the dispatcher, the
# /api/algorithms catalog and the contract guard tests — no other file
# needs editing when this module changes.
register(
    "caesar",
    type="encryption",
    name={"ar": "قيصر", "en": "Caesar"},
    description={
        "ar": "تشفير إبدالي بسيط بإزاحة ثابتة — تعليمي فقط",
        "en": "Simple substitution cipher with fixed shift — educational only",
    },
    params=["key", "mode"],
    keyspace=25,
    order=10,
)

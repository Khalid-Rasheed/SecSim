"""Brute-force attack on Caesar: try all 25 shifts, rank by chi-squared.

Chi-squared against English letter frequencies — works best on
English text of reasonable length. Demonstrates why a keyspace
of 25 offers zero real security.

Ranking strategy (see :func:`_score`): dictionary hits dominate so
short texts like ``"Khoor Zruog"`` still resolve, chi-squared breaks
ties on longer prose. Non-English input never crashes — it simply
scores ``inf`` on the English statistics and degrades gracefully.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"brute_force"`` at the bottom
of this file (see :mod:`app.services.registry`).
"""
from algorithms.encryption.caesar import _shift_char

from app.services.registry import register

COMPLEXITY = {
    "time": "O(25 · n)",
    "space": "O(n)",
    "n": {"ar": "طول النص المشفر", "en": "ciphertext length"},
    "note": {
        "ar": "25 تمريرة كاملة على النص — الثابت 25 صغير لدرجة أن الهجوم فوري؛ في التشفير الحقيقي الثابت فلكي",
        "en": "25 full passes over the text — the constant 25 is so small the attack is instant; in real ciphers it is astronomical",
    },
}

DETAILS = {
    "overview": {
        "ar": "أبسط الهجمات وأصدقها: تجربة كل المفاتيح الممكنة واحداً واحداً حتى ينكشف النص. لا ذكاء فيه، لكنه ينجح دائماً إن كانت مساحة المفاتيح صغيرة — وقيصر بمساحته (25) هو الضحية المثالية.",
        "en": "The simplest, most honest attack: trying every possible key one by one until the text reveals itself. No cleverness — yet it always wins when the keyspace is small, and Caesar with 25 keys is the perfect victim.",
    },
    "history": {
        "ar": "فكرة قديمة قِدم الشيفرات، لكن لحظتها الأشهر كانت 1998 حين بنت مؤسسة EFF آلة Deep Crack التي كسرت DES (72 كوادرليون مفتاح) خلال أيام — فدُفن DES رسمياً ومهد الطريق لـ AES.",
        "en": "As old as ciphers themselves, but its most famous moment was 1998, when the EFF built Deep Crack, breaking DES (72 quadrillion keys) in days — burying DES and paving the way for AES.",
    },
    "how_it_works": {
        "ar": [
            "فك النص المشفر بكل مفتاح من 1 إلى 25 (25 مرشحاً).",
            "قيّم كل مرشح إحصائياً: مطابقة كلمات إنجليزية شائعة أولاً ثم اختبار مربع-كاي لتوزيع الحروف.",
            "رتّب المرشحين — الأقل درجة هو الأقرب للنص الحقيقي.",
            "أعلن المفتاح الفائز والنص المستعاد (جرّب: Khoor Zruog ← Hello World بالمفتاح 3).",
        ],
        "en": [
            "Decrypt the ciphertext with every key 1–25 (25 candidates).",
            "Score each statistically: common-English-word matches first, then chi-squared letter distribution.",
            "Rank candidates — the lowest score is closest to real text.",
            "Declare the winning key and recovered text (try: Khoor Zruog → Hello World with key 3).",
        ],
    },
    "parameters": {
        "ar": [{"name": "input", "desc": "نص مشفر بقيصر (إنجليزي بطول معقول لأدق نتيجة)."}],
        "en": [{"name": "input", "desc": "Caesar ciphertext (reasonably long English for best accuracy)."}],
    },
    "security": {
        "ar": "الدرس المركزي في علم التشفير: الأمان = مساحة مفاتيح هائلة. 25 مفتاحاً تُكسر فوراً، و2^128 (كـ AES) تحتاج طاقة تفوق ما في الكون المنظور. ومبدأ كيركهوفس: افترض أن المهاجم يعرف كل شيء عدا المفتاح.",
        "en": "Cryptography's central lesson: security = an enormous keyspace. 25 keys fall instantly, while 2^128 (like AES) needs more energy than the observable universe holds. And Kerckhoffs's principle: assume the attacker knows everything except the key.",
    },
    "uses": {
        "ar": ["تدقيق الشيفرات الضعيفة", "عروض CTF ومسابقات الاختراق", "كسر كلمات المرور الضعيفة (بأدوات مخصصة)", "إثبات الحاجة لمساحات مفاتيح كبيرة"],
        "en": ["Auditing weak ciphers", "CTF and hacking competitions", "Weak-password cracking (with dedicated tools)", "Proving the need for huge keyspaces"],
    },
}

# Standard English letter frequencies in percent, a-z order
# (source: classical cryptanalysis tables). Index i ↔ chr(ord('a')+i).
ENGLISH_FREQ = [
    8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966,
    0.153, 0.772, 4.025, 2.406, 6.749, 7.507, 1.929, 0.095, 5.987,
    6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074,
]


def _chi_squared(text: str) -> float:
    # Count ASCII a-z only: other alphabets (e.g. Arabic) must not
    # index into the 26-slot English frequency table.
    letters = [c for c in text.lower() if "a" <= c <= "z"]
    if not letters:
        return float("inf")
    n = len(letters)
    counts = [0] * 26
    for c in letters:
        counts[ord(c) - ord("a")] += 1
    return sum((counts[i] - n * f / 100) ** 2 / (n * f / 100) for i, f in enumerate(ENGLISH_FREQ))


COMMON_WORDS = {
    "the", "and", "hello", "world", "quick", "brown", "fox", "jumps",
    "over", "lazy", "dog", "this", "that", "with", "from", "have",
    "security", "attack", "cipher", "key", "test", "message", "is", "it",
}


def _score(text: str) -> float:
    """Dictionary hits dominate (robust on short text), chi-squared breaks ties."""
    words = [w.strip(".,!?").lower() for w in text.split()]
    hits = sum(1 for w in words if w in COMMON_WORDS)
    return _chi_squared(text) - hits * 500


def _word_hits(text: str) -> int:
    """Count common-English-word hits (used for the plaintext warning)."""
    words = [w.strip(".,!?").lower() for w in text.split()]
    return sum(1 for w in words if w in COMMON_WORDS)


def _input_warning(ciphertext: str):
    """Advise when the input is unlikely to be Caesar ciphertext.

    The ranking is English-only statistics, so three input problems
    make the "recovered" result misleading rather than wrong-crashing:
    empty input, (almost) no English letters, too-short text, or text
    that already reads as plain English (≥2 dictionary hits — real
    ciphertext almost never contains two English words by chance).

    Args:
        ciphertext: Raw user input.

    Returns:
        Bilingual ``{"ar": ..., "en": ...}`` warning dict, or ``None``
        when the input looks like attackable ciphertext.
    """
    if not ciphertext.strip():
        return {
            "ar": "الدخل فارغ — أدخل نصاً مشفراً بقيصر (إنجليزي) لتجربة الهجوم.",
            "en": "Input is empty — enter English Caesar ciphertext to attack.",
        }
    ascii_letters = [c for c in ciphertext.lower() if "a" <= c <= "z"]
    if not ascii_letters:
        return {
            "ar": "تنبيه: لا توجد حروف إنجليزية — الترتيب الإحصائي مصمم للإنجليزية فقط، والنتيجة المعروضة غير موثوقة.",
            "en": "Warning: no English letters found — ranking is English-only statistics, so the shown result is unreliable.",
        }
    if len(ascii_letters) < 4:
        return {
            "ar": "تنبيه: النص قصير جداً — الترتيب الإحصائي يحتاج نصاً أطول (4+ حروف) ليكون دقيقاً.",
            "en": "Warning: text is too short — statistical ranking needs 4+ letters to be accurate.",
        }
    if _word_hits(ciphertext) >= 2:
        return {
            "ar": "تنبيه: الدخل يبدو نصاً إنجليزياً صريحاً — الهجوم مخصص للنص المشفر، والنتيجة «المستعادة» قد تكون مضللة.",
            "en": "Warning: input already reads as plain English — this attack targets ciphertext, so the 'recovered' result may mislead.",
        }
    return None


def simulate(ciphertext: str, key=3, mode: str = "encrypt", extra=None):
    ciphertext = ciphertext or ""
    warning = _input_warning(ciphertext)
    steps = [
        {
            "index": 0,
            "title": {"ar": "بدء الهجوم الغاشم", "en": "Starting brute force"},
            "description": {
                "ar": f"مساحة مفاتيح قيصر = 25 فقط. سنجربها كلها على: '{ciphertext}' (الترتيب إحصائي للإنجليزية فقط)",
                "en": f"Caesar keyspace is only 25. Trying all on: '{ciphertext}' (English-only statistical ranking)",
            },
            "snapshot": {"ciphertext": ciphertext, "keyspace": 25, "ranking": "english-only"},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    ]
    attempts = []
    for key in range(1, 26):
        plain = "".join(_shift_char(c, (-key) % 26) for c in ciphertext)
        score = _score(plain)
        attempts.append({"key": key, "plain": plain, "score": round(score, 2)})
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"تجربة المفتاح {key}", "en": f"Try key {key}"},
                "description": {
                    "ar": f"المفتاح {key} ← '{plain}' (درجة {score:.1f} — الأقل أفضل)",
                    "en": f"Key {key} → '{plain}' (score {score:.1f} — lower is better)",
                },
                "snapshot": {"key": key, "plain": plain, "score": round(score, 2)},
                "highlight": [key],
                "meta": {"phase": "attempt", "key": key},
            }
        )
    best = min(attempts, key=lambda a: a["score"])
    # Surface the input warning (if any) on the verdict step so the UI
    # can banner it next to the headline result. `None` serialises to
    # JSON null — the frontend treats null as "no warning".
    final_snapshot = {"best_key": best["key"], "plaintext": best["plain"], "attempts": attempts}
    if warning is not None:
        final_snapshot["warning"] = warning
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "المفتاح المكتشف", "en": "Key recovered"},
            "description": {
                "ar": f"أفضل نتيجة: المفتاح {best['key']} ← '{best['plain']}'",
                "en": f"Best match: key {best['key']} → '{best['plain']}'",
            },
            "snapshot": final_snapshot,
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return best["plain"], steps


def analyze(extra=None):
    return {
        "strengths": {
            "ar": ["القسوة الغاشمة تنجح دائماً مع مساحة مفاتيح صغيرة"],
            "en": ["Brute force always wins against tiny keyspaces"],
        },
        "weaknesses": {
            "ar": ["الترتيب الإحصائي قد يخطئ مع النصوص القصيرة أو غير الإنجليزية"],
            "en": ["Statistical ranking can miss on short or non-English text"],
        },
        "metrics": {"keyspace": 25, "attempts": 25},
        "complexity": COMPLEXITY,
    }


register(
    "brute_force",
    type="attack",
    name={"ar": "القوة الغاشمة", "en": "Brute Force"},
    description={
        "ar": "هجوم يجرب مفاتيح قيصر الـ 25 على نص مشفر",
        "en": "Attack trying all 25 Caesar keys on ciphertext",
    },
    params=[],
    keyspace=25,
    order=60,
)

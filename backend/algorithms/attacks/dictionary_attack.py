"""Dictionary attack on unsalted fast hashes (MD5), salt lesson included.

Phase 1 tries a built-in 30-word list (common English + Arabic
passwords) against the target MD5 digest — one hash compare per word.
Phase 2 always runs the salt lesson: the same word under two fresh
random salts derives two different PBKDF2 keys, proving rainbow tables
useless and per-guess cost real.

Input is the target: a 32-hex MD5 digest, or any other text (then its
MD5 becomes the target — noted honestly in the setup step so the demo
never crashes on free typing). Result is the cracked word, or the
target digest back with a bilingual warning when nothing matches.

Failure message (per user decision): states explicitly that real
dictionaries hold millions of words plus mutation rules, and that
salt + slow KDFs are the defense — the 30-word list is the demo's
honest limit, not the attacker's.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"dictionary_attack"``.
"""

import hashlib
import os
import re

from app.services.registry import register

COMPLEXITY = {
    "time": "O(W)",
    "space": "O(1)",
    "n": {"ar": "حجم قائمة الكلمات W (هنا 30)", "en": "wordlist size W (here 30)"},
    "note": {
        "ar": "محاولة واحدة رخيصة لكل كلمة ضد الهاش السريع — لهذا تموت كلمات القواميس في أجزاء من الثانية",
        "en": "One cheap try per word against the fast hash — why dictionary words die in fractions of a second",
    },
}

DETAILS = {
    "overview": {
        "ar": "هجوم القاموس: بدل تجربة كل المفاتيح، جرّب كلمات البشر المرجحة (password و123456 وأخواتها) على الهاش السريع غير المملّح. ينجح لأن البشر يختارون كلمات متوقعة — ثم يُظهر درس الملح لماذا يفشل نفس الهجوم ضد التخزين الصحيح.",
        "en": "Dictionary attack: instead of every key, try humans' likely words (password, 123456 and family) against the fast unsalted hash. It wins because humans pick predictable words — then the salt lesson shows why the same attack fails against proper storage.",
    },
    "history": {
        "ar": "منذ يونكس الأولى (crypt ثم MD5) سقطت كلمات المرور الضعيفة بهذه الطريقة، واليوم أدوات مثل John the Ripper وhashcat تجرب مليارات التخمينات بقواميس ضخمة وقواعد تشويه — والرد الوحيد الموثوق: ملح فريد + اشتقاق بطيء.",
        "en": "Since early Unix (crypt, then MD5), weak passwords fell exactly this way; today John the Ripper and hashcat try billions of guesses with huge dictionaries and mangling rules — and the only reliable answer is unique salt + slow derivation.",
    },
    "how_it_works": {
        "ar": [
            "الهدف: بصمة MD5 (32 خانة) — أو أي نص فيُشتق هدفه تلقائياً.",
            "جرّب كلمات القائمة الـ 30 واحدة واحدة: MD5(كلمة) == الهدف؟",
            "عند التطابق: الكلمة مكشوفة — اعرضها مع رقم المحاولة.",
            "درس الملح دائماً: نفس الكلمة بملحين عشوائيين تعطي مشتقين مختلفين (PBKDF2) — فلا جداول قوس قزح ولا مقارنة مباشرة.",
        ],
        "en": [
            "Target: an MD5 digest (32 hex chars) — or any text, whose digest becomes the target.",
            "Try the 30 list words one by one: MD5(word) == target?",
            "On match: the word is exposed — show it with its attempt number.",
            "Salt lesson always: the same word under two random salts derives two different keys (PBKDF2) — no rainbow tables, no direct compare.",
        ],
    },
    "parameters": {
        "ar": [{"name": "input", "desc": "بصمة MD5 الهدف — أو أي نص ليُستخدم هاشه هدفاً (مثال جاهز: زر المثال)."}],
        "en": [{"name": "input", "desc": "Target MD5 digest — or any text whose hash becomes the target (preset: example button)."}],
    },
    "security": {
        "ar": "الخلاصة العملية: لا تخزن بهاش سريع غير مملّح أبداً (MD5/SHA وحدهما = هدية للمهاجم)، واستخدم ملحاً فريداً + Argon2/PBKDF2 بتكرارات عالية، واختر عبارة مرور طويلة خارج كل قاموس.",
        "en": "The practical takeaway: never store a fast unsalted hash (raw MD5/SHA is a gift to attackers); use unique salt + Argon2/PBKDF2 with high iterations, and pick a long passphrase outside every dictionary.",
    },
    "uses": {
        "ar": [
            "تدقيق سياسات كلمات المرور",
            "فهم جداول قوس قزح والملح",
            "عروض CTF على الهاشات المسربة",
        ],
        "en": [
            "Auditing password policies",
            "Understanding rainbow tables and salt",
            "CTF demonstrations on leaked hashes",
        ],
    },
}

# Built-in demo wordlist: 25 common English passwords + 5 common Arabic
# words. Deliberately small (user decision): real attacker dictionaries
# hold millions of entries plus mutation rules — the failure verdict
# says so explicitly.
WORDLIST = [
    "password", "123456", "123456789", "qwerty", "abc123",
    "password1", "12345678", "111111", "123123", "admin",
    "letmein", "welcome", "monkey", "dragon", "sunshine",
    "princess", "football", "iloveyou", "hunter", "trustno1",
    "login", "master", "shadow", "michael", "superman",
    "حب", "سلام", "نور", "قمر", "12345",
]

_MD5_RE = re.compile(r"^[0-9a-fA-F]{32}$")


def _target_of(text: str) -> tuple[str, bool]:
    """Return (target_digest, was_direct_hex)."""
    stripped = (text or "").strip()
    if _MD5_RE.match(stripped):
        return stripped.lower(), True
    return hashlib.md5(stripped.encode("utf-8")).hexdigest(), False


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    target, direct = _target_of(text or "")
    steps = [
        {
            "index": 0,
            "title": {"ar": "الهدف والقائمة", "en": "Target & wordlist"},
            "description": {
                "ar": (
                    f"الهدف MD5: {target} (مُدخل مباشرة)"
                    if direct else
                    f"الدخل ليس بصمة — الهدف هو MD5('{text}') = {target}"
                ) + f" | القائمة: {len(WORDLIST)} كلمة",
                "en": (
                    f"Target MD5: {target} (pasted directly)"
                    if direct else
                    f"Input is not a digest — target is MD5('{text}') = {target}"
                ) + f" | Wordlist: {len(WORDLIST)} words",
            },
            "snapshot": {"target": target, "direct_hex": direct, "wordlist_size": len(WORDLIST)},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    ]
    cracked: str | None = None
    for i, word in enumerate(WORDLIST):
        digest = hashlib.md5(word.encode("utf-8")).hexdigest()
        hit = digest == target
        if hit:
            cracked = word
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"تجربة {i + 1}: '{word}'", "en": f"Try {i + 1}: '{word}'"},
                "description": {
                    "ar": f"MD5('{word}') = {digest[:16]}... {'← تطابق!' if hit else '≠ الهدف'}",
                    "en": f"MD5('{word}') = {digest[:16]}... {'← MATCH!' if hit else '≠ target'}",
                },
                "snapshot": {"attempt": i + 1, "word": word, "match": hit},
                "highlight": [i % 8],
                "meta": {"phase": "attempt", "attempt": i + 1},
            }
        )
        if hit:
            break

    # Phase 2 (always): the salt lesson on the cracked word — or the
    # first word when nothing matched — under two fresh random salts.
    lesson_word = cracked or WORDLIST[0]
    salt_a, salt_b = os.urandom(16), os.urandom(16)
    dk_a = hashlib.pbkdf2_hmac("sha256", lesson_word.encode("utf-8"), salt_a, 1000, dklen=32)
    dk_b = hashlib.pbkdf2_hmac("sha256", lesson_word.encode("utf-8"), salt_b, 1000, dklen=32)
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "درس الملح", "en": "Salt lesson"},
            "description": {
                "ar": f"نفس الكلمة '{lesson_word}' بملحين عشوائيين ← مشتقان مختلفان ({dk_a.hex()[:12]}... ≠ {dk_b.hex()[:12]}...) — فلا مقارنة مباشرة ولا جداول قوس قزح",
                "en": f"Same word '{lesson_word}' under two random salts → two different keys ({dk_a.hex()[:12]}... ≠ {dk_b.hex()[:12]}...) — no direct compare, no rainbow tables",
            },
            "snapshot": {"word": lesson_word, "salt_a": salt_a.hex(), "salt_b": salt_b.hex(),
                         "same": dk_a == dk_b},
            "highlight": [],
            "meta": {"phase": "salt"},
        }
    )

    if cracked is not None:
        final_snapshot: dict = {"cracked": True, "word": cracked, "result": cracked}
    else:
        failure = {
            "ar": "لم تُكسر: الكلمة خارج قائمة الـ 30. تنبيه صريح — قواميس المهاجمين الحقيقية تحوي ملايين الكلمات وقواعد تشويه (John/Hashcat)، والحماية الوحيدة الموثوقة: ملح فريد + اشتقاق بطيء (Argon2/PBKDF2) + عبارة مرور طويلة.",
            "en": "Not cracked: the word is outside the 30-word list. Explicit notice — real attacker dictionaries hold millions of words plus mangling rules (John/Hashcat), and the only reliable defense is unique salt + slow derivation (Argon2/PBKDF2) + a long passphrase.",
        }
        final_snapshot = {"cracked": False, "warning": failure, "result": target}
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "الحكم النهائي", "en": "Final verdict"},
            "description": {
                "ar": f"الكلمة المكشوفة: '{cracked}'" if cracked else f"الهدف {target[:16]}... صمد أمام القائمة",
                "en": f"Cracked word: '{cracked}'" if cracked else f"Target {target[:16]}... survived the list",
            },
            "snapshot": final_snapshot,
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return (cracked if cracked is not None else target), steps


def analyze(extra=None):
    return {
        "strengths": {
            "ar": ["قاتل ضد الهاش السريع غير المملّح — الكلمات الشائعة تسقط فوراً", "رخيص: تجربة واحدة لكل كلمة"],
            "en": ["Lethal vs fast unsalted hashes — common words fall instantly", "Cheap: one try per word"],
        },
        "weaknesses": {
            "ar": ["محدود بالقائمة (30 كلمة هنا؛ الملايين عند المهاجم الحقيقي)", "الملح الفريد + الاشتقاق البطيء يهزمانه"],
            "en": ["Limited to the list (30 words here; millions for a real attacker)", "Unique salt + slow derivation defeat it"],
        },
        "metrics": {"wordlist_size": len(WORDLIST)},
        "complexity": COMPLEXITY,
    }


register(
    "dictionary_attack",
    type="attack",
    family="attack",
    kind=None,
    security="educational",
    name={"ar": "هجوم القاموس", "en": "Dictionary Attack"},
    description={
        "ar": "قائمة 30 كلمة ضد MD5 غير المملّح + درس الملح",
        "en": "30-word list vs unsalted MD5 + the salt lesson",
    },
    params=[],
    keyspace=None,
    order=64,
)

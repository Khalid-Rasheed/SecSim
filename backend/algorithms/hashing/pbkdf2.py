"""PBKDF2 password hashing demo (salt + iterations, step trace).

Derives a 256-bit key via ``hashlib.pbkdf2_hmac("sha256", password,
salt, iterations)``. Shows WHY passwords need slow salted KDFs, not
fast hashes: same password + different salt → different output, and
iteration count scales attacker cost linearly.

Teaching demo (real systems: prefer Argon2id/scrypt/bcrypt; PBKDF2
with ≥210k iterations per OWASP 2023 is an acceptable fallback).

simulate(): ``text`` is the password; ``extra`` carries
``pbkdf2_salt`` (default "secsim-salt") and ``pbkdf2_iterations``
(default 1000 for instant demo — the UI warns it is NOT production).
Result is ``"salt_hex$iterations$derived_hex"``.
"""

import hashlib
import os

from app.services.registry import register

COMPLEXITY = {
    "time": "O(iterations)",
    "space": "O(1)",
    "n": {"ar": "عدد التكرارات", "en": "iteration count"},
    "note": {
        "ar": "التكلفة تتناسب طرداً مع التكرارات — البطء هنا مقصود لإرهاق المهاجم",
        "en": "Cost scales linearly with iterations — slowness here is deliberate to exhaust attackers",
    },
}

DETAILS = {
    "overview": {
        "ar": "PBKDF2: اشتقاق مفتاح من كلمة مرور بملح وتكرارات كثيرة (HMAC-SHA256). الملح العشوائي يهزم جداول قوس قزح، والتكرارات تجعل كل تخمين مكلفاً — عكس SHA-256 المباشر الذي يُجرَّب بمليارات/ثانية.",
        "en": "PBKDF2: password-based key derivation with salt and many iterations (HMAC-SHA256). Random salt defeats rainbow tables; iterations make each guess expensive — unlike raw SHA-256 at billions/sec.",
    },
    "history": {
        "ar": "معيار RSA Labs (PKCS#5/RFC 2898 سنة 2000). ما زال مقبولاً بديلاً عند غياب Argon2 (توصية OWASP: 210k+ تكرار لـ SHA-256). العرض يستخدم 1000 فقط للسرعة — والواجهة تحذر من ذلك.",
        "en": "RSA Labs standard (PKCS#5/RFC 2898, 2000). Still an acceptable fallback without Argon2 (OWASP: 210k+ SHA-256 iterations). This demo uses 1000 for speed — the UI warns it is NOT production.",
    },
    "how_it_works": {
        "ar": [
            "ولّد ملحاً عشوائياً (16 بايت) — يُخزَّن مكشوفاً بجانب الناتج.",
            "كرر HMAC-SHA256 (كلمة+ملح) بعدد التكرارات مع خلط.",
            "أخرج مشتقاً 256-بت بصيغة salt$iterations$hash.",
            "للتحقق: أعد الحساب بنفس الملح والتكرارات وقارن بثبات زمني.",
        ],
        "en": [
            "Generate a random salt (16 bytes) — stored openly next to the output.",
            "Iterate HMAC-SHA256(password+salt) with mixing, N times.",
            "Output 256-bit derived key as salt$iterations$hash.",
            "To verify: recompute with same salt/iterations, compare in constant time.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "pbkdf2_salt", "desc": "الملح (اتركه فارغاً لتوليد عشوائي — الأفضل)."},
            {"name": "pbkdf2_iterations", "desc": "التكرارات (1000 للعرض؛ الإنتاج 210k+)."},
        ],
        "en": [
            {"name": "pbkdf2_salt", "desc": "Salt (leave empty for random — best)."},
            {"name": "pbkdf2_iterations", "desc": "Iterations (1000 demo; production 210k+)."},
        ],
    },
    "security": {
        "ar": "آمن إذا: ملح عشوائي فريد + تكرارات عالية + SHA-256. الأفضل حديثاً Argon2id (مقاوم للذاكرة). الممنوع: SHA/MD5 مباشر، ملح ثابت، تكرارات قليلة.",
        "en": "Secure if: unique random salt + high iterations + SHA-256. Modern best is Argon2id (memory-hard). Forbidden: raw SHA/MD5, fixed salt, low iterations.",
    },
    "uses": {
        "ar": ["تخزين كلمات المرور", "اشتقاق مفاتيح من عبارات", "حماية النسخ الاحتياطية"],
        "en": ["Password storage", "Key derivation from passphrases", "Backup encryption"],
    },
}


def _params(extra: dict):
    extra = extra or {}
    salt_text = str(extra.get("pbkdf2_salt", "") or "")
    try:
        iterations = int(extra.get("pbkdf2_iterations", 1000))
    except (TypeError, ValueError):
        raise ValueError("pbkdf2_iterations must be an integer")
    if not 1 <= iterations <= 2_000_000:
        raise ValueError("pbkdf2_iterations must be within 1..2000000")
    salt = salt_text.encode("utf-8") if salt_text else os.urandom(16)
    return salt, iterations


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    salt, iterations = _params(extra or {})
    password = (text or "").encode("utf-8")
    steps = [
        {
            "index": 0,
            "title": {"ar": "الملح والتكرارات", "en": "Salt & iterations"},
            "description": {
                "ar": f"الملح: {salt.hex()[:24]}... ({len(salt)} بايت) | التكرارات: {iterations}",
                "en": f"Salt: {salt.hex()[:24]}... ({len(salt)} bytes) | Iterations: {iterations}",
            },
            "snapshot": {"salt_hex": salt.hex(), "iterations": iterations,
                         "password_len": len(password)},
            "highlight": [],
            "meta": {"phase": "setup"},
        },
        {
            "index": 1,
            "title": {"ar": "الاشتقاق التكراري", "en": "Iterative derivation"},
            "description": {
                "ar": f"تكرار HMAC-SHA256 عدد {iterations} مرة — كل تخمين للمهاجم يكلف نفس القدر",
                "en": f"Iterate HMAC-SHA256 {iterations} times — each attacker guess costs the same",
            },
            "snapshot": {"algorithm": "PBKDF2-HMAC-SHA256", "iterations": iterations},
            "highlight": [],
            "meta": {"phase": "derive"},
        },
    ]
    dk = hashlib.pbkdf2_hmac("sha256", password, salt, iterations, dklen=32)
    result = f"{salt.hex()}${iterations}${dk.hex()}"
    warn = None
    if iterations < 100_000:
        warn = {
            "ar": "تنبيه تعليمي: التكرارات منخفضة للعرض السريع — الإنتاج يحتاج 210k+ (OWASP).",
            "en": "Teaching note: iterations are low for a fast demo — production needs 210k+ (OWASP).",
        }
    final_snapshot: dict = {"derived_hex": dk.hex(), "bits": 256, "result": result}
    if warn:
        final_snapshot["warning"] = warn
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "المفتاح المشتق", "en": "Derived key"},
            "description": {
                "ar": f"الناتج 256-بت: {dk.hex()[:32]}...",
                "en": f"256-bit output: {dk.hex()[:32]}...",
            },
            "snapshot": final_snapshot,
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return result, steps


def analyze(extra=None):
    extra = extra or {}
    try:
        iterations = int(extra.get("pbkdf2_iterations", 1000))
    except (TypeError, ValueError):
        iterations = 1000
    return {
        "strengths": {
            "ar": ["الملح يهزم جداول قوس قزح", "التكرارات تُبطئ التخمين خطياً"],
            "en": ["Salt defeats rainbow tables", "Iterations slow guessing linearly"],
        },
        "weaknesses": {
            "ar": [
                "يحتاج 210k+ تكرار للإنتاج (العرض 1000 فقط)",
                "Argon2id أفضل (مقاوم للذاكرة/GPU)",
                "لا يحمي كلمة ضعيفة مُعاد استخدامها",
            ],
            "en": [
                "Needs 210k+ iterations in production (demo uses 1000)",
                "Argon2id is better (memory-hard vs GPUs)",
                "Cannot save a weak reused password",
            ],
        },
        "metrics": {"iterations": iterations, "dk_bits": 256,
                    "owasp_minimum": 210000},
        "complexity": COMPLEXITY,
    }


register(
    "pbkdf2",
    type="hashing",
    family="hashing",
    kind="password",
    security="secure",
    name={"ar": "PBKDF2", "en": "PBKDF2"},
    description={
        "ar": "اشتقاق آمن لكلمات المرور (ملح + تكرارات)",
        "en": "Secure password derivation (salt + iterations)",
    },
    params=["pbkdf2_salt", "pbkdf2_iterations"],
    keyspace=None,
    order=48,
)

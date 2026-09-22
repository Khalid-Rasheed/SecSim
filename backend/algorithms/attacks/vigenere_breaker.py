"""Kasiski breaker for Vigenère: find the key length, then break columns.

Pipeline (all computed live on the input):
  setup → Kasiski examination (repeated trigrams → distances → GCD
  votes) → index of coincidence per candidate length 2..12 →
  per-column Caesar break via chi-squared → recovered key + plaintext.

Needs reasonably long English ciphertext (40+ letters); short or
non-English input yields a bilingual warning and a best-effort guess
instead of a crash — same honesty pattern as ``brute_force``.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"vigenere_breaker"``.
"""

from math import gcd
from functools import reduce

from algorithms.attacks.brute_force import _chi_squared
from algorithms.encryption.caesar import _shift_char
from app.services.registry import register

COMPLEXITY = {
    "time": "O(12 · (n + 26 · n))",
    "space": "O(n)",
    "n": {"ar": "طول النص المشفر", "en": "ciphertext length"},
    "note": {
        "ar": "فحص 11 طولاً مرشحاً ثم 26 تجربة لكل عمود — كثير حسابياً لكنه تافه للحاسوب؛ القوة هنا في الرياضيات لا في السرعة",
        "en": "11 candidate lengths then 26 trials per column — heavy arithmetically yet trivial for a computer; the power is in the math, not the speed",
    },
}

DETAILS = {
    "overview": {
        "ar": "الكاسر الذي أسقط «الشيفرة المستحيلة»: أولاً اكتشف طول المفتاح من التكرارات (كاسيسكي) ومعامل التطابق، ثم اكسر كل عمود كقيصر مستقل. لحظة اكتشاف الطول هي لحظة موت فيجينير.",
        "en": "The breaker that felled 'le chiffre indéchiffrable': first recover the key length from repeats (Kasiski) and the index of coincidence, then break each column as independent Caesar. The moment the length leaks, Vigenère dies.",
    },
    "history": {
        "ar": "نشر فريدريش كاسيسكي الطريقة سنة 1863 (وسبقه باباج سراً). كانت أول كسر منهجي لشيفرة متعددة الأبجدية، وفتحت عصر تحليل الشيفرات الحديث.",
        "en": "Friedrich Kasiski published the method in 1863 (Babbage beat him to it in secret). It was the first systematic break of a polyalphabetic cipher and opened modern cryptanalysis.",
    },
    "how_it_works": {
        "ar": [
            "ابحث عن مقاطع ثلاثية متكررة وسجّل المسافات بين تكراراتها — المسافة مضاعف لطول المفتاح غالباً.",
            "خذ القاسم المشترك الأكبر للمسافات (أصوات مرشحة للطول) واحسب معامل التطابق لكل طول 2..12 (الإنجليزية ≈ 0.065 والعشوائي ≈ 0.038).",
            "قسّم النص إلى أعمدة حسب الطول الفائز واكسر كل عمود بمربع-كاي كقيصر مستقل.",
            "اجمع مفاتيح الأعمدة مفتاحاً واحداً وفك النص كاملاً.",
        ],
        "en": [
            "Find repeated trigrams and record the distances between repeats — each distance is usually a multiple of the key length.",
            "Take the GCD of distances (length votes) and score the index of coincidence for each length 2..12 (English ≈ 0.065, random ≈ 0.038).",
            "Split the text into columns by the winning length and break each column with chi-squared as independent Caesar.",
            "Join the column keys into one keyword and decrypt the whole text.",
        ],
    },
    "parameters": {
        "ar": [{"name": "input", "desc": "نص مشفر بفيجينير (إنجليزي طويل — 40+ حرفاً لأدق نتيجة)."}],
        "en": [{"name": "input", "desc": "Vigenère ciphertext (long English — 40+ letters for best accuracy)."}],
    },
    "security": {
        "ar": "الدرس: طول المفتاح معلومات تتسرب. أي تكرار دوري (مفتاح يُعاد) يكشفه تحليل كاسيسكي. العلاج الحديث: مفاتيح بطول النص تُستخدم مرة واحدة (OTP) أو مفاتيح جلسات عشوائية.",
        "en": "The lesson: key length is leaking information. Any periodic repetition (a reused key) exposes it to Kasiski analysis. The modern cure: one-time keys as long as the message (OTP) or random session keys.",
    },
    "uses": {
        "ar": [
            "تدريس تحليل الشيفرات الكلاسيكي",
            "عروض CTF على فيجينير",
            "فهم معامل التطابق إحصائياً",
        ],
        "en": [
            "Teaching classical cryptanalysis",
            "CTF demonstrations on Vigenère",
            "Understanding the index of coincidence statistically",
        ],
    },
}

_MAX_LENGTH = 12
_MIN_LETTERS_WARN = 40


def _clean(text: str) -> str:
    return "".join(c for c in text.upper() if "A" <= c <= "Z")


def _kasiski_votes(clean: str) -> dict[int, int]:
    """Map trigram-repeat distances to GCD vote counts."""
    positions: dict[str, list[int]] = {}
    for i in range(len(clean) - 2):
        tri = clean[i:i + 3]
        positions.setdefault(tri, []).append(i)
    votes: dict[int, int] = {}
    for occ in positions.values():
        if len(occ) < 2:
            continue
        dists = [b - a for a, b in zip(occ, occ[1:])]
        g = reduce(gcd, dists)
        for d in range(2, min(g, 30) + 1):
            if g % d == 0:
                votes[d] = votes.get(d, 0) + 1
    return votes


def _index_of_coincidence(column: str) -> float:
    n = len(column)
    if n < 2:
        return 0.0
    counts = [0] * 26
    for c in column:
        counts[ord(c) - 65] += 1
    return sum(c * (c - 1) for c in counts) / (n * (n - 1))


def _avg_ic(clean: str, length: int) -> float:
    return sum(_index_of_coincidence(clean[i::length]) for i in range(length)) / length


def _break_column(column: str) -> int:
    """Best Caesar shift for one column (lowest chi-squared)."""
    best_k, best_score = 0, float("inf")
    for k in range(26):
        plain = "".join(_shift_char(c, (-k) % 26) for c in column)
        score = _chi_squared(plain)
        if score < best_score:
            best_k, best_score = k, score
    return best_k


def _input_warning(clean: str):
    if not clean:
        return {
            "ar": "الدخل فارغ — أدخل نصاً مشفراً بفيجينير (إنجليزي) لتجربة الكسر.",
            "en": "Input is empty — enter English Vigenère ciphertext to break.",
        }
    if len(clean) < _MIN_LETTERS_WARN:
        return {
            "ar": f"تنبيه: النص قصير ({len(clean)} حرفاً) — كاسيسكي يحتاج 40+ حرفاً، والنتيجة تخمين غير موثوق.",
            "en": f"Warning: short text ({len(clean)} letters) — Kasiski needs 40+ letters, so this is an unreliable guess.",
        }
    return None


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    clean = _clean(text or "")
    warning = _input_warning(clean)
    steps = [
        {
            "index": 0,
            "title": {"ar": "تنظيف الدخل", "en": "Clean input"},
            "description": {
                "ar": f"استخلاص الحروف اللاتينية: {len(clean)} حرفاً من '{(text or '')[:32]}...'",
                "en": f"Extract Latin letters: {len(clean)} letters from '{(text or '')[:32]}...'",
            },
            "snapshot": {"letters": len(clean)},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    ]
    if not clean:
        steps.append(
            {
                "index": 1,
                "title": {"ar": "تعذر الكسر", "en": "Cannot break"},
                "description": {"ar": "لا توجد حروف لاتينية للتحليل", "en": "No Latin letters to analyze"},
                "snapshot": {"result": "", "warning": warning},
                "highlight": [],
                "meta": {"phase": "done"},
            }
        )
        return "", steps

    # Phase 1: Kasiski votes.
    votes = _kasiski_votes(clean)
    top_votes = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "فحص كاسيسكي", "en": "Kasiski examination"},
            "description": {
                "ar": f"التكرارات الثلاثية صوّتت للأطوال: {top_votes or 'لا تكرارات كافية'}",
                "en": f"Trigram repeats voted for lengths: {top_votes or 'too few repeats'}",
            },
            "snapshot": {"votes": dict(top_votes)},
            "highlight": [],
            "meta": {"phase": "kasiski"},
        }
    )

    # Phase 2: index of coincidence for lengths 2..12.
    # Multiples of the true length also score high (their columns stay
    # monoalphabetic), so the winner is NOT simply argmax IC: take the
    # near-best plateau, prefer Kasiski-voted lengths, tie-break smallest.
    hi = min(_MAX_LENGTH, max(2, len(clean) // 4))
    ics = [(L, round(_avg_ic(clean, L), 4)) for L in range(2, hi + 1)]
    best_ic = max(score for _, score in ics)
    plateau = [L for L, score in ics if score >= best_ic - 0.008]
    voted = [(votes.get(L, 0), L) for L in plateau]
    best_length = sorted(voted, key=lambda t: (-t[0], t[1]))[0][1]
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "معامل التطابق", "en": "Index of coincidence"},
            "description": {
                "ar": f"أعلى IC عند الطول {best_length} (الإنجليزية ≈ 0.065، ومضاعفات الطول الحقيقي ترتفع أيضاً — لهذا ندمج أصوات كاسيسكي): {ics}",
                "en": f"Highest IC shortlist → length {best_length} (English ≈ 0.065; multiples of the true length also score high, hence Kasiski votes break the tie): {ics}",
            },
            "snapshot": {"ics": dict(ics), "guessed_length": best_length},
            "highlight": [],
            "meta": {"phase": "ic"},
        }
    )

    # Phase 3: break each column.
    key_shifts: list[int] = []
    for col in range(best_length):
        column = clean[col::best_length]
        k = _break_column(column)
        key_shifts.append(k)
        if col < 8:
            steps.append(
                {
                    "index": len(steps),
                    "title": {"ar": f"كسر العمود {col + 1}", "en": f"Break column {col + 1}"},
                    "description": {
                        "ar": f"أفضل إزاحة {k} ← حرف المفتاح '{chr(k + 65)}'",
                        "en": f"Best shift {k} → key letter '{chr(k + 65)}'",
                    },
                    "snapshot": {"column": col + 1, "shift": k, "key_char": chr(k + 65)},
                    "highlight": [col],
                    "meta": {"phase": "columns", "column": col},
                }
            )
    if best_length > 8:
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"... {best_length - 8} أعمدة أخرى", "en": f"... {best_length - 8} more columns"},
                "description": {"ar": "نفس الكسر بمربع-كاي لكل عمود", "en": "Same chi-squared break per column"},
                "snapshot": {"remaining": best_length - 8},
                "highlight": [],
                "meta": {"phase": "columns"},
            }
        )

    recovered_key = "".join(chr(k + 65) for k in key_shifts)
    plain_chars = []
    for i, c in enumerate(clean):
        plain_chars.append(_shift_char(c, (-key_shifts[i % best_length]) % 26))
    plaintext = "".join(plain_chars)
    final_snapshot: dict = {
        "guessed_length": best_length,
        "recovered_key": recovered_key,
        "plaintext": plaintext,
        "result": plaintext,
    }
    if warning is not None:
        final_snapshot["warning"] = warning
    steps.append(
        {
            "index": len(steps),
            "title": {"ar": "المفتاح والنص المستعادان", "en": "Key and plaintext recovered"},
            "description": {
                "ar": f"الطول {best_length} + المفتاح '{recovered_key}' ← '{plaintext[:64]}...'",
                "en": f"Length {best_length} + key '{recovered_key}' → '{plaintext[:64]}...'",
            },
            "snapshot": final_snapshot,
            "highlight": [],
            "meta": {"phase": "done"},
        }
    )
    return plaintext, steps


def analyze(extra=None):
    return {
        "strengths": {
            "ar": ["منهجي وحتمي: طول كافٍ من النص يكفي دائماً", "يكشف المفتاح والنص معاً"],
            "en": ["Systematic and deterministic: enough text always suffices", "Recovers key and plaintext together"],
        },
        "weaknesses": {
            "ar": ["يحتاج نصاً طويلاً (40+ حرفاً) — القصير يُضلل", "مفتاح بطول النص (OTP) يقاومه تماماً"],
            "en": ["Needs long text (40+ letters) — short text misleads", "A full-length one-time key resists it entirely"],
        },
        "metrics": {"max_tested_length": _MAX_LENGTH, "min_reliable_letters": _MIN_LETTERS_WARN},
        "complexity": COMPLEXITY,
    }


register(
    "vigenere_breaker",
    type="attack",
    family="attack",
    kind=None,
    security="educational",
    name={"ar": "كاسر فيجينير", "en": "Vigenère Breaker"},
    description={
        "ar": "كسر فيجينير بكاسيسكي ومعامل التطابق وأعمدة قيصر",
        "en": "Break Vigenère via Kasiski, IC and Caesar columns",
    },
    params=[],
    keyspace=None,
    order=61,
)

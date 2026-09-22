"""Playfair cipher with step-by-step trace (digraph substitution).

Encrypts letter PAIRS using a 5×5 key square (I/J merged, X filler):
same row → shift right, same column → shift down, rectangle → swap
columns. Non-Latin chars pass through unchanged.

Contract: exposes ``COMPLEXITY`` / ``DETAILS`` / ``simulate()`` /
``analyze()`` and self-registers as ``"playfair"``.
"""

from app.services.registry import register

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(n)",
    "n": {"ar": "عدد أحرف النص", "en": "number of text characters"},
    "note": {
        "ar": "عمل ثابت لكل زوج حروف (بحث في مربع 5×5) — خطي، لكن 26! من المربعات لا تنقذه من تحليل الثنائيات",
        "en": "Constant work per letter pair (5×5 square lookup) — linear, but 26! squares still fall to digraph analysis",
    },
}

DETAILS = {
    "overview": {
        "ar": "شيفرة بلاي فير: تشفر أزواج الحروف بمربع مفتاح 5×5 (تُدمج I مع J ويُستخدم X للفصل والحشو). تكسر التكرار أحادي الحروف الذي يقتل قيصر، لكنها تبقي بصمات الثنائيات.",
        "en": "The Playfair cipher encrypts letter pairs with a 5×5 key square (I/J merged, X for splitting and padding). It breaks the single-letter frequency that kills Caesar, but keeps digraph fingerprints.",
    },
    "history": {
        "ar": "اخترعها تشارلز ويتستون سنة 1854 وروّج لها اللورد بلاي فير، واستخدمها الجيش البريطاني في حرب البوير والحرب العالمية الأولى. كُسرت بتحليل تكرار الثنائيات (/pr/ و/th/ تفضح نفسها).",
        "en": "Invented by Charles Wheatstone in 1854, promoted by Lord Playfair, and used by the British Army in the Boer War and WWI. Broken via digraph frequency analysis (th/he reveal themselves).",
    },
    "how_it_works": {
        "ar": [
            "ابنِ مربع 5×5 من المفتاح (أحرف فريدة أولاً ثم باقي الأبجدية، وادمج J مع I).",
            "جهّز النص: أحرف لاتينية فقط، وافصل الحرفين المتماثلين بـ X، وأكمل الطول الفردي بـ X.",
            "لكل زوج: نفس الصف → يمين، نفس العمود → أسفل، مستطيل → تبادل الأعمدة.",
            "الفك يعكس الاتجاه (يسار/أعلى) بنفس المربع ثم تُزال حشوة X.",
        ],
        "en": [
            "Build the 5×5 square from the key (unique letters first, then the rest; merge J into I).",
            "Prepare the text: Latin letters only, split double letters with X, pad odd length with X.",
            "For each pair: same row → right, same column → down, rectangle → swap columns.",
            "Decrypt by reversing direction (left/up) with the same square, then strip X padding.",
        ],
    },
    "parameters": {
        "ar": [
            {"name": "playfair_key", "desc": "كلمة المفتاح (مثل MONARCHY — المثال الأشهر)."},
            {"name": "mode", "desc": "encrypt للتشفير أو decrypt للفك."},
        ],
        "en": [
            {"name": "playfair_key", "desc": "Keyword (e.g. MONARCHY — the classic example)."},
            {"name": "mode", "desc": "encrypt to encipher or decrypt to reverse."},
        ],
    },
    "security": {
        "ar": "مكسورة عملياً: الثنائيات الإنجليزية الشائعة (th وhe وer) تفضح المربع، والنص الطويل يكفي لكسرها يدوياً. أقوى من قيصر وفيجينير للتدريس فقط — لا استخدام حقيقي.",
        "en": "Practically broken: common English digraphs (th, he, er) expose the square, and long text suffices to break it by hand. Stronger than Caesar/Vigenère for teaching only — never for real use.",
    },
    "uses": {
        "ar": ["تعليم تشفير الثنائيات", "فهم تحليل التكرار المتقدم", "ألغاز تاريخية"],
        "en": ["Teaching digraph encryption", "Understanding advanced frequency analysis", "Historical puzzles"],
    },
}

# Max pairs with individual trace steps; longer inputs get one summary
# step instead of an unbounded tape (keeps history rows small).
_MAX_TRACED_PAIRS = 20


def _build_square(key_text: str) -> tuple[list[list[str]], dict[str, tuple[int, int]]]:
    """Build the 5×5 square and a letter→(row, col) index."""
    seen: list[str] = []
    for c in (key_text or "").upper():
        if c == "J":
            c = "I"
        if "A" <= c <= "Z" and c not in seen:
            seen.append(c)
    if not seen:
        raise ValueError("playfair_key must contain at least one Latin letter")
    for code in range(ord("A"), ord("Z") + 1):
        c = chr(code)
        if c == "J":
            continue
        if c not in seen:
            seen.append(c)
    grid = [seen[r * 5:(r + 1) * 5] for r in range(5)]
    pos = {c: (r, col) for r, row in enumerate(grid) for col, c in enumerate(row)}
    return grid, pos


def _prepare(text: str) -> list[str]:
    """Clean text into digraphs (J→I, X splitting/padding)."""
    letters = [("I" if c == "J" else c) for c in text.upper()
               if "A" <= c <= "Z" or c == "J"]
    pairs: list[str] = []
    i = 0
    while i < len(letters):
        a = letters[i]
        b = letters[i + 1] if i + 1 < len(letters) else ""
        if b == "":
            pairs.append(a + "X")
            i += 1
        elif a == b:
            pairs.append(a + "X")
            i += 1
        else:
            pairs.append(a + b)
            i += 2
    return pairs


def _enc_pair(a: str, b: str, pos: dict) -> str:
    ra, ca = pos[a]
    rb, cb = pos[b]
    if ra == rb:
        # same row → right
        inv = {v: k for k, v in pos.items()}
        return inv[(ra, (ca + 1) % 5)] + inv[(rb, (cb + 1) % 5)]
    if ca == cb:
        # same column → down
        inv = {v: k for k, v in pos.items()}
        return inv[((ra + 1) % 5, ca)] + inv[((rb + 1) % 5, cb)]
    # rectangle → swap columns
    inv = {v: k for k, v in pos.items()}
    return inv[(ra, cb)] + inv[(rb, ca)]


def _dec_pair(a: str, b: str, pos: dict) -> str:
    ra, ca = pos[a]
    rb, cb = pos[b]
    inv = {v: k for k, v in pos.items()}
    if ra == rb:
        return inv[(ra, (ca - 1) % 5)] + inv[(rb, (cb - 1) % 5)]
    if ca == cb:
        return inv[((ra - 1) % 5, ca)] + inv[((rb - 1) % 5, cb)]
    return inv[(ra, cb)] + inv[(rb, ca)]


def simulate(text: str, key=3, mode: str = "encrypt", extra=None):
    extra = extra or {}
    key_text = str(extra.get("playfair_key", "MONARCHY"))
    if mode not in ("encrypt", "decrypt"):
        raise ValueError("mode must be 'encrypt' or 'decrypt'")
    grid, pos = _build_square(key_text)
    square_preview = "/".join("".join(row) for row in grid)

    if mode == "encrypt":
        pairs = _prepare(text or "")
        transform = _enc_pair
    else:
        clean = [c for c in (text or "").upper() if "A" <= c <= "Z"]
        if len(clean) % 2 != 0:
            raise ValueError("decrypt expects even-length Latin ciphertext (pairs)")
        pairs = ["".join(clean[i:i + 2]) for i in range(0, len(clean), 2)]
        transform = _dec_pair

    steps = [
        {
            "index": 0,
            "title": {"ar": "مربع المفتاح", "en": "Key square"},
            "description": {
                "ar": f"المفتاح '{key_text}' ← المربع: {square_preview} | الأزواج: {len(pairs)}",
                "en": f"Key '{key_text}' → square: {square_preview} | Pairs: {len(pairs)}",
            },
            "snapshot": {"key": key_text, "square": grid, "pairs": len(pairs), "mode": mode},
            "highlight": [],
            "meta": {"phase": "setup"},
        }
    ]
    out: list[str] = []
    for i, pair in enumerate(pairs):
        new_pair = transform(pair[0], pair[1], pos)
        out.append(new_pair)
        if i >= _MAX_TRACED_PAIRS:
            continue
        ra, ca = pos[pair[0]]
        rb, cb = pos[pair[1]]
        if ra == rb:
            rule_ar, rule_en = "نفس الصف → يمين", "same row → right"
        elif ca == cb:
            rule_ar, rule_en = "نفس العمود → أسفل", "same column → down"
        else:
            rule_ar, rule_en = "مستطيل → تبادل الأعمدة", "rectangle → swap columns"
        if mode == "decrypt":
            rule_ar, rule_en = rule_ar + " (عكس)", rule_en + " (reverse)"
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"الزوج {i + 1}", "en": f"Pair {i + 1}"},
                "description": {
                    "ar": f"'{pair}' → '{new_pair}' ({rule_ar})",
                    "en": f"'{pair}' → '{new_pair}' ({rule_en})",
                },
                "snapshot": {"position": i, "pair_in": pair, "pair_out": new_pair, "rule": rule_en},
                "highlight": [i],
                "meta": {"phase": "transform", "position": i},
            }
        )
    if len(pairs) > _MAX_TRACED_PAIRS:
        steps.append(
            {
                "index": len(steps),
                "title": {"ar": f"... {len(pairs) - _MAX_TRACED_PAIRS} أزواج أخرى", "en": f"... {len(pairs) - _MAX_TRACED_PAIRS} more pairs"},
                "description": {
                    "ar": "نفس القواعد لكل زوج متبقٍ",
                    "en": "Same rules for each remaining pair",
                },
                "snapshot": {"remaining": len(pairs) - _MAX_TRACED_PAIRS},
                "highlight": [],
                "meta": {"phase": "transform"},
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
    key_text = str(extra.get("playfair_key", "MONARCHY"))
    distinct = len({(c.upper().replace("J", "I")) for c in key_text if c.isalpha() and c.isascii()})
    return {
        "strengths": {
            "ar": ["تكسر تكرار الحروف الأحادية (600+ ثنائية بدل 26 حرفاً)"],
            "en": ["Breaks single-letter frequency (600+ digraphs instead of 26 letters)"],
        },
        "weaknesses": {
            "ar": [
                "تكرار الثنائيات الشائعة (th/he/er) يفضح المربع",
                "النص الطويل يكفي للكسر اليدوي",
                "لا مفاتيح كبيرة ولا سلامة — مكسورة عملياً",
            ],
            "en": [
                "Common digraph frequency (th/he/er) exposes the square",
                "Long text suffices for manual breaking",
                "No large keys, no integrity — practically broken",
            ],
        },
        "metrics": {"distinct_key_letters": distinct, "key": key_text},
        "complexity": COMPLEXITY,
    }


register(
    "playfair",
    type="encryption",
    family="symmetric",
    kind="classical",
    security="broken",
    name={"ar": "بلاي فير", "en": "Playfair"},
    description={
        "ar": "تشفير الثنائيات بمربع 5×5 — مكسور تعليمياً",
        "en": "Digraph cipher with a 5×5 square — educational, broken",
    },
    params=["playfair_key", "mode"],
    keyspace=26 * 25,
    order=13,
)

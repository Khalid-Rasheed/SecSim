"""Interactive security tests: computed per-input analysis.

Routes:
    POST /api/security-tests: Run live measurements for an algorithm
    on the caller's input (entropy, keyspace/crack estimate, avalanche
    for hashes, salt/iteration checks for password KDFs...).
    POST /api/compare: Run 2..4 algorithms on (their own) inputs and
    return side-by-side results (digest size, rounds, time, avalanche)
    plus a bilingual verdict — powers the comparison presets
    (MD5 vs SHA-256, AES-128 vs AES-256).

Unlike POST /api/analyze (static theory), these endpoints measure the
ACTUAL input — e.g. avalanche % between hash(input) and hash(flipped),
or Shannon entropy of the message.
"""

from flask import Blueprint, jsonify, request

from app.schemas import parse_analyze, parse_compare
from app.services import security as sec
from app.services.simulator import analyze_algorithm, list_algorithms, run_simulation
from app.services.registry import lookup

security_bp = Blueprint("security", __name__)

_HASHLIB_MAP = {
    "md5": "md5",
    "sha1": "sha1",
    "sha256": "sha256",
    "sha512": "sha512",
    "sha3": "sha3_256",
}

_DIGEST_BITS = {"md5": 128, "sha1": 160, "sha256": 256, "sha512": 512, "sha3": 256}


def _t(ar: str, en: str) -> dict:
    return {"ar": ar, "en": en}


def _entropy_tests(text: str) -> list[dict]:
    shannon = sec.shannon_entropy_bits(text)
    charset = sec.charset_entropy_bits(text)
    level = "info" if not text else ("pass" if charset >= 60 else ("warn" if charset >= 28 else "fail"))
    return [
        {
            "id": "entropy",
            "name": _t("إنتروبيا الدخل", "Input entropy"),
            "status": level,
            "summary": _t(
                f"شانون {shannon} بت — حد المساحة {charset} بت (الطول {len(text or '')})",
                f"Shannon {shannon} bits — charset bound {charset} bits (length {len(text or '')})",
            ),
            "details": {"shannon_bits": shannon, "charset_bits": charset,
                        "length": len(text or "")},
        }
    ]


def _keyspace_tests(meta: dict, analysis_metrics: dict) -> list[dict]:
    """Keyspace + crack-time estimate from analyze() metrics."""
    tests: list[dict] = []
    keyspace = analysis_metrics.get("keyspace", meta.get("keyspace"))
    bits = None
    for candidate in (analysis_metrics.get("key_bits"), analysis_metrics.get("n_bits"),
                      analysis_metrics.get("p_bits")):
        if isinstance(candidate, int):
            bits = candidate
            break
    n_bits = analysis_metrics.get("key_length")
    if isinstance(keyspace, int):
        est = sec.crack_estimate(keyspace)
        status = "fail" if keyspace <= 100 else ("warn" if keyspace <= 2**40 else "pass")
        tests.append({
            "id": "keyspace",
            "name": _t("مساحة المفاتيح وزمن الكسر", "Keyspace & crack time"),
            "status": status,
            "summary": _t(
                f"المساحة {keyspace:,} — متوسط الكسر {est['human']['ar']} (بـ 10G تخمين/ث)",
                f"Keyspace {keyspace:,} — avg crack {est['human']['en']} (at 10G guesses/s)",
            ) if est else _t("مساحة معروفة", "Known keyspace"),
            "details": {"keyspace": keyspace, "crack": est},
        })
    elif isinstance(keyspace, str) and keyspace.startswith("2^"):
        try:
            exp = int("".join(c for c in keyspace if c.isdigit())[:4])
        except ValueError:
            exp = 128
        seconds_avg = (2**exp / 2) / sec.GUESSES_PER_SECOND
        from app.services.security import _human_duration  # internal formatter
        human = _human_duration(seconds_avg)
        tests.append({
            "id": "keyspace",
            "name": _t("مساحة المفاتيح وزمن الكسر", "Keyspace & crack time"),
            "status": "pass",
            "summary": _t(
                f"المساحة {keyspace} — متوسط الكسر {human['ar']} (عملياً مستحيل)",
                f"Keyspace {keyspace} — avg crack {human['en']} (practically impossible)",
            ),
            "details": {"keyspace": keyspace, "exponent_bits": exp},
        })
    elif isinstance(bits, int):
        # RSA/DH toy moduli or RC4 key bits
        status = "fail" if bits < 64 else ("warn" if bits < 128 else "pass")
        tests.append({
            "id": "modulus",
            "name": _t("حجم المفتاح/المعامل", "Key/modulus size"),
            "status": status,
            "summary": _t(
                f"الحجم {bits} بت — تعليمي ويُكسر فوراً (الواقع 2048+ بت)",
                f"Size {bits} bits — toy, breaks instantly (reality: 2048+ bits)",
            ) if bits < 512 else _t(f"الحجم {bits} بت", f"Size {bits} bits"),
            "details": {"bits": bits},
        })
    if isinstance(n_bits, int) and meta.get("id") == "vigenere":
        tests.append({
            "id": "keylength",
            "name": _t("طول مفتاح فيجينير", "Vigenère key length"),
            "status": "warn" if n_bits < 8 else "pass",
            "summary": _t(
                f"الطول {n_bits} — المساحة 26^{n_bits} لكن كاسيسكي يكشف الطول",
                f"Length {n_bits} — keyspace 26^{n_bits} but Kasiski reveals length",
            ),
            "details": {"key_length": n_bits},
        })
    return tests


def _hash_tests(algo_id: str, text: str) -> list[dict]:
    tests: list[dict] = []
    bits = _DIGEST_BITS.get(algo_id)
    hashlib_name = _HASHLIB_MAP.get(algo_id)
    if bits:
        bound = sec.collision_bound_years(bits)
        status = "fail" if algo_id in ("md5", "sha1") else "pass"
        tests.append({
            "id": "collision",
            "name": _t("مقاومة التصادم (حد عيد الميلاد)", "Collision resistance (birthday bound)"),
            "status": status,
            "summary": _t(
                f"ملخص {bits}-بت — التصادم عند ≈ {bound['operations']} عملية",
                f"{bits}-bit digest — collisions at ≈ {bound['operations']} ops",
            ),
            "details": {"digest_bits": bits, "birthday_operations": bound["operations"]},
        })
    if hashlib_name:
        data = (text or "").encode("utf-8")
        h1 = sec.hash_hex(hashlib_name, data)
        h2 = sec.hash_hex(hashlib_name, sec.flip_first_char(text or "").encode("utf-8"))
        pct = sec.avalanche_pct(h1, h2) if h1 and h2 else None
        if pct is not None:
            ok = 40 <= pct <= 60
            tests.append({
                "id": "avalanche",
                "name": _t("أثر الانهيار الجليدي (قلب بت واحد)", "Avalanche effect (flip one bit)"),
                "status": "pass" if ok else "warn",
                "summary": _t(
                    f"تغيّر {pct}% من بتات الملخص — المثالي ~50%",
                    f"{pct}% of digest bits flipped — ideal ≈50%",
                ),
                "details": {"avalanche_pct": pct, "digest_a": h1, "digest_b": h2},
            })
    return tests


def _password_tests(analysis_metrics: dict) -> list[dict]:
    tests: list[dict] = []
    it = analysis_metrics.get("iterations")
    if isinstance(it, int):
        status = "pass" if it >= 210_000 else ("warn" if it >= 10_000 else "fail")
        tests.append({
            "id": "iterations",
            "name": _t("تكرارات الاشتقاق", "KDF iterations"),
            "status": status,
            "summary": _t(
                f"{it:,} تكرار — الحد الأدنى للإنتاج 210k (OWASP)",
                f"{it:,} iterations — production minimum 210k (OWASP)",
            ),
            "details": {"iterations": it, "owasp_minimum": 210000},
        })
    tests.append({
        "id": "salt",
        "name": _t("الملح العشوائي", "Random salt"),
        "status": "pass",
        "summary": _t(
            "PBKDF2 يولد ملحاً عشوائياً 16 بايت — يهزم جداول قوس قزح",
            "PBKDF2 generates a random 16-byte salt — defeats rainbow tables",
        ),
        "details": {"salt_bytes": 16},
    })
    return tests


@security_bp.post("/security-tests")
def security_tests():
    """Run live security measurements for an algorithm on given input.

    Request JSON::

        {"algorithm": "sha256", "input": "hello",
         "parameters": {"vigenere_key": "LEMON"}}

    Returns 200 with ``{algorithm, tests[]}``; 400 for unknown ids.
    """
    data = request.get_json(force=True, silent=True) or {}
    clean, error = parse_analyze(data)
    if error:
        return jsonify({"error": error}), 400
    algorithm = clean["algorithm"]
    params = clean["parameters"] or {}
    text = data.get("input", "")
    if not isinstance(text, str):
        return jsonify({"error": "input must be a string"}), 400
    ids = {a["id"] for a in list_algorithms()}
    if algorithm not in ids:
        return jsonify({"error": f"Unsupported algorithm: {algorithm}"}), 400
    try:
        entry = lookup(algorithm)
        meta = entry["meta"]
        metrics = entry["analyze"]({**params, "key": params.get("key", 3)}) or {}
        metrics = metrics.get("metrics", {}) if isinstance(metrics, dict) else {}
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    tests = _entropy_tests(text)
    tests += _keyspace_tests(meta, metrics)
    if meta["family"] == "hashing" and meta["kind"] in ("broken", "secure"):
        tests += _hash_tests(algorithm, text)
    if meta["kind"] == "password":
        tests += _password_tests(metrics)
    if meta["family"] == "asymmetric":
        tests.append({
            "id": "auth",
            "name": _t("المصادقة ورجل-في-الوسط", "Authentication & MITM"),
            "status": "warn",
            "summary": _t(
                "التبادل دون مصادقة عُرضة لرجل-في-الوسط — الواقع يحتاج شهادات/توقيعات",
                "Unauthenticated exchange is MITM-vulnerable — reality needs certs/signatures",
            ),
            "details": {},
        })
    if meta["id"] in ("caesar", "vigenere"):
        tests.append({
            "id": "frequency",
            "name": _t("تحليل التكرار", "Frequency analysis"),
            "status": "fail",
            "summary": _t(
                "شيفرة إبدالية — توزيع الحروف يكشف النص دون تجربة كل المفاتيح",
                "Substitution cipher — letter frequency reveals text without trying all keys",
            ),
            "details": {},
        })
    return jsonify({"algorithm": algorithm, "tests": tests})


def _compare_avalanche(algo_id: str, text: str) -> float | None:
    """Avalanche % for one hash entry (None for non-hashes)."""
    hashlib_name = _HASHLIB_MAP.get(algo_id)
    if not hashlib_name:
        return None
    data = (text or "").encode("utf-8")
    h1 = sec.hash_hex(hashlib_name, data)
    h2 = sec.hash_hex(hashlib_name, sec.flip_first_char(text or "").encode("utf-8"))
    return sec.avalanche_pct(h1, h2) if h1 and h2 else None


def _compare_verdict(entries: list[dict]) -> dict:
    """Pick a bilingual winner line from compared entries.

    Rules (teaching-first, deterministic):
        - all hashes → largest digest wins (birthday bound doubles);
        - all AES → larger key wins (rounds + keyspace);
        - otherwise → fastest secure entry wins, broken entries flagged.
    """
    ids = [e["algorithm"] for e in entries]
    if all(_DIGEST_BITS.get(i) for i in ids):
        best = max(entries, key=lambda e: _DIGEST_BITS[e["algorithm"]])
        bits = _DIGEST_BITS[best["algorithm"]]
        return _t(
            f"الفائز: {best['algorithm']} (ملخص {bits}-بت — حد عيد ميلاد 2^{bits // 2})",
            f"Winner: {best['algorithm']} ({bits}-bit digest — 2^{bits // 2} birthday bound)",
        )
    if all(i == "aes" for i in ids):
        best = max(entries, key=lambda e: int(e["analysis_metrics"].get("key_bits", 0)))
        kb = best["analysis_metrics"].get("key_bits", "?")
        return _t(
            f"الفائز: AES-{kb} (جولات ومساحة مفاتيح أكبر — الفرق نظري ضد هجمات المستقبل)",
            f"Winner: AES-{kb} (more rounds and keyspace — a hedge against future attacks)",
        )
    broken = [e["algorithm"] for e in entries
              if e["meta"].get("security") == "broken"]
    if broken:
        return _t(
            f"تنبيه: {', '.join(broken)} مكسورة — لا تستخدمها حقيقة",
            f"Warning: {', '.join(broken)} is broken — never use it for real",
        )
    fastest = min(entries, key=lambda e: e["metrics"]["time_ms"])
    return _t(
        f"الأسرع في هذا الإدخال: {fastest['algorithm']} ({fastest['metrics']['time_ms']} مللي ثانية)",
        f"Fastest on this input: {fastest['algorithm']} ({fastest['metrics']['time_ms']} ms)",
    )


@security_bp.post("/compare")
def compare():
    """Run 2..4 algorithms side by side on the same (or own) inputs.

    Request JSON::

        {"comparisons": [{"algorithm": "md5", "input": "hello"},
                         {"algorithm": "sha256", "input": "hello"}]}

    ``parameters`` per entry is optional and forwarded like /simulate
    (e.g. ``{"key_size": 256}`` for the AES-256 side). Runs are NOT
    saved to history. Returns 200 with ``{results[], verdict{ar,en}}``;
    400 for bad shapes, unknown ids, or entry ``ValueError`` rejections
    (reported with the entry index).
    """
    data = request.get_json(force=True, silent=True) or {}
    clean, error = parse_compare(data)
    if error:
        return jsonify({"error": error}), 400
    ids = {a["id"] for a in list_algorithms()}
    results: list[dict] = []
    for i, item in enumerate(clean["comparisons"]):
        algo_id, text, params = item["algorithm"], item["text"], item["parameters"]
        if algo_id not in ids:
            return jsonify({"error": f"comparisons[{i}]: Unsupported algorithm: {algo_id}"}), 400
        try:
            entry = lookup(algo_id)
            result, steps, metrics, analysis = run_simulation(
                algo_id, text, params.get("key", 3),
                params.get("mode", "encrypt"), params,
            )
        except ValueError as e:
            return jsonify({"error": f"comparisons[{i}]: {e}"}), 400
        analysis_metrics = analysis.get("metrics", {}) if isinstance(analysis, dict) else {}
        results.append({
            "algorithm": algo_id,
            "meta": entry["meta"],
            "input": text,
            "result": result,
            "result_preview": result[:64] + ("..." if len(result) > 64 else ""),
            "result_len": len(result),
            "metrics": metrics,
            "analysis_metrics": analysis_metrics,
            "complexity": analysis.get("complexity") if isinstance(analysis, dict) else None,
            "digest_bits": _DIGEST_BITS.get(algo_id),
            "avalanche_pct": _compare_avalanche(algo_id, text),
        })
    return jsonify({"results": results, "verdict": _compare_verdict(results)})

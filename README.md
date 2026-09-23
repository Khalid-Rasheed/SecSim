# SecSim — Interactive Security Algorithms Simulator

![CI](https://github.com/Khalid-Rasheed/SecSim/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)
![Node](https://img.shields.io/badge/Node-20%2B-green.svg)

> **Learn security by breaking it open.** SecSim is a bilingual (Arabic/English)
> web lab where you can *run* security algorithms step by step, *read* a full
> reference guide for each one, and *analyze* their strengths, weaknesses and
> complexity — all in one place.

## Contents

- [The idea](#the-idea)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Run (Windows)](#run-windows)
- [Run tests](#run-tests)
- [Docker (full stack)](#docker-full-stack)
- [API reference](#api-reference)
- [Supported inputs](#supported-inputs)
- [Algorithm complexity](#algorithm-complexity)
- [Adding an algorithm](#adding-an-algorithm-single-file-zero-edits-elsewhere)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

## The idea

Textbooks show you *what* an algorithm outputs; SecSim shows you *how* it gets
there. Pick an algorithm — Caesar, Vigenère, Playfair, RC4, AES, RSA,
Diffie-Hellman, ElGamal, SHA-256, or a live attack like the Vigenère breaker
(19 in total across symmetric / asymmetric / hashing + an attack lab) — feed
it your own input — Arabic, English, symbols or emoji — and watch every
transformation unfold as an inspectable, replayable step tape. Each algorithm
also ships with a reference page (story, mechanics, parameters, security
stance, real-world uses), so the platform doubles as a **playground and a
reference**.

Who is it for:

- **Students & the curious** — see encryption happen character by character.
- **Developers** — compare algorithms empirically (measured time) and
  theoretically (Big-O) before choosing one.
- **Contributors** — add a new algorithm with a single file (see below).

## Features

- **Step-by-step simulation** — unified step schema
  `{index, title{ar,en}, description{ar,en}, snapshot, highlight, meta}` with
  play / pause / prev / next / speed transport.
- **Reference guides** — `GET /api/algorithms/<id>` serves a bilingual guide
  (overview, history, how-it-works, parameters, security, uses) rendered on
  `/algorithms/:id`, with a one-click jump into the simulator (`?algo=`).
- **Security analysis** — strengths, weaknesses, keyspace metrics and
  Big-O time/space complexity per algorithm, plus a Chart.js timing chart.
- **Computed security tests** — `POST /api/security-tests` measures your
  actual input live: entropy, keyspace/crack-time estimate, avalanche %
  and birthday bound for hashes, salt/iteration checks for password KDFs.
- **Side-by-side comparison** — `POST /api/compare` runs 2–4 algorithms on
  one input (presets: MD5 vs SHA-256, AES-128 vs AES-256, SHA family) with
  a bilingual verdict; results are never saved to history.
- **Attack lab** — five real attacks, not animations: Caesar brute force,
  Vigenère breaker (Kasiski + IC + column break), DH man-in-the-middle,
  birthday-collision finder on truncated SHA-256, and dictionary attack on
  unsalted MD5 with a salt lesson.
- **Accounts & history** — JWT auth; simulations auto-save to your account
  when you are logged in; last 50 runs browsable in History.
- **Bilingual UI** — Arabic (RTL, default) / English toggle; algorithm content
  itself is served bilingual from the API.
- **Beginner-friendly UX** — guided 5-station learning path (`/learn`) with
  local progress, difficulty badges, one-line `?` help on every simulator
  input, a plain-language glossary, readable step snapshots, and a
  searchable algorithm menu that works on mobile.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.x, Flask-SQLAlchemy, Flask-Migrate, Flask-CORS, Flask-JWT-Extended, Flask-Limiter, pycryptodome |
| Frontend | Vue 3, Vite, Tailwind CSS, Pinia, Vue Router, Axios, Chart.js, vue-i18n, Font Awesome |
| Database | SQLite (dev) / PostgreSQL-ready via `DATABASE_URL` |
| DevOps | Docker + docker-compose (gunicorn / nginx), GitHub Actions CI, pytest (61 tests) |

## Project structure

```text
backend/
  app/
    __init__.py        # app factory: extensions, blueprints, JSON errors
    models/            # User, Simulation (SQLAlchemy)
    routes/            # auth / algorithms / simulation / analysis / security (tests + compare)
    services/          # registry.py (self-registering catalogue + taxonomy tree)
                       # simulator.py (thin dispatcher, knows no algo by name)
                       # security.py (entropy / crack-time / avalanche helpers)
  algorithms/          # plug-ins: encryption/ hashing/ attacks/ (19 total)
    encryption/caesar.py, vigenere.py, playfair.py, rc4.py, aes.py,
                 rsa.py, diffie_hellman.py, elgamal.py ...
    hashing/md5.py, sha1.py, sha256.py, sha512.py, sha3.py, pbkdf2.py ...
    attacks/brute_force.py, vigenere_breaker.py, dh_mitm.py,
            birthday_collision.py, dictionary_attack.py ...
  tests/               # test_api / test_inputs / test_phase3 / test_registry
  config.py  run.py  requirements.txt  Dockerfile
frontend/
  src/
    views/             # Home / LearnPath (beginner track) / Simulator / AlgorithmDetails / History / Profile / Login
    components/        # FieldHint (?) / CipherTape / VisualizationArea / SecurityMetrics / ComparePanel / Navbar
    utils/             # ux.js (difficulty levels, attack↔victim maps, snapshot formatting)
    stores/            # authStore / simulationStore (Pinia)
    router/  services/api.js (JWT interceptor)  i18n/ (ar.json, en.json)
docs/api.md            # full endpoint reference
```

## Prerequisites

| Tool | Minimum version | Notes |
|---|---|---|
| Python | 3.12+ | On Windows use the `py` launcher (`py -m pip`, `py run.py`) — plain `python` may not be on PATH |
| Node.js | 20+ | Ships with npm; frontend uses Vite 6 |
| Docker (optional) | 24+ | Only needed for the compose stack |
| Git | any | Clone + contribution workflow |

## Run (Windows)

```powershell
# Backend (Flask 3.x) → http://localhost:5000/api/health
cd backend
py -m venv venv
.\venv\Scripts\activate
py -m pip install -r requirements.txt
copy .env.example .env
py run.py

# Frontend (Vue 3 + Vite) → http://localhost:5173
cd ..\frontend
npm install
npm run dev
```

Set `frontend/.env`: `VITE_API_URL=http://localhost:5000/api` (or rely on Vite proxy).

## Run tests

```powershell
cd backend
py -m pytest -q        # 61 tests: API, input matrix (AR/EN/emoji/empty),
                       # Phase-3 algos incl. attack roundtrips, registry
                       # contract + taxonomy + security-tests/compare guards
```

## Docker (full stack)

```powershell
docker compose up --build
# UI → http://localhost:5173 · API → http://localhost:5000/api/health
```

Images: `backend/Dockerfile` (gunicorn, 2 workers), `frontend/Dockerfile`
(multi-stage build → nginx with SPA fallback). The SQLite DB persists in
the `secsim-data` volume. Override `SECRET_KEY` / `JWT_SECRET_KEY` via
environment in production — never ship the compose defaults.

## API reference

Base URL: `http://localhost:5000/api`. Error bodies are always JSON:
`{"error": "<message>"}` (400/401/404/405/429/500).

| Method & path | Auth | Description |
|---|---|---|
| `GET /api/health` | — | Liveness probe → `{status: ok}` |
| `GET /api/algorithms` | — | Catalog: `[{id, type, family, kind, security, name{ar,en}, description{ar,en}, params, keyspace, complexity}]` (19 entries) |
| `GET /api/taxonomy` | — | Hierarchical tree: `{tabs: [{family, kinds: [...]}]}` (symmetric / asymmetric / hashing) + `attacks` lab |
| `GET /api/algorithms/<id>` | — | Full entry + bilingual `details` guide (overview, history, how_it_works, parameters, security, uses) |
| `POST /api/auth/register` | — | `{email, password, name?}` → `{token, user}` (201). Email must be `user@domain.tld`; password ≥ 8 chars with a letter and a digit. **5/min/IP** |
| `POST /api/auth/login` | — | `{email, password}` → `{token, user}`. Wrong credentials → identical 401 (no email enumeration). **10/min/IP** |
| `GET /api/auth/me` | Bearer | Current-user profile |
| `POST /api/simulate` | Optional | `{algorithm, input, ...params}` → `{id, result, steps[], metrics{time_ms, steps}, analysis}`. Saved anonymously, or linked to you when a token is sent. Extra params per algorithm: `key` (caesar), `vigenere_key`, `playfair_key`, `rc4_key`, `key_text` + `key_size` (aes), `rsa_p/q/e`, `dh_p/g/a/b`, `mitm_e/f` (dh_mitm), `collision_bits` (birthday), `elgamal_p/g/x/k` |
| `POST /api/analyze` | — | `{algorithm, parameters?}` → `{algorithm, analysis}` (no simulation) |
| `POST /api/security-tests` | — | `{algorithm, input, parameters?}` → `{algorithm, tests[]}` — live entropy / keyspace / avalanche / collision / salt measurements |
| `POST /api/compare` | — | `{comparisons: [{algorithm, input, parameters?}]}` (2–4) → `{results[], verdict{ar,en}}` (never saved to history) |
| `GET /api/history` | Bearer | Your last 50 runs, newest first (without step traces) |
| `GET /api/history/<id>` | Bearer | One run with full `steps` (owner-only; others → 404) |

Security notes:
- JWT access tokens live 12h (`JWT_ACCESS_HOURS`); expired/malformed tokens
  answer 401/422, and the Vue interceptor logs out and routes to
  `/login?expired=1` with a visible notice.
- Rate limits answer `429 {"error": "rate limit exceeded, try again later"}`.
- AES key handling and RSA toy primes are teaching simplifications — the
  demo labels them as such; do not reuse them in real systems.

## Supported inputs

Every algorithm accepts Arabic, English, symbols and emoji (UTF-8
end-to-end), including empty input. Two honest limits: Caesar passes
non-Latin scripts through unchanged (it is a Latin-shift cipher — the demo
makes this visible), and RSA toy primes (n=3233) only fit codes below n —
larger scripts need bigger `p`/`q`, which the UI lets you set.

## Algorithm complexity

| Algorithm | Time | Space | n = |
|---|---|---|---|
| Caesar | O(n) | O(n) | characters |
| Vigenère | O(n) | O(n) | characters (keyspace grows with key length) |
| Playfair | O(n) | O(n) | characters (one 5×5 lookup per digraph) |
| RC4 | O(n) | O(1) | input bytes (fixed 256-byte setup) |
| AES-CBC | O(n) | O(n) | input bytes (fixed 10/12/14 rounds) |
| RSA | O(n · log e) | O(n) | message chars (modular exponentiation each) |
| Diffie-Hellman | O(log p) | O(1) | modulus bits (one exponentiation per party) |
| ElGamal | O(n · log p) | O(n) | message chars (two exponentiations each) |
| SHA-256 | O(n) | O(1) | input bytes (fixed 256-bit state) |
| SHA-512 | O(n) | O(1) | input bytes (fixed 512-bit state) |
| SHA-3 | O(n) | O(1) | input bytes (fixed 1600-bit sponge) |
| MD5 / SHA-1 | O(n) | O(1) | input bytes (broken — teaching only) |
| PBKDF2 | O(iterations) | O(1) | iteration count (slowness is deliberate) |
| Brute Force | O(25 · n) | O(n) | ciphertext length |
| Vigenère breaker | O(12 · (n + 26 · n)) | O(n) | ciphertext length (lengths × columns × shifts) |
| DH MITM | O(log p) | O(1) | modulus bits (a few exponentiations) |
| Birthday collision | O(2^(n/2)) | O(2^(n/2)) | truncated digest bits (square-root bound) |
| Dictionary attack | O(W) | O(1) | wordlist size (one cheap hash per word) |

## Adding an algorithm (single file, zero edits elsewhere)
1. Create `backend/algorithms/<encryption|hashing|attacks>/<id>.py` with:
   - `simulate(text, key=3, mode="encrypt", extra=None) -> (result, steps)` — unified step schema
   - `analyze(extra=None) -> {strengths, weaknesses, metrics}` (+ `complexity`)
   - `COMPLEXITY = {time, space, n{ar,en}, note{ar,en}}`
   - `DETAILS = {overview, history, how_it_works, parameters, security, uses}` (all `{ar,en}`)
   - one `register("<id>", type=..., name={...}, description={...}, params=[...], keyspace=..., order=N)` call at the end
2. It is auto-discovered on next reload: list, detail page, simulate, analyze, history all work.
3. Frontend: only add input widgets if it has params (`simulationStore.js` + conditional panel in `Simulator.vue`); guide page, badges and icons render automatically. Guarded by `tests/test_registry.py`.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `python` / `pip` not recognized (Windows) | Use the `py` launcher: `py -m pip …`, `py run.py` |
| Port `5173` busy | Another Vite app is holding it — stop it, then `npm run dev` |
| Port `5000` busy | Stop the old Flask process, then `py run.py` |
| `401` after login, redirect to login | JWT expired (12h default) — log in again; check system clock skew |
| `429 rate limit exceeded` | Too many auth attempts — wait a minute (limits documented above) |
| Arabic shows as boxes | Missing Arabic font in the OS/browser — install any Arabic-capable font |
| `GET /history` → `401` | No/expired `Authorization: Bearer <token>` header — log in first |

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md)
first (setup, branch naming, PR checklist), open algorithm ideas as an
[algorithm proposal](.github/ISSUE_TEMPLATE/algorithm_proposal.md), and
report vulnerabilities privately per [SECURITY.md](SECURITY.md).

## Roadmap
- Export PDF/CSV, elliptic-curve (ECC) teaching module, ChaCha20, frequency-analysis visualizer

## License
MIT — free for educational use.

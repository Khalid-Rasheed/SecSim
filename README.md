# SecSim — Interactive Security Algorithms Simulator

> **Learn security by breaking it open.** SecSim is a bilingual (Arabic/English)
> web lab where you can *run* security algorithms step by step, *read* a full
> reference guide for each one, and *analyze* their strengths, weaknesses and
> complexity — all in one place.

## The idea

Textbooks show you *what* an algorithm outputs; SecSim shows you *how* it gets
there. Pick an algorithm (Caesar, AES, RSA, SHA-256, MD5, Brute Force…), feed
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
- **Attack lab** — brute-force demo that tries all 25 Caesar keys and ranks
  candidates statistically.
- **Accounts & history** — JWT auth; simulations auto-save to your account
  when you are logged in; last 50 runs browsable in History.
- **Bilingual UI** — Arabic (RTL, default) / English toggle; algorithm content
  itself is served bilingual from the API.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.x, Flask-SQLAlchemy, Flask-Migrate, Flask-CORS, Flask-JWT-Extended, Flask-Limiter, pycryptodome |
| Frontend | Vue 3, Vite, Tailwind CSS, Pinia, Vue Router, Axios, Chart.js, vue-i18n, Font Awesome |
| Database | SQLite (dev) / PostgreSQL-ready via `DATABASE_URL` |
| DevOps | Docker + docker-compose (gunicorn / nginx), GitHub Actions CI, pytest (48 tests) |

## Project structure

```text
backend/
  app/
    __init__.py        # app factory: extensions, blueprints, JSON errors
    models/            # User, Simulation (SQLAlchemy)
    routes/            # auth / algorithms / simulation / analysis blueprints
    services/          # registry.py (self-registering catalogue)
                       # simulator.py (thin dispatcher, knows no algo by name)
  algorithms/          # plug-ins: encryption/ hashing/ attacks/
    encryption/caesar.py, aes.py, rsa.py ...
  tests/               # test_api / test_inputs / test_phase3 / test_registry
  config.py  run.py  requirements.txt  Dockerfile
frontend/
  src/
    views/             # Home / Simulator / AlgorithmDetails / History / Profile / Login
    components/        # CipherTape (signature), VisualizationArea, SecurityMetrics, Navbar
    stores/            # authStore / simulationStore (Pinia)
    router/  services/api.js (JWT interceptor)  i18n/ (ar.json, en.json)
docs/api.md            # full endpoint reference
```

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
py -m pytest -q        # 48 tests: API, input matrix (AR/EN/emoji/empty),
                       # Phase-3 algos, registry contract guards
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
| `GET /api/algorithms` | — | Catalog: `[{id, type, name{ar,en}, description{ar,en}, params, keyspace, complexity}]` |
| `GET /api/algorithms/<id>` | — | Full entry + bilingual `details` guide (overview, history, how_it_works, parameters, security, uses) |
| `POST /api/auth/register` | — | `{email, password, name?}` → `{token, user}` (201). Email must be `user@domain.tld`; password ≥ 8 chars with a letter and a digit. **5/min/IP** |
| `POST /api/auth/login` | — | `{email, password}` → `{token, user}`. Wrong credentials → identical 401 (no email enumeration). **10/min/IP** |
| `GET /api/auth/me` | Bearer | Current-user profile |
| `POST /api/simulate` | Optional | `{algorithm, input, key?, mode?, key_text?, key_size?, rsa_p?, rsa_q?, rsa_e?}` → `{id, result, steps[], metrics{time_ms, steps}, analysis}`. Saved anonymously, or linked to you when a token is sent |
| `POST /api/analyze` | — | `{algorithm, parameters?}` → `{algorithm, analysis}` (no simulation) |
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
| AES-CBC | O(n) | O(n) | input bytes (fixed 10/12/14 rounds) |
| RSA | O(n · log e) | O(n) | message chars (modular exponentiation each) |
| SHA-256 | O(n) | O(1) | input bytes (fixed 256-bit state) |
| MD5 | O(n) | O(1) | input bytes (fixed 128-bit state) |
| Brute Force | O(25 · n) | O(n) | ciphertext length |

## Adding an algorithm (single file, zero edits elsewhere)
1. Create `backend/algorithms/<encryption|hashing|attacks>/<id>.py` with:
   - `simulate(text, key=3, mode="encrypt", extra=None) -> (result, steps)` — unified step schema
   - `analyze(extra=None) -> {strengths, weaknesses, metrics}` (+ `complexity`)
   - `COMPLEXITY = {time, space, n{ar,en}, note{ar,en}}`
   - `DETAILS = {overview, history, how_it_works, parameters, security, uses}` (all `{ar,en}`)
   - one `register("<id>", type=..., name={...}, description={...}, params=[...], keyspace=..., order=N)` call at the end
2. It is auto-discovered on next reload: list, detail page, simulate, analyze, history all work.
3. Frontend: only add input widgets if it has params (`simulationStore.js` + conditional panel in `Simulator.vue`); guide page, badges and icons render automatically. Guarded by `tests/test_registry.py`.

## Roadmap
- Dictionary attack, MITM demo, algorithm comparison view, export PDF/CSV

## License
MIT — free for educational use.

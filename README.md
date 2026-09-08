# SecSim — Interactive Security Algorithms Simulator

## Run (Windows)

```powershell
# Backend (Flask 3.x)
cd backend
py -m venv venv
.\venv\Scripts\activate
py -m pip install -r requirements.txt
copy .env.example .env
py run.py   # http://localhost:5000/api/health
py -m pytest -q

# Frontend (Vue 3 + Vite)
cd ..\frontend
npm install
npm run dev    # http://localhost:5173
```

Set `frontend/.env`: `VITE_API_URL=http://localhost:5000/api` (or rely on Vite proxy).

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

## MVP scope
- Algorithms: Caesar (encrypt/decrypt + steps), AES-CBC (128/192/256, per-block steps), RSA (toy primes, per-char steps), SHA-256, MD5 (broken, for comparison), Brute-Force attack on Caesar (25 attempts, ranked)
- Step engine: unified JSON `{index, title{ar,en}, description{ar,en}, snapshot, highlight, meta}` + metrics + static security analysis
- Auth: JWT register/login/me; `/simulate` saves history when token present; `/history` requires JWT
- Analysis: `POST /api/analyze` for standalone security analysis
- Frontend: AR/EN toggle with RTL, Home/Simulator/History/Profile/Login, step player (play/pause/prev/next/speed), Chart.js time chart

## Next
- Dictionary attack, MITM demo, algorithm comparison view, export PDF/CSV

## Adding an algorithm (single file, zero edits elsewhere)
1. Create `backend/algorithms/<encryption|hashing|attacks>/<id>.py` with:
   - `simulate(text, key=3, mode="encrypt", extra=None) -> (result, steps)` — unified step schema
   - `analyze(extra=None) -> {strengths, weaknesses, metrics}` (+ `complexity`)
   - `COMPLEXITY = {time, space, n{ar,en}, note{ar,en}}`
   - `DETAILS = {overview, history, how_it_works, parameters, security, uses}` (all `{ar,en}`)
   - one `register("<id>", type=..., name={...}, description={...}, params=[...], keyspace=..., order=N)` call at the end
2. It is auto-discovered on next reload: list, detail page, simulate, analyze, history all work.
3. Frontend: only add input widgets if it has params (`simulationStore.js` + conditional panel in `Simulator.vue`); guide page, badges and icons render automatically. Guarded by `tests/test_registry.py`.

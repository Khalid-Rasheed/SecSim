# Contributing to SecSim

Thank you for contributing! This guide keeps multi-developer work smooth.
Please also follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Setup

```powershell
# Backend
cd backend
py -m venv venv; .\venv\Scripts\activate
py -m pip install -r requirements.txt
copy .env.example .env
py -m pytest -q            # must be green before you push

# Frontend
cd ..\frontend
npm install
npm run dev                # http://localhost:5173 (proxies /api to :5000)
npm run build              # must succeed before you push
```

## Workflow

1. **Branch** from `master`: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`.
2. **One concern per PR**; keep PRs small and linked to an issue.
3. **PR checklist** (enforced by CI + reviewers):
   - [ ] `py -m pytest -q` green (backend) and `npm run build` green (frontend)
   - [ ] New behavior covered by tests (see below)
   - [ ] User-facing strings added in **both** `ar.json` and `en.json`
   - [ ] No emojis in the UI (Font Awesome icons only)
   - [ ] `docs/api.md` / README updated if any endpoint or contract changed
4. **Commits**: imperative English subject, e.g. `Add AES-256-GCM mode`.
   Reference issues: `Fixes #12`.

## Adding an algorithm (full checklist)

Backend single-file plug-in (auto-discovered, zero edits elsewhere):

- [ ] New module `backend/algorithms/<encryption|hashing|attacks>/<id>.py`
      with `simulate(text, key, mode, extra)`, `analyze(extra)`,
      `COMPLEXITY`, bilingual `DETAILS`, and one trailing `register(...)`.
- [ ] Round-trip property: `decrypt(encrypt(x)) == x` for representative
      inputs (AR/EN/symbols/emoji/empty) + a graceful `ValueError` case.
- [ ] Security honesty: teaching simplifications (toy keys, ECB, raw RSA…)
      stated in `security`/`note`, never silently.
- [ ] Registry guard (`tests/test_registry.py`) still green — it validates
      your module automatically.

Frontend (only if the algorithm has parameters or custom display):

- [ ] Input widgets: `simulationStore.js` payload mapping + conditional panel
      in `Simulator.vue` + type icon in `algoIcon`/`histIcon` helpers.
- [ ] i18n labels in both languages; guide page/badges render automatically.

## Reporting bugs / proposing features

Use the issue templates (bug report needs a repro payload; algorithm ideas
use the proposal form). Security vulnerabilities: **do not open public
issues** — see [SECURITY.md](SECURITY.md).

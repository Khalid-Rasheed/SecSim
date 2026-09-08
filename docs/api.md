# SecSim API

## Health
`GET /api/health` → `{status: ok}`

## Algorithms
`GET /api/algorithms` → `[{id, type, name{ar,en}, description{ar,en}, params, complexity}]`

`GET /api/algorithms/<id>` → full entry + `details` reference guide:
`{overview{ar,en}, history{ar,en}, how_it_works{ar[],en[]}, parameters{ar[{name,desc}],en[]}, security{ar,en}, uses{ar[],en[]}}`

Each algorithm carries a theoretical complexity block:
`{time: "O(n)", space: "O(n)", n{ar,en}: "what n means", note{ar,en}: "explanation"}`
— also included in every `/simulate` and `/analyze` response under `analysis.complexity`.
Measured wall-clock time stays under `metrics.time_ms`.

## Auth
- `POST /api/auth/register {email, password, name?}` → `{token, user}` (201)
- `POST /api/auth/login {email, password}` → `{token, user}`
- `GET /api/auth/me` (Bearer) → user

## Simulate
`POST /api/simulate`
```json
{ "algorithm": "caesar", "input": "Hello World", "key": 3, "mode": "encrypt" }
```
→ `{id, algorithm, result, steps[], metrics{time_ms, steps}, analysis{strengths, weaknesses, metrics}}`

Extra parameters per algorithm:
- `aes`: `{key_text, key_size (128|192|256), mode}` — encrypt returns `iv_hex:cipher_hex`, decrypt takes it back
- `rsa`: `{rsa_p, rsa_q, rsa_e, mode}` — encrypt returns space-separated ints, decrypt takes them back
- `md5` / `sha256`: no extra params
- `brute_force`: ciphertext input only — returns best-guess plaintext, last step holds all 25 attempts

## Analyze
`POST /api/analyze`
```json
{ "algorithm": "rsa", "parameters": { "rsa_p": 61, "rsa_q": 53 } }
```
→ `{algorithm, analysis}`

## History (JWT required)
- `GET /api/history` → last 50 (without steps)
- `GET /api/history/<id>` → with steps

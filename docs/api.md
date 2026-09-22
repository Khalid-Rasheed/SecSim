# SecSim API

## Health
`GET /api/health` → `{status: ok}`

## Algorithms
`GET /api/algorithms` → `[{id, type, family, kind, security, name{ar,en}, description{ar,en}, params, complexity}]`

`GET /api/taxonomy` → `{tabs: [{family, name{ar,en}, kinds: [{kind, name, items}]}], attacks: [...]}` — 3 tabs (symmetric | asymmetric | hashing) + attack lab.

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
- `caesar`: `{key, mode}` — classical symmetric
- `vigenere`: `{vigenere_key, mode}` — classical symmetric
- `playfair`: `{playfair_key, mode}` — classical symmetric (digraphs)
- `rc4`: `{rc4_key, mode}` — stream symmetric (encrypt→hex, decrypt←hex)
- `aes`: `{key_text, key_size (128|192|256), mode}` — encrypt returns `iv_hex:cipher_hex`, decrypt takes it back
- `rsa`: `{rsa_p, rsa_q, rsa_e, mode}` — encrypt returns space-separated ints, decrypt takes them back
- `diffie_hellman`: `{dh_p, dh_g, dh_a, dh_b}` — key exchange, returns shared secret (input text ignored)
- `elgamal`: `{elgamal_p, elgamal_g, elgamal_x, elgamal_k, mode}` — encrypt returns space-separated `c1,c2` pairs, decrypt takes them back
- `md5` / `sha1` / `sha256` / `sha512` / `sha3`: no extra params
- `pbkdf2`: `{pbkdf2_salt, pbkdf2_iterations}` — returns `salt$iterations$derived`
- `brute_force`: ciphertext input only — returns best-guess plaintext, last step holds all 25 attempts
- `vigenere_breaker`: Vigenère ciphertext input — returns recovered plaintext, last step holds length + key
- `dh_mitm`: `{dh_p, dh_g, dh_a, dh_b, mitm_e, mitm_f}` — message input, returns Eve's recovered plaintext
- `birthday_collision`: `{collision_bits (8..24)}` — returns the colliding pair, last step holds attempts vs theory
- `dictionary_attack`: MD5 digest (or any text) input — returns cracked word or the target with a warning

## Analyze
`POST /api/analyze`
```json
{ "algorithm": "rsa", "parameters": { "rsa_p": 61, "rsa_q": 53 } }
```
→ `{algorithm, analysis}`

## Security tests (live, per-input)
`POST /api/security-tests`
```json
{ "algorithm": "sha256", "input": "hello", "parameters": {} }
```
→ `{algorithm, tests: [{id, name{ar,en}, status: pass|warn|fail|info, summary{ar,en}, details}]}` — entropy, keyspace/crack estimate, avalanche % (hashes), collision bound, salt/iterations (passwords), MITM/frequency notes.

## Compare (side-by-side, not saved to history)
`POST /api/compare`
```json
{ "comparisons": [{"algorithm": "md5", "input": "hello"}, {"algorithm": "sha256", "input": "hello"}] }
```
→ `{results: [{algorithm, meta, input, result, result_preview, result_len, metrics, analysis_metrics, complexity, digest_bits, avalanche_pct}], verdict{ar,en}}` — 2..4 entries, per-entry `parameters` like /simulate (e.g. `{"key_size": 256}` for AES-256).

## History (JWT required)
- `GET /api/history` → last 50 (without steps)
- `GET /api/history/<id>` → with steps

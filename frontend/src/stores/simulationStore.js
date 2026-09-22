/**
 * Simulation store (Pinia), the heart of the frontend.
 *
 * Responsibilities:
 *   1. Catalogue — `algorithms` list + cached per-algorithm `details`
 *      (reference guides) fetched lazily by the Simulator brief card.
 *   2. Lab inputs — one field group per algorithm family (caesar key,
 *      AES key text/size, RSA p/q/e); run() maps them to the backend's
 *      flat payload (key / key_text / key_size / rsa_p / rsa_q / rsa_e).
 *   3. Step player — currentStep + play/stop timer consumed by
 *      VisualizationArea (transport + step dots + progress rail).
 *   4. Results — result/metrics/analysis/warning straight from
 *      POST /api/simulate, plus the JWT-protected `history`.
 */
import { defineStore } from 'pinia'
import api from '../services/api'

export const useSimulationStore = defineStore('simulation', {
  state: () => ({
    algorithms: [],
    taxonomy: null,
    algorithm: 'caesar',
    input: 'Hello World',
    key: 3,
    mode: 'encrypt',
    aesKeyText: 'secret',
    aesKeySize: 128,
    rsaP: 61,
    rsaQ: 53,
    rsaE: 17,
    vigenereKey: 'LEMON',
    rc4Key: 'secret',
    playfairKey: 'MONARCHY',
    dhP: 23,
    dhG: 5,
    dhA: 6,
    dhB: 15,
    mitmE: 3,
    mitmF: 7,
    collisionBits: 20,
    elgamalP: 2579,
    elgamalG: 2,
    elgamalX: 101,
    elgamalK: 7,
    pbkdf2Salt: '',
    pbkdf2Iterations: 1000,
    result: null,
    steps: [],
    metrics: null,
    analysis: null,
    securityTests: [],
    securityTestsLoading: false,
    compareResults: [],
    compareVerdict: null,
    compareLoading: false,
    // Bilingual {ar, en} input warning from the algorithm (currently
    // emitted by brute_force on its verdict step), or null.
    warning: null,
    currentStep: 0,
    playing: false,
    speed: 1000,
    loading: false,
    error: null,
    history: [],
    details: {},
    detailsLoading: false,
    _timer: null
  }),
  getters: {
    currentMeta: (s) => s.algorithms.find((a) => a.id === s.algorithm) || null,
    currentDetail: (s) => s.details[s.algorithm] || null
  },
  actions: {
    async fetchAlgorithms() {
      const { data } = await api.get('/algorithms')
      this.algorithms = data
      // Taxonomy is cheap and drives the 3-tab layout; fetch lazily
      // alongside the catalog but tolerate older backends.
      try {
        const t = await api.get('/taxonomy')
        this.taxonomy = t.data
      } catch {
        this.taxonomy = null
      }
    },
    async fetchDetails(id) {
      // Lazily loads + caches GET /api/algorithms/:id (full reference
      // guide). Cached per id so switching algorithms back and forth
      // never refetches.
      const algoId = id || this.algorithm
      if (this.details[algoId]) return this.details[algoId]
      this.detailsLoading = true
      try {
        const { data } = await api.get(`/algorithms/${algoId}`)
        this.details[algoId] = data
        return data
      } catch {
        return null
      } finally {
        this.detailsLoading = false
      }
    },
    fillExample() {
      // One-click demo inputs per algorithm (also used as sane defaults
      // for the auto-run when the user switches algorithms).
      this.mode = 'encrypt'
      if (this.algorithm === 'caesar') {
        this.input = 'Hello World'
        this.key = 3
      } else if (this.algorithm === 'vigenere') {
        this.input = 'Attack at dawn'
        this.vigenereKey = 'LEMON'
      } else if (this.algorithm === 'playfair') {
        this.input = 'HELLO'
        this.playfairKey = 'MONARCHY'
      } else if (this.algorithm === 'rc4') {
        this.input = 'Hello World'
        this.rc4Key = 'secret'
      } else if (this.algorithm === 'aes') {
        this.input = 'Secret message'
        this.aesKeyText = 'secret'
        this.aesKeySize = 128
      } else if (this.algorithm === 'rsa') {
        this.input = 'Hi'
        this.rsaP = 61
        this.rsaQ = 53
        this.rsaE = 17
      } else if (this.algorithm === 'diffie_hellman') {
        this.input = 'key-exchange'
        this.dhP = 23
        this.dhG = 5
        this.dhA = 6
        this.dhB = 15
      } else if (this.algorithm === 'elgamal') {
        this.input = 'Hi'
        this.elgamalP = 2579
        this.elgamalG = 2
        this.elgamalX = 101
        this.elgamalK = 7
      } else if (this.algorithm === 'pbkdf2') {
        this.input = 'correct-horse'
        this.pbkdf2Salt = ''
        this.pbkdf2Iterations = 1000
      } else if (this.algorithm === 'brute_force') {
        this.input = 'Khoor Zruog'
      } else if (this.algorithm === 'vigenere_breaker') {
        this.input =
          'NVKDGZKDOCSC UG GSI BFNNXUQR ZJ ESPFVQ QBXQGBVNEFWBY MZ HUP TDSFPROS BQ EPJRCWMFVPW MBQ TX DSYTIE CA XEFVRXEFWPD RAH FPGDSPJ JAF VEW EHEPRSHU'
      } else if (this.algorithm === 'dh_mitm') {
        this.input = 'HELLO'
        this.dhP = 23
        this.dhG = 5
        this.dhA = 6
        this.dhB = 15
        this.mitmE = 3
        this.mitmF = 7
      } else if (this.algorithm === 'birthday_collision') {
        this.input = 'secsim'
        this.collisionBits = 20
      } else if (this.algorithm === 'dictionary_attack') {
        // MD5("password") — in the 30-word list, cracks instantly.
        this.input = '5f4dcc3b5aa765d61d8327deb882cf99'
      } else {
        this.input = 'Hello World'
      }
      return this.run()
    },
    async run() {
      this.loading = true
      this.error = null
      this.warning = null
      try {
        const payload = { algorithm: this.algorithm, input: this.input, mode: this.mode }
        if (this.algorithm === 'caesar') payload.key = Number(this.key)
        if (this.algorithm === 'vigenere') payload.vigenere_key = this.vigenereKey
        if (this.algorithm === 'playfair') payload.playfair_key = this.playfairKey
        if (this.algorithm === 'rc4') payload.rc4_key = this.rc4Key
        if (this.algorithm === 'aes') {
          payload.key_text = this.aesKeyText
          payload.key_size = Number(this.aesKeySize)
        }
        if (this.algorithm === 'rsa') {
          payload.rsa_p = Number(this.rsaP)
          payload.rsa_q = Number(this.rsaQ)
          payload.rsa_e = Number(this.rsaE)
        }
        if (this.algorithm === 'diffie_hellman') {
          payload.dh_p = Number(this.dhP)
          payload.dh_g = Number(this.dhG)
          payload.dh_a = Number(this.dhA)
          payload.dh_b = Number(this.dhB)
        }
        if (this.algorithm === 'dh_mitm') {
          payload.dh_p = Number(this.dhP)
          payload.dh_g = Number(this.dhG)
          payload.dh_a = Number(this.dhA)
          payload.dh_b = Number(this.dhB)
          payload.mitm_e = Number(this.mitmE)
          payload.mitm_f = Number(this.mitmF)
        }
        if (this.algorithm === 'birthday_collision') {
          payload.collision_bits = Number(this.collisionBits)
        }
        if (this.algorithm === 'elgamal') {
          payload.elgamal_p = Number(this.elgamalP)
          payload.elgamal_g = Number(this.elgamalG)
          payload.elgamal_x = Number(this.elgamalX)
          payload.elgamal_k = Number(this.elgamalK)
        }
        if (this.algorithm === 'pbkdf2') {
          payload.pbkdf2_salt = this.pbkdf2Salt
          payload.pbkdf2_iterations = Number(this.pbkdf2Iterations)
        }
        const { data } = await api.post('/simulate', payload)
        this.result = data.result
        this.steps = data.steps
        this.metrics = data.metrics
        this.analysis = data.analysis
        // Warnings ride on the verdict (last) step snapshot, e.g.
        // brute_force flags non-ciphertext-looking input there.
        const last = data.steps?.length ? data.steps[data.steps.length - 1] : null
        this.warning = last?.snapshot?.warning || null
        this.currentStep = 0
        // Fire-and-forget live security tests (never blocks the bench).
        this.fetchSecurityTests(payload)
      } catch (e) {
        this.error = e.response?.data?.error || e.message
      } finally {
        this.loading = false
      }
    },
    async fetchSecurityTests(payload) {
      // POST /api/security-tests with the same parameters used for the
      // simulation, so avalanche/keyspace/entropy reflect live input.
      this.securityTestsLoading = true
      try {
        const body = {
          algorithm: this.algorithm,
          input: this.input,
          parameters: { ...(payload || {}) }
        }
        delete body.parameters.algorithm
        delete body.parameters.input
        delete body.parameters.mode
        const { data } = await api.post('/security-tests', body)
        this.securityTests = data.tests || []
      } catch {
        this.securityTests = []
      } finally {
        this.securityTestsLoading = false
      }
    },
    payloadFor(algoId, overrides = {}) {
      // Flat backend payload for any algorithm, mirroring run()'s
      // mapping so the compare panel reuses the bench's live inputs.
      const get = (key, fallback) =>
        overrides[key] !== undefined ? overrides[key] : this[key] ?? fallback
      const p = { algorithm: algoId, input: get('input', this.input), mode: this.mode }
      if (algoId === 'caesar') p.key = Number(get('key', this.key))
      if (algoId === 'vigenere') p.vigenere_key = get('vigenereKey', this.vigenereKey)
      if (algoId === 'playfair') p.playfair_key = get('playfairKey', this.playfairKey)
      if (algoId === 'rc4') p.rc4_key = get('rc4Key', this.rc4Key)
      if (algoId === 'aes') {
        p.key_text = get('aesKeyText', this.aesKeyText)
        p.key_size = Number(overrides.aesKeySize ?? this.aesKeySize)
      }
      if (algoId === 'rsa') {
        p.rsa_p = Number(get('rsaP', this.rsaP))
        p.rsa_q = Number(get('rsaQ', this.rsaQ))
        p.rsa_e = Number(get('rsaE', this.rsaE))
      }
      if (algoId === 'diffie_hellman') {
        p.dh_p = Number(get('dhP', this.dhP))
        p.dh_g = Number(get('dhG', this.dhG))
        p.dh_a = Number(get('dhA', this.dhA))
        p.dh_b = Number(get('dhB', this.dhB))
      }
      if (algoId === 'dh_mitm') {
        p.dh_p = Number(get('dhP', this.dhP))
        p.dh_g = Number(get('dhG', this.dhG))
        p.dh_a = Number(get('dhA', this.dhA))
        p.dh_b = Number(get('dhB', this.dhB))
        p.mitm_e = Number(get('mitmE', this.mitmE))
        p.mitm_f = Number(get('mitmF', this.mitmF))
      }
      if (algoId === 'birthday_collision') {
        p.collision_bits = Number(get('collisionBits', this.collisionBits))
      }
      if (algoId === 'elgamal') {
        p.elgamal_p = Number(get('elgamalP', this.elgamalP))
        p.elgamal_g = Number(get('elgamalG', this.elgamalG))
        p.elgamal_x = Number(get('elgamalX', this.elgamalX))
        p.elgamal_k = Number(get('elgamalK', this.elgamalK))
      }
      if (algoId === 'pbkdf2') {
        p.pbkdf2_salt = get('pbkdf2Salt', this.pbkdf2Salt)
        p.pbkdf2_iterations = Number(get('pbkdf2Iterations', this.pbkdf2Iterations))
      }
      return p
    },
    async fetchCompare(entries) {
      // entries: [{algorithm, overrides?}] — each entry's payload comes
      // from payloadFor() so presets (AES-128 vs 256) only override
      // what differs. Results are NOT saved to history.
      this.compareLoading = true
      this.compareResults = []
      this.compareVerdict = null
      try {
        const comparisons = entries.map((e) => {
          const flat = this.payloadFor(e.algorithm, e.overrides || {})
          const { algorithm, input: inputText, ...parameters } = flat
          delete parameters.mode
          return { algorithm, input: inputText, parameters }
        })
        const { data } = await api.post('/compare', { comparisons })
        this.compareResults = data.results || []
        this.compareVerdict = data.verdict || null
      } catch (e) {
        this.error = e.response?.data?.error || e.message
      } finally {
        this.compareLoading = false
      }
    },
    async fetchHistory() {
      // GET /history answers {total, limit, offset, items[]};
      // tolerate a bare array for backward compatibility.
      const { data } = await api.get('/history')
      this.history = Array.isArray(data) ? data : data.items || []
    },
    next() {
      if (this.currentStep < this.steps.length - 1) this.currentStep++
    },
    prev() {
      if (this.currentStep > 0) this.currentStep--
    },
    play() {
      if (this.playing || this.steps.length === 0) return
      this.playing = true
      this._timer = setInterval(() => {
        if (this.currentStep >= this.steps.length - 1) this.stop()
        else this.currentStep++
      }, this.speed)
    },
    stop() {
      this.playing = false
      if (this._timer) clearInterval(this._timer)
      this._timer = null
    },
    setSpeed(ms) {
      this.speed = ms
      if (this.playing) {
        this.stop()
        this.play()
      }
    }
  }
})

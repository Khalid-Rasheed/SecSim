/**
 * Simulation store — مخزن المحاكاة (Pinia), the heart of the frontend.
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
    algorithm: 'caesar',
    input: 'Hello World',
    key: 3,
    mode: 'encrypt',
    aesKeyText: 'secret',
    aesKeySize: 128,
    rsaP: 61,
    rsaQ: 53,
    rsaE: 17,
    result: null,
    steps: [],
    metrics: null,
    analysis: null,
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
      } else if (this.algorithm === 'aes') {
        this.input = 'Secret message'
        this.aesKeyText = 'secret'
        this.aesKeySize = 128
      } else if (this.algorithm === 'rsa') {
        this.input = 'Hi'
        this.rsaP = 61
        this.rsaQ = 53
        this.rsaE = 17
      } else if (this.algorithm === 'brute_force') {
        this.input = 'Khoor Zruog'
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
        if (this.algorithm === 'aes') {
          payload.key_text = this.aesKeyText
          payload.key_size = Number(this.aesKeySize)
        }
        if (this.algorithm === 'rsa') {
          payload.rsa_p = Number(this.rsaP)
          payload.rsa_q = Number(this.rsaQ)
          payload.rsa_e = Number(this.rsaE)
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
      } catch (e) {
        this.error = e.response?.data?.error || e.message
      } finally {
        this.loading = false
      }
    },
    async fetchHistory() {
      const { data } = await api.get('/history')
      this.history = data
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

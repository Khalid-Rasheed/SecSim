/**
 * Auth store (Pinia).
 *
 * Holds the JWT + user profile and mirrors them to localStorage so the
 * session survives reloads. The api service reads 'secsim_token' on every
 * request; logout() clears both copies. `isLoggedIn` gates /history and
 * the History/Profile views.
 */
import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('secsim_token') || null,
    user: JSON.parse(localStorage.getItem('secsim_user') || 'null')
  }),
  getters: {
    isLoggedIn: (s) => !!s.token
  },
  actions: {
    async register(email, password, name) {
      const { data } = await api.post('/auth/register', { email, password, name })
      this._save(data)
    },
    async login(email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      this._save(data)
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('secsim_token')
      localStorage.removeItem('secsim_user')
    },
    _save(data) {
      this.token = data.token
      this.user = data.user
      localStorage.setItem('secsim_token', data.token)
      localStorage.setItem('secsim_user', JSON.stringify(data.user))
    }
  }
})

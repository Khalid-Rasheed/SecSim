// Central HTTP client for the SecSim API.
//
// Auth model: a JWT (stored in localStorage by the auth store) is
// attached as `Authorization: Bearer <token>` on every request.
//
// Session expiry: the backend answers 401 (missing/invalid token) or
// 422 (expired/malformed token). When such a response arrives for a
// request that *carried* a token, the session is dead — so this
// interceptor clears the stored credentials, flags the expiry, and
// broadcasts `secsim:unauthorized`. App.vue listens for it, resets
// the auth store and routes to /login?expired=1 where Login.vue shows
// a clear "session expired" banner (no silent failures).
//
// The `Authorization` guard prevents login/register failures (which
// also return 401 but carry no token) from triggering a logout loop.
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('secsim_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const sentToken = Boolean(error.config?.headers?.Authorization)
    if ((status === 401 || status === 422) && sentToken) {
      localStorage.removeItem('secsim_token')
      localStorage.removeItem('secsim_user')
      localStorage.setItem('secsim_expired', '1')
      window.dispatchEvent(new CustomEvent('secsim:unauthorized'))
    }
    return Promise.reject(error)
  }
)

export default api

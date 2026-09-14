/**
 * SecSim entry point.
 *
 * Boot order (important): Pinia → Router → i18n → mount, so every view can
 * rely on stores, routes and translations from its first render.
 * The saved language is applied to <html> here (lang + dir) before
 * any component mounts, preventing an RTL/LTR flash on reload.
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import '@fortawesome/fontawesome-free/css/all.min.css'
import './assets/css/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')

const lang = localStorage.getItem('secsim_lang') || 'ar'
document.documentElement.lang = lang
document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'

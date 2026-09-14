/**
 * Internationalization — إدارة اللغتين.
 *
 * Arabic is the default locale (ar.json), English the fallback (en.json);
 * the choice persists in localStorage under 'secsim_lang'. Algorithm
 * content itself (titles, steps, guides) is NOT translated here — it
 * arrives bilingual ({ar, en}) from the backend API.
 */
import { createI18n } from 'vue-i18n'
import ar from './ar.json'
import en from './en.json'

const saved = localStorage.getItem('secsim_lang') || 'ar'

const i18n = createI18n({
  legacy: false,
  locale: saved,
  fallbackLocale: 'en',
  messages: { ar, en }
})

export default i18n

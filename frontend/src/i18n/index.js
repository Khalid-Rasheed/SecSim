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

<template>
  <header class="sticky top-0 z-50 bg-white/85 backdrop-blur-md border-b border-[rgba(15,23,42,0.08)]">
    <nav class="max-w-6xl mx-auto px-4 h-16 flex items-center gap-1">
      <router-link to="/" class="flex items-center gap-2.5 me-4">
        <span class="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-pop"
          style="background: linear-gradient(135deg, #0d9488, #0f766e)">
          <i class="fa-solid fa-lock text-sm"></i>
        </span>
        <span class="font-display font-extrabold text-lg tracking-tight text-mist" dir="ltr">SecSim<span class="text-teal-600">_</span></span>
      </router-link>

      <router-link to="/" class="navlink text-sm hidden sm:inline-block">
        <i class="fa-solid fa-house me-1.5 text-xs"></i>{{ $t('nav.home') }}
      </router-link>
      <router-link to="/simulator" class="navlink text-sm">
        <i class="fa-solid fa-flask me-1.5 text-xs"></i>{{ $t('nav.simulator') }}
      </router-link>
      <router-link to="/history" class="navlink text-sm">
        <i class="fa-solid fa-clock-rotate-left me-1.5 text-xs"></i>{{ $t('nav.history') }}
      </router-link>
      <router-link to="/profile" class="navlink text-sm hidden sm:inline-block">
        <i class="fa-solid fa-user me-1.5 text-xs"></i>{{ $t('nav.profile') }}
      </router-link>

      <span class="flex-1"></span>

      <button @click="toggleLang" class="btn-ghost text-xs px-3 py-2 font-bold" dir="ltr">
        <i class="fa-solid fa-language me-1 text-teal-700"></i>{{ locale === 'ar' ? 'EN' : 'عربي' }}
      </button>

      <template v-if="auth.isLoggedIn">
        <span class="hidden md:inline text-xs text-muted font-mono max-w-[180px] truncate" dir="ltr">{{ auth.user?.email }}</span>
        <button @click="auth.logout()" class="btn-ghost text-xs font-bold px-3 py-2">
          <i class="fa-solid fa-right-from-bracket me-1 text-teal-700"></i>{{ $t('nav.logout') }}
        </button>
      </template>
      <router-link v-else to="/login" class="btn-cipher text-xs font-bold px-4 py-2">
        <i class="fa-solid fa-right-to-bracket me-1"></i>{{ $t('nav.login') }}
      </router-link>
    </nav>
  </header>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../../stores/authStore'
const { locale } = useI18n()
const auth = useAuthStore()
function toggleLang() {
  const next = locale.value === 'ar' ? 'en' : 'ar'
  locale.value = next
  localStorage.setItem('secsim_lang', next)
  document.documentElement.lang = next
  document.documentElement.dir = next === 'ar' ? 'rtl' : 'ltr'
}
</script>

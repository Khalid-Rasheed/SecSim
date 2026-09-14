<template>
  <div class="max-w-5xl mx-auto px-4 py-10 md:py-14">
    <div class="panel overflow-hidden !rounded-3xl grid lg:grid-cols-2">
      <!-- SIDE / BRANDING -->
      <div
        class="relative overflow-hidden p-8 md:p-10 text-white flex flex-col justify-between min-h-[320px]"
        style="background: linear-gradient(150deg, #0d9488 0%, #0f766e 55%, #115e59 100%)"
      >
        <!-- decorative shapes -->
        <div class="blob w-64 h-64 bg-white/20 -top-20 -start-20"></div>
        <div class="blob w-72 h-72 bg-amber-300/30 -bottom-24 -end-16"></div>
        <div
          class="absolute inset-0 opacity-[0.12]"
          style="background-image: radial-gradient(#fff 1.2px, transparent 1.2px); background-size: 20px 20px"
        ></div>

        <div class="relative">
          <div class="flex items-center gap-3 mb-8">
            <span
              class="w-11 h-11 rounded-2xl bg-white/15 border border-white/30 backdrop-blur flex items-center justify-center"
            >
              <i class="fa-solid fa-lock text-white text-lg"></i>
            </span>
            <div>
              <p class="font-display font-extrabold text-xl leading-none" dir="ltr">
                SecSim<span class="text-amber-300">_</span>
              </p>
              <p class="text-teal-50/80 text-xs mt-1">{{ $t('hero.eyebrow') }}</p>
            </div>
          </div>

          <h2 class="font-display text-2xl md:text-3xl font-extrabold leading-snug mb-3">
            {{ $t('auth.side_title') }}
          </h2>
          <p class="text-teal-50/90 text-sm leading-relaxed mb-8 max-w-sm">{{ $t('auth.side_sub') }}</p>

          <ul class="space-y-3">
            <li
              v-for="(p, i) in $tm('auth.points')"
              :key="i"
              class="flex items-start gap-3 bg-white/10 border border-white/20 rounded-2xl px-4 py-3 backdrop-blur"
            >
              <span
                class="w-9 h-9 rounded-xl bg-white/15 border border-white/25 flex items-center justify-center shrink-0"
              >
                <i :class="[$rt(p.icon), 'text-white text-sm']"></i>
              </span>
              <span>
                <span class="block text-sm font-bold">{{ $rt(p.title) }}</span>
                <span class="block text-teal-50/85 text-xs mt-0.5">{{ $rt(p.text) }}</span>
              </span>
            </li>
          </ul>
        </div>

        <div class="relative mt-8 flex flex-wrap items-center gap-2">
          <span
            class="inline-flex items-center gap-1.5 bg-white text-teal-800 text-xs font-extrabold px-3 py-1.5 rounded-full"
            dir="ltr"
          >
            <i class="fa-solid fa-code-branch"></i> {{ $t('footer.badge') }}
          </span>
          <span class="text-teal-50/90 text-xs">{{ $t('auth.opensource') }}</span>
        </div>
      </div>

      <!-- FORM -->
      <div class="p-6 md:p-10 bg-white">
        <div
          class="grid grid-cols-2 gap-1 p-1 rounded-2xl bg-panel2 border border-[rgba(15,23,42,0.08)] mb-6"
        >
          <button
            :class="[
              'py-2.5 rounded-xl text-sm font-bold transition',
              mode === 'login'
                ? 'bg-white shadow-card text-teal-700 border border-[rgba(15,23,42,0.08)]'
                : 'text-muted hover:text-mist'
            ]"
            @click="mode = 'login'"
          >
            <i class="fa-solid fa-right-to-bracket me-1.5"></i>{{ $t('auth.login') }}
          </button>
          <button
            :class="[
              'py-2.5 rounded-xl text-sm font-bold transition',
              mode === 'register'
                ? 'bg-white shadow-card text-teal-700 border border-[rgba(15,23,42,0.08)]'
                : 'text-muted hover:text-mist'
            ]"
            @click="mode = 'register'"
          >
            <i class="fa-solid fa-user-plus me-1.5"></i>{{ $t('auth.register') }}
          </button>
        </div>

        <h1 class="font-display text-2xl font-extrabold text-mist">
          {{ mode === 'login' ? $t('auth.login_title') : $t('auth.register_title') }}
        </h1>
        <p class="text-muted text-sm mt-1 mb-6">
          {{ mode === 'login' ? $t('auth.login_desc') : $t('auth.register_desc') }}
        </p>

        <div
          v-if="expiredNotice"
          class="flex items-start gap-2 bg-amber-50 border border-amber-300 text-amber-800 text-xs font-semibold rounded-xl px-3.5 py-3 mb-4"
        >
          <i class="fa-solid fa-clock-rotate-left mt-0.5 shrink-0"></i>
          <span>{{ $t('auth.session_expired') }}</span>
        </div>

        <form class="space-y-4" @submit.prevent="submit">
          <div v-if="mode === 'register'">
            <label class="block text-xs font-bold text-mist mb-1.5">{{ $t('auth.name') }}</label>
            <div class="relative">
              <i
                class="fa-solid fa-user absolute top-1/2 -translate-y-1/2 start-3.5 text-slate-400 text-sm pointer-events-none"
              ></i>
              <input
                v-model="name"
                class="field w-full ps-10 pe-3 py-3 text-sm"
                autocomplete="name"
                :placeholder="locale === 'ar' ? 'مثال: سارة أحمد' : 'e.g. Sara Ahmed'"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-mist mb-1.5">{{ $t('auth.email') }}</label>
            <div class="relative">
              <i
                class="fa-solid fa-envelope absolute top-1/2 -translate-y-1/2 start-3.5 text-slate-400 text-sm pointer-events-none"
              ></i>
              <input
                v-model="email"
                type="email"
                required
                class="field w-full ps-10 pe-3 py-3 text-sm font-mono"
                dir="ltr"
                autocomplete="email"
                placeholder="you@mail.com"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-mist mb-1.5">{{ $t('auth.password') }}</label>
            <div class="relative">
              <i
                class="fa-solid fa-key absolute top-1/2 -translate-y-1/2 start-3.5 text-slate-400 text-sm pointer-events-none"
              ></i>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                minlength="8"
                class="field w-full ps-10 pe-16 py-3 text-sm font-mono"
                dir="ltr"
                autocomplete="current-password"
                placeholder="••••••••"
              />
              <button
                type="button"
                class="absolute top-1/2 -translate-y-1/2 end-2.5 text-[0.72rem] font-bold text-teal-700 hover:text-teal-800 bg-teal-700/10 hover:bg-teal-700/15 rounded-lg px-2.5 py-1.5 transition"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? $t('auth.hide') : $t('auth.show') }}
              </button>
            </div>
            <p v-if="mode === 'register'" class="text-[0.7rem] text-muted mt-1.5">
              <i class="fa-solid fa-circle-info me-1"></i>{{ $t('auth.password_hint') }}
            </p>
          </div>

          <div
            v-if="error"
            class="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-xs font-semibold rounded-xl px-3.5 py-3"
          >
            <i class="fa-solid fa-circle-exclamation mt-0.5 shrink-0"></i>
            <span>{{ error }}</span>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="btn-cipher w-full py-3.5 text-sm disabled:opacity-60"
          >
            <i v-if="loading" class="fa-solid fa-circle-notch fa-spin me-2"></i>
            <i v-else class="fa-solid fa-check me-2"></i>
            {{ loading ? $t('auth.loading') : $t('auth.submit') }}
          </button>
        </form>

        <div class="hairline-t mt-6 pt-5 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p class="text-[0.72rem] text-muted flex items-center gap-1.5">
            <i class="fa-solid fa-lock text-teal-600"></i>{{ $t('auth.secure') }}
          </p>
          <router-link
            to="/"
            class="text-xs font-bold text-teal-700 hover:text-teal-800 hover:underline shrink-0"
          >
            <i class="fa-solid fa-arrow-right text-[0.65rem] me-1 rtl:rotate-180"></i>{{ $t('auth.back') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/authStore'

const { locale } = useI18n()
const mode = ref('login')
const email = ref('')
const password = ref('')
const name = ref('')
const error = ref(null)
const loading = ref(false)
const showPassword = ref(false)
// True when arriving via /login?expired=1 (or the expiry flag left by
// the API interceptor) — shows the "session expired" banner below.
const expiredNotice = ref(false)
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

onMounted(() => {
  if (route.query.expired === '1' || localStorage.getItem('secsim_expired') === '1') {
    expiredNotice.value = true
  }
})

async function submit() {
  error.value = null
  loading.value = true
  try {
    if (mode.value === 'login') await auth.login(email.value, password.value)
    else await auth.register(email.value, password.value, name.value)
    // Fresh login: clear any stale expiry flag/notice.
    localStorage.removeItem('secsim_expired')
    expiredNotice.value = false
    router.push('/simulator')
  } catch (e) {
    error.value = e.response?.data?.error || e.message
  } finally {
    loading.value = false
  }
}
</script>

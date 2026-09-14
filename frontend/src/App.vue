<template>
  <Navbar />
  <main class="min-h-screen bg-ink lab-grid">
    <router-view />
  </main>
  <footer class="bg-white border-t border-[rgba(15,23,42,0.08)]">
    <div class="max-w-6xl mx-auto px-4 pt-12 pb-6">
      <div class="grid gap-10 md:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
        <!-- BRAND -->
        <div>
          <div class="flex items-center gap-2.5 mb-4">
            <span
              class="w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-pop"
              style="background: linear-gradient(135deg, #0d9488, #0f766e)"
            >
              <i class="fa-solid fa-lock"></i>
            </span>
            <span class="font-display font-extrabold text-xl text-mist" dir="ltr"
              >SecSim<span class="text-teal-600">_</span></span
            >
            <span
              class="inline-flex items-center gap-1 bg-teal-700/10 text-teal-800 border border-teal-700/20 text-[0.68rem] font-extrabold px-2.5 py-1 rounded-full"
              dir="ltr"
            >
              <i class="fa-solid fa-code-branch text-[0.6rem]"></i>{{ $t('footer.badge') }}
            </span>
          </div>
          <p class="font-bold text-mist text-sm mb-1.5">{{ $t('footer.tag') }}</p>
          <p class="text-muted text-[0.83rem] leading-relaxed mb-4">{{ $t('footer.desc') }}</p>
          <p
            class="inline-flex items-center gap-1.5 text-[0.72rem] font-bold text-amber-700 bg-amber-500/10 border border-amber-500/25 rounded-full px-3 py-1.5"
          >
            <i class="fa-solid fa-scale-balanced"></i>{{ $t('footer.license') }}
          </p>
        </div>

        <!-- QUICK LINKS -->
        <div>
          <h4 class="font-display font-extrabold text-sm text-mist mb-4">{{ $t('footer.nav_title') }}</h4>
          <ul class="space-y-2.5 text-sm">
            <li>
              <router-link to="/" class="text-muted hover:text-teal-700 font-semibold transition">
                <i class="fa-solid fa-house text-[0.65rem] me-2 text-teal-600"></i>{{ $t('nav.home') }}
              </router-link>
            </li>
            <li>
              <router-link to="/simulator" class="text-muted hover:text-teal-700 font-semibold transition">
                <i class="fa-solid fa-flask text-[0.65rem] me-2 text-teal-600"></i>{{ $t('nav.simulator') }}
              </router-link>
            </li>
            <li>
              <router-link to="/history" class="text-muted hover:text-teal-700 font-semibold transition">
                <i class="fa-solid fa-clock-rotate-left text-[0.65rem] me-2 text-teal-600"></i
                >{{ $t('nav.history') }}
              </router-link>
            </li>
            <li>
              <router-link to="/login" class="text-muted hover:text-teal-700 font-semibold transition">
                <i class="fa-solid fa-right-to-bracket text-[0.65rem] me-2 text-teal-600"></i
                >{{ $t('nav.login') }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- ALGORITHMS -->
        <div>
          <h4 class="font-display font-extrabold text-sm text-mist mb-4">{{ $t('footer.algos_title') }}</h4>
          <ul class="space-y-2.5 text-sm">
            <li v-for="a in algos" :key="a">
              <router-link
                to="/simulator"
                class="inline-flex items-center gap-2 text-muted hover:text-teal-700 font-semibold transition"
              >
                <span
                  class="font-mono text-[0.7rem] bg-panel2 border border-[rgba(15,23,42,0.08)] rounded-md px-1.5 py-0.5"
                  dir="ltr"
                  >{{ a }}</span
                >
              </router-link>
            </li>
          </ul>
        </div>

        <!-- OPEN SOURCE -->
        <div
          class="rounded-2xl bg-gradient-to-br from-teal-700/[0.07] to-amber-500/[0.08] border border-[rgba(15,23,42,0.08)] p-5"
        >
          <h4 class="font-display font-extrabold text-sm text-mist mb-2">
            <i class="fa-solid fa-code-branch text-teal-700 me-1.5"></i>{{ $t('footer.open_title') }}
          </h4>
          <p class="text-muted text-[0.8rem] leading-relaxed mb-4">{{ $t('footer.open_text') }}</p>
          <div class="flex items-center gap-2 text-[0.72rem] font-bold text-teal-800">
            <span
              class="w-7 h-7 rounded-lg bg-teal-700/10 border border-teal-700/20 flex items-center justify-center"
            >
              <i class="fa-solid fa-unlock"></i>
            </span>
            <span dir="ltr">MIT · Open Code</span>
          </div>
        </div>
      </div>

      <div
        class="hairline-t mt-10 pt-5 flex flex-col sm:flex-row items-center gap-2 justify-between text-xs text-muted"
      >
        <span class="font-mono" dir="ltr">SecSim © 2026 · {{ $t('footer.rights') }}</span>
        <span class="font-semibold"
          ><i class="fa-solid fa-heart text-red-400 me-1.5"></i>{{ $t('footer.made') }}</span
        >
      </div>
    </div>
  </footer>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Navbar from './components/common/Navbar.vue'
import { useAuthStore } from './stores/authStore'

const algos = ['caesar', 'aes', 'rsa', 'sha256']
const router = useRouter()
const route = useRoute()

// Global session-expiry handler: fired by the API interceptor when a
// request carrying a token gets 401/422 (expired or revoked JWT).
// Syncs the Pinia store (the interceptor already wiped localStorage)
// and routes to login with ?expired=1 so the user sees WHY they were
// logged out instead of a silent failure.
function onUnauthorized() {
  useAuthStore().logout()
  if (route.path !== '/login') router.push({ path: '/login', query: { expired: '1' } })
}

onMounted(() => window.addEventListener('secsim:unauthorized', onUnauthorized))
onUnmounted(() => window.removeEventListener('secsim:unauthorized', onUnauthorized))
</script>

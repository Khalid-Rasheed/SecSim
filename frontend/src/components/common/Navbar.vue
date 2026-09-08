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

      <!-- ALGORITHMS DROPDOWN: Encryption (symmetric/asymmetric tree) + hashing + attacks -->
      <div class="relative hidden sm:inline-block" @keydown.escape="closeMenu">
        <button @click="toggleMenu" :aria-expanded="open" aria-haspopup="true"
          :class="['navlink text-sm font-semibold inline-flex items-center', open ? '!text-teal-700 bg-teal-700/10' : '']">
          <i class="fa-solid fa-layer-group me-1.5 text-xs"></i>{{ $t('nav.algorithms') }}
          <i :class="['fa-solid fa-chevron-down ms-1.5 text-[0.6rem] transition-transform', open ? 'rotate-180' : '']"></i>
        </button>

        <div v-if="open" class="absolute start-0 top-full mt-2 w-[21rem] max-w-[90vw] bg-white border border-[rgba(15,23,42,0.1)] rounded-2xl shadow-card p-2 z-50 max-h-[70vh] overflow-y-auto">
          <p v-if="menuLoading" class="text-xs text-muted px-3 py-4 text-center">
            <i class="fa-solid fa-circle-notch fa-spin me-1.5"></i>{{ $t('sim.brief_loading') }}
          </p>
          <template v-else>
            <!-- ENCRYPTION: symmetric / asymmetric families, each grouped by kind -->
            <p class="px-3 pt-2 pb-1 text-[0.68rem] font-extrabold text-mist uppercase tracking-wide">
              <i class="fa-solid fa-lock text-teal-600 me-1.5"></i>{{ $t('tax.encryption') }}
            </p>
            <div v-for="fam in menuEncryption" :key="fam.family" class="mb-1">
              <p class="px-3 py-1 text-[0.7rem] font-bold text-teal-700">{{ $t('tax.' + fam.family) }}</p>
              <div v-for="g in fam.kinds" :key="g.kind" class="mb-1">
                <p class="px-3 text-[0.65rem] text-muted font-semibold">{{ $t('tax.' + g.kind) }}</p>
                <router-link v-for="a in g.items" :key="a.id"
                  :to="{ path: '/simulator', query: { algo: a.id } }" @click="closeMenu"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-teal-700/5 transition">
                  <i :class="[algoIcon(a.type), 'text-teal-600 text-xs w-4 text-center']"></i>
                  <span class="font-mono text-xs font-bold text-mist" dir="ltr">{{ a.id }}</span>
                  <span class="text-[0.7rem] text-muted truncate">{{ a.name?.[locale] || '' }}</span>
                </router-link>
              </div>
            </div>

            <!-- HASHING + ATTACKS: flat groups -->
            <div v-for="sec in menuFlat" :key="sec.key">
              <p class="px-3 pt-2 pb-1 text-[0.68rem] font-extrabold text-mist uppercase tracking-wide">
                <i :class="[sec.icon, 'me-1.5', sec.color]"></i>{{ $t('tax.' + sec.key) }}
              </p>
              <router-link v-for="a in sec.items" :key="a.id"
                :to="{ path: '/simulator', query: { algo: a.id } }" @click="closeMenu"
                class="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-teal-700/5 transition">
                <i :class="[algoIcon(a.type), 'text-teal-600 text-xs w-4 text-center']"></i>
                <span class="font-mono text-xs font-bold text-mist" dir="ltr">{{ a.id }}</span>
                <span class="text-[0.7rem] text-muted truncate">{{ a.name?.[locale] || '' }}</span>
              </router-link>
            </div>
          </template>
        </div>
      </div>

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

  <!-- Invisible click-catcher: closes the dropdown on any outside click.
       Rendered below the panel (z-40 vs panel z-50) so items stay clickable. -->
  <div v-if="open" class="fixed inset-0 z-40" @click="closeMenu"></div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../../stores/authStore'
import { useSimulationStore } from '../../stores/simulationStore'

const { locale } = useI18n()
const auth = useAuthStore()
const sim = useSimulationStore()
const route = useRoute()

// Dropdown open state. Items are lazy-loaded from /api/algorithms on
// first open so the navbar costs zero requests for direct visitors.
const open = ref(false)
const menuLoading = ref(false)

function algoIcon(type) {
  if (type === 'attack') return 'fa-solid fa-burst'
  if (type === 'hashing') return 'fa-solid fa-fingerprint'
  return 'fa-solid fa-key'
}

async function toggleMenu() {
  open.value = !open.value
  if (open.value && !sim.algorithms.length) {
    menuLoading.value = true
    try {
      await sim.fetchAlgorithms()
    } catch {
      /* offline: menu simply stays empty */
    } finally {
      menuLoading.value = false
    }
  }
}

function closeMenu() {
  open.value = false
}

// Group encryption entries: family (symmetric/asymmetric) → kind
// (stream/block/factorization/...) → items, preserving catalog order.
const menuEncryption = computed(() => {
  const enc = sim.algorithms.filter((a) => a.type === 'encryption')
  return ['symmetric', 'asymmetric']
    .map((family) => {
      const members = enc.filter((a) => a.family === family)
      if (!members.length) return null
      const kinds = []
      for (const a of members) {
        let g = kinds.find((k) => k.kind === a.kind)
        if (!g) {
          g = { kind: a.kind || 'other', items: [] }
          kinds.push(g)
        }
        g.items.push(a)
      }
      return { family, kinds }
    })
    .filter(Boolean)
})

// Non-encryption sections render flat (no subtype tree).
const menuFlat = computed(() => [
  {
    key: 'hashing',
    icon: 'fa-solid fa-fingerprint',
    color: 'text-teal-600',
    items: sim.algorithms.filter((a) => a.type === 'hashing')
  },
  {
    key: 'attack',
    icon: 'fa-solid fa-burst',
    color: 'text-keyamber',
    items: sim.algorithms.filter((a) => a.type === 'attack')
  }
])

function toggleLang() {
  const next = locale.value === 'ar' ? 'en' : 'ar'
  locale.value = next
  localStorage.setItem('secsim_lang', next)
  document.documentElement.lang = next
  document.documentElement.dir = next === 'ar' ? 'rtl' : 'ltr'
}

// Navigating anywhere collapses the menu (covers dropdown item clicks
// that stay on the same view with a different ?algo= query).
watch(
  () => route.fullPath,
  () => {
    open.value = false
  }
)
</script>

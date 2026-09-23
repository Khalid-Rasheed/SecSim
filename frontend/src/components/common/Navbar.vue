<template>
  <header class="sticky top-0 z-50 bg-white/85 backdrop-blur-md border-b border-[rgba(15,23,42,0.08)]">
    <nav class="max-w-6xl mx-auto px-4 h-16 flex items-center gap-1">
      <router-link to="/" class="flex items-center gap-2.5 me-4">
        <span
          class="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-pop"
          style="background: linear-gradient(135deg, #0d9488, #0f766e)"
        >
          <i class="fa-solid fa-lock text-sm"></i>
        </span>
        <span class="font-display font-extrabold text-lg tracking-tight text-mist" dir="ltr"
          >SecSim<span class="text-teal-600">_</span></span
        >
      </router-link>

      <router-link to="/" class="navlink text-sm hidden sm:inline-block">
        <i class="fa-solid fa-house me-1.5 text-xs"></i>{{ $t('nav.home') }}
      </router-link>
      <router-link to="/simulator" class="navlink text-sm">
        <i class="fa-solid fa-flask me-1.5 text-xs"></i>{{ $t('nav.simulator') }}
      </router-link>
      <router-link to="/learn" class="navlink text-sm hidden sm:inline-block">
        <i class="fa-solid fa-route me-1.5 text-xs"></i>{{ $t('ux.learn.eyebrow') }}
      </router-link>
      <router-link to="/help" class="navlink text-sm hidden sm:inline-block">
        <i class="fa-solid fa-circle-question me-1.5 text-xs"></i>{{ $t('nav.help') }}
      </router-link>

      <!-- ALGORITHMS DROPDOWN (visible on mobile too: beginners on
           phones lost the whole menu when it was sm+ only). -->
      <div class="relative inline-block" @keydown.escape="closeMenu">
        <button
          :aria-expanded="open"
          aria-haspopup="true"
          :class="[
            'navlink text-sm font-semibold inline-flex items-center',
            open ? '!text-teal-700 bg-teal-700/10' : ''
          ]"
          @click="toggleMenu"
        >
          <i class="fa-solid fa-layer-group me-1.5 text-xs"></i>{{ $t('nav.algorithms') }}
          <i
            :class="[
              'fa-solid fa-chevron-down ms-1.5 text-[0.6rem] transition-transform',
              open ? 'rotate-180' : ''
            ]"
          ></i>
        </button>

        <div
          v-if="open"
          class="absolute start-0 top-full mt-2 w-[21rem] max-w-[90vw] bg-white border border-[rgba(15,23,42,0.1)] rounded-2xl shadow-card p-2 z-50 max-h-[70vh] overflow-y-auto"
        >
          <p v-if="menuLoading" class="text-xs text-muted px-3 py-4 text-center">
            <i class="fa-solid fa-circle-notch fa-spin me-1.5"></i>{{ $t('sim.brief_loading') }}
          </p>
          <template v-else>
            <!-- Instant search across ids + bilingual names (19 items). -->
            <div class="px-2 pt-1 pb-2 sticky top-0 bg-white">
              <div class="relative">
                <i
                  class="fa-solid fa-magnifying-glass absolute start-3 top-1/2 -translate-y-1/2 text-muted text-xs"
                ></i>
                <input
                  v-model="query"
                  class="field w-full ps-8 pe-3 py-2 text-xs"
                  :placeholder="$t('ux.search')"
                  dir="auto"
                />
              </div>
            </div>
            <p v-if="!anythingVisible" class="text-xs text-muted px-3 py-4 text-center">
              {{ $t('ux.no_results') }}
            </p>
            <!-- 3 TABS: symmetric / asymmetric / hashing (each grouped by kind) -->
            <div v-for="fam in menuTabs" v-show="famVisible(fam)" :key="fam.family" class="mb-1">
              <p class="px-3 pt-2 pb-1 text-[0.68rem] font-extrabold text-mist uppercase tracking-wide">
                <i :class="[fam.icon, 'me-1.5', fam.color]"></i>{{ $t('tax.' + fam.family) }}
              </p>
              <div v-for="g in fam.kinds" v-show="groupVisible(g)" :key="g.kind" class="mb-1">
                <p class="px-3 text-[0.65rem] text-muted font-semibold">{{ $t('tax.' + g.kind) }}</p>
                <router-link
                  v-for="a in g.items"
                  v-show="matches(a)"
                  :key="a.id"
                  :to="{ path: '/simulator', query: { algo: a.id } }"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-teal-700/5 transition"
                  @click="closeMenu"
                >
                  <i :class="[algoIcon(a.type), 'text-teal-600 text-xs w-4 text-center']"></i>
                  <span class="font-mono text-xs font-bold text-mist" dir="ltr">{{ a.id }}</span>
                  <span class="text-[0.7rem] text-muted truncate">{{ a.name?.[locale] || '' }}</span>
                  <span
                    v-if="a.security === 'broken' || a.security === 'secure'"
                    :class="[
                      'ms-auto text-[0.6rem] font-mono px-1.5 py-px rounded border shrink-0',
                      a.security === 'secure'
                        ? 'text-teal-700 border-teal-600/30 bg-teal-700/5'
                        : 'text-red-600 border-red-500/30 bg-red-500/5'
                    ]"
                    >{{ $t('alg.badge_' + a.security) }}</span
                  >
                </router-link>
              </div>
            </div>

            <!-- ATTACK LAB -->
            <div v-if="visibleAttacks.length">
              <p class="px-3 pt-2 pb-1 text-[0.68rem] font-extrabold text-mist uppercase tracking-wide">
                <i class="fa-solid fa-burst me-1.5 text-keyamber"></i>{{ $t('tax.attack_lab') }}
              </p>
              <router-link
                v-for="a in visibleAttacks"
                :key="a.id"
                :to="{ path: '/simulator', query: { algo: a.id } }"
                class="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-teal-700/5 transition"
                @click="closeMenu"
              >
                <i :class="[algoIcon(a.type), 'text-teal-600 text-xs w-4 text-center']"></i>
                <span class="font-mono text-xs font-bold text-mist" dir="ltr">{{ a.id }}</span>
                <span class="text-[0.7rem] text-muted truncate">{{ a.name?.[locale] || '' }}</span>
              </router-link>
            </div>

            <!-- HELP -->
            <router-link
              :to="{ path: '/help' }"
              class="flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-teal-700/5 transition"
              @click="closeMenu"
            >
              <i class="fa-solid fa-circle-question text-teal-600 text-xs w-4 text-center"></i>
              <span class="font-mono text-xs font-bold text-mist" dir="ltr">{{ $t('nav.help') }}</span>
            </router-link>
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

      <button class="btn-ghost text-xs px-3 py-2 font-bold" dir="ltr" @click="toggleLang">
        <i class="fa-solid fa-language me-1 text-teal-700"></i>{{ locale === 'ar' ? 'EN' : 'عربي' }}
      </button>

      <template v-if="auth.isLoggedIn">
        <span class="hidden md:inline text-xs text-muted font-mono max-w-[180px] truncate" dir="ltr">{{
          auth.user?.email
        }}</span>
        <button class="btn-ghost text-xs font-bold px-3 py-2" @click="auth.logout()">
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
  query.value = ''
}

// Three tabs (symmetric / asymmetric / hashing), each grouped by kind,
// preserving catalog order. Prefers the /api/taxonomy tree when loaded,
// falls back to client-side grouping for older backends.
const menuTabs = computed(() => {
  if (sim.taxonomy?.tabs?.length) return sim.taxonomy.tabs.map((t) => ({
    family: t.family,
    icon:
      t.family === 'symmetric'
        ? 'fa-solid fa-key'
        : t.family === 'asymmetric'
          ? 'fa-solid fa-key'
          : 'fa-solid fa-fingerprint',
    color: 'text-teal-600',
    kinds: t.kinds
  }))
  const tabs = []
  const conf = [
    { family: 'symmetric', icon: 'fa-solid fa-key', color: 'text-teal-600' },
    { family: 'asymmetric', icon: 'fa-solid fa-key', color: 'text-teal-600' },
    { family: 'hashing', icon: 'fa-solid fa-fingerprint', color: 'text-teal-600' }
  ]
  for (const c of conf) {
    const members = sim.algorithms.filter((a) => a.family === c.family)
    if (!members.length) continue
    const kinds = []
    for (const a of members) {
      let g = kinds.find((k) => k.kind === (a.kind || 'other'))
      if (!g) {
        g = { kind: a.kind || 'other', items: [] }
        kinds.push(g)
      }
      g.items.push(a)
    }
    tabs.push({ ...c, kinds })
  }
  return tabs
})

const menuAttacks = computed(() => {
  if (sim.taxonomy?.attacks?.length) return sim.taxonomy.attacks
  return sim.algorithms.filter((a) => a.type === 'attack')
})

// Instant menu search (id + bilingual name). Helpers below hide
// non-matching items / groups so the 19-entry menu stays scannable.
const query = ref('')
function matches(a) {
  const q = query.value.trim().toLowerCase()
  if (!q) return true
  const name = String(a.name?.[locale.value] || a.name?.en || '').toLowerCase()
  return a.id.toLowerCase().includes(q) || name.includes(q)
}
function groupVisible(g) {
  return g.items.some(matches)
}
function famVisible(fam) {
  return fam.kinds.some(groupVisible)
}
const visibleAttacks = computed(() => menuAttacks.value.filter(matches))
const anythingVisible = computed(
  () => menuTabs.value.some(famVisible) || visibleAttacks.value.length > 0
)

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

<!--
  LearnPath — guided 5-station path for absolute beginners.
  Each station: one algorithm to watch + its attack to break, with
  deep links (?algo=) into the simulator and the reference guide.
  Progress (visited stations) persists in localStorage under
  'secsim_learn' — no backend, no account needed. Stations and
  glossary text come from ux.learn.* / ux.glossary (both languages).
-->
<template>
  <div class="max-w-4xl mx-auto px-4 py-10">
    <p class="eyebrow mb-2"><i class="fa-solid fa-route me-2"></i>{{ $t('ux.learn.eyebrow') }}</p>
    <h1 class="font-display text-3xl font-bold mb-1">{{ $t('ux.learn.title') }}</h1>
    <p class="text-muted text-sm mb-6">{{ $t('ux.learn.subtitle') }}</p>

    <!-- progress -->
    <div class="panel p-4 mb-6 flex items-center gap-3">
      <i class="fa-solid fa-flag-checkered text-cipher"></i>
      <div class="flex-1 h-2 rounded bg-panel2 overflow-hidden" dir="ltr">
        <div
          class="h-full bg-cipher transition-all"
          :style="{ width: (doneCount / (stations.length || 1)) * 100 + '%' }"
        ></div>
      </div>
      <span class="font-mono text-xs text-muted" dir="ltr">{{ doneCount }}/{{ stations.length }}</span>
      <span class="text-xs text-muted">{{ $t('ux.learn.progress') }}</span>
    </div>

    <!-- stations -->
    <h2 class="font-semibold text-sm mb-3">
      <i class="fa-solid fa-list-ol text-cipher me-2"></i>{{ $t('ux.learn.stations_title') }}
    </h2>
    <div class="space-y-3 mb-8">
      <div
        v-for="(s, i) in stations"
        :key="s.algo"
        class="panel p-5 flex gap-4 items-start"
        :class="done[i] ? 'border-cipher/40' : ''"
      >
        <button
          class="w-9 h-9 rounded-xl border flex items-center justify-center shrink-0 transition"
          :class="
            done[i]
              ? 'bg-cipher text-white border-cipher'
              : 'bg-panel2 border-[rgba(148,163,184,0.25)] text-muted hover:border-cipher'
          "
          :title="$t('ux.learn.progress')"
          @click="toggle(i)"
        >
          <i v-if="done[i]" class="fa-solid fa-check text-sm"></i>
          <span v-else class="font-display font-bold text-sm" dir="ltr">{{ i + 1 }}</span>
        </button>
        <div class="flex-1">
          <h3 class="font-semibold mb-1">
            {{ $rtStation(s, 'title') }}
            <span v-if="done[i]" class="text-cipher text-xs ms-2"
              ><i class="fa-solid fa-circle-check"></i
            ></span>
          </h3>
          <p class="text-sm text-muted leading-relaxed mb-3">{{ $rtStation(s, 'goal') }}</p>
          <div class="flex gap-2 flex-wrap">
            <router-link
              :to="{ path: '/simulator', query: { algo: s.algo } }"
              class="btn-cipher px-4 py-2 text-xs"
              @click="mark(i)"
            >
              <i class="fa-solid fa-play me-1.5"></i>{{ algoName(s.algo) }}
            </router-link>
            <router-link :to="'/algorithms/' + s.algo" class="btn-ghost px-4 py-2 text-xs">
              <i class="fa-solid fa-book-open me-1.5"></i>{{ $t('alg.learn_more') }}
            </router-link>
            <router-link
              v-if="s.attack"
              :to="{ path: '/simulator', query: { algo: s.attack } }"
              class="btn-ghost px-4 py-2 text-xs !border-dangerx/40 !text-dangerx"
              @click="mark(i)"
            >
              <i class="fa-solid fa-burst me-1.5"></i>{{ $t('ux.break_it') }}: {{ algoName(s.attack) }}
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- glossary -->
    <h2 class="font-semibold text-sm mb-3">
      <i class="fa-solid fa-book text-cipher me-2"></i>{{ $t('ux.learn.glossary_title') }}
    </h2>
    <div class="grid sm:grid-cols-2 gap-3">
      <div v-for="(g, i) in $tm('ux.glossary')" :key="i" class="panel-flat p-4">
        <p class="text-sm font-bold mb-1">
          <i class="fa-solid fa-quote-right text-cipher/50 me-1.5 text-xs"></i>{{ $rt(g.term) }}
        </p>
        <p class="text-xs text-muted leading-relaxed">{{ $rt(g.def) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSimulationStore } from '../stores/simulationStore'

/** localStorage key for visited-station flags (array of booleans). */
const STORE_KEY = 'secsim_learn'

const { locale, tm, rt } = useI18n()
const sim = useSimulationStore()
const done = ref([false, false, false, false, false])

/** Stations come from i18n (ux.learn.stations) so both languages work. */
const stations = computed(() => {
  try {
    const list = tm('ux.learn.stations')
    return Array.isArray(list) ? list : []
  } catch {
    return []
  }
})

/** Resolve a station field that may be a plain string or {ar,en}. */
function $rtStation(s, field) {
  try {
    return rt(s[field])
  } catch {
    return ''
  }
}

/** Display name of an algorithm id (catalog name, fallback: raw id). */
function algoName(id) {
  const meta = sim.algorithms.find((a) => a.id === id)
  return meta?.name?.[locale.value] || meta?.name?.en || id
}

const doneCount = computed(() => done.value.filter(Boolean).length)

function save() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(done.value))
  } catch {
    /* private mode: progress simply doesn't persist */
  }
}
function mark(i) {
  done.value[i] = true
  save()
}
function toggle(i) {
  done.value[i] = !done.value[i]
  save()
}

onMounted(() => {
  sim.fetchAlgorithms().catch(() => {})
  try {
    const saved = JSON.parse(localStorage.getItem(STORE_KEY) || '[]')
    if (Array.isArray(saved)) {
      for (let i = 0; i < Math.min(saved.length, done.value.length); i++) {
        done.value[i] = !!saved[i]
      }
    }
  } catch {
    /* corrupt value: start fresh */
  }
})
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-10">
    <p class="eyebrow mb-2"><i class="fa-solid fa-flask me-2"></i>{{ $t('sim.title') }}</p>
    <h1 class="font-display text-3xl font-bold mb-1">{{ $t('sim.title') }}</h1>
    <p class="text-muted text-sm mb-6">{{ $t('sim.subtitle') }}</p>

    <!-- SELECTED ALGORITHM MASTHEAD -->
    <div class="panel px-6 py-5 mb-4 flex items-center gap-4 flex-wrap">
      <span class="w-14 h-14 rounded-2xl bg-cipher/10 border border-cipher/30 flex items-center justify-center shrink-0">
        <i :class="[algoIcon(store.currentMeta?.type || 'encryption'), 'text-cipher text-2xl']"></i>
      </span>
      <div class="flex-1 min-w-[200px]">
        <p class="eyebrow mb-1">{{ $t('sim.now_simulating') }}</p>
        <h2 class="font-display font-bold text-3xl md:text-4xl tracking-tight leading-none" dir="ltr">
          {{ store.currentMeta?.name?.en || store.algorithm }}
        </h2>
        <p v-if="store.currentMeta?.name?.ar" class="text-lg font-semibold mt-1">{{ store.currentMeta.name.ar }}</p>
      </div>
      <span class="font-mono text-xs px-3 py-1.5 rounded-lg bg-cipher/10 border border-cipher/30 text-cipher" dir="ltr">
        {{ taxBreadcrumb }}
      </span>
    </div>

    <div class="grid lg:grid-cols-5 gap-4 items-start">
      <!-- CONTROL DECK -->
      <div class="panel p-5 space-y-5 lg:col-span-2">
        <div>
          <h2 class="text-sm font-semibold mb-3">
            <i class="fa-solid fa-microchip text-cipher me-2"></i>{{ $t('sim.choose') }}
          </h2>
          <!-- Grouped picker: mirrors the navbar dropdown taxonomy
               (encryption → family → kind; hashing/attacks flat). -->
          <div class="space-y-4">
            <div v-for="grp in pickerGroups" :key="grp.key">
              <p class="text-[0.7rem] font-extrabold text-mist mb-1.5">
                {{ grp.title }}
                <span v-if="grp.sub" class="font-semibold text-muted">· {{ grp.sub }}</span>
              </p>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="a in grp.items"
                  :key="a.id"
                  @click="store.algorithm = a.id"
                  :class="['panel-flat p-3 text-start transition', store.algorithm === a.id ? '!border-cipher bg-cipher/10' : 'hover:border-muted']"
                >
                  <i :class="[algoIcon(a.type), 'text-xs mb-1.5', store.algorithm === a.id ? 'text-cipher' : 'text-muted']"></i>
                  <div class="font-display font-semibold text-sm" dir="ltr">{{ a.id }}</div>
                  <div class="text-[0.7rem] text-muted font-mono" dir="ltr">{{ a.kind || a.type }}</div>
                </button>
              </div>
            </div>
          </div>
          <router-link :to="'/algorithms/' + store.algorithm" class="text-xs text-cipher hover:underline mt-2 inline-block">
            <i class="fa-solid fa-book-open me-1"></i>{{ $t('alg.learn_more') }}: <span class="font-mono" dir="ltr">{{ store.algorithm }}</span>
          </router-link>
        </div>

        <!-- ALGORITHM BRIEF -->
        <div v-if="store.currentMeta" class="panel-flat p-4">
          <div class="flex items-center gap-2 mb-2">
            <i :class="[algoIcon(store.currentMeta.type), 'text-cipher text-sm']"></i>
            <h2 class="text-sm font-semibold">{{ $t('sim.brief') }}</h2>
            <span class="ms-auto font-mono text-[0.65rem] px-2 py-0.5 rounded bg-cipher/10 border border-cipher/30 text-cipher" dir="ltr">
              {{ store.currentMeta.type }}
            </span>
          </div>
          <p v-if="briefText" class="text-xs text-mist/90 leading-relaxed line-clamp-3 mb-2">{{ briefText }}</p>
          <p v-else class="text-xs text-muted mb-2">
            <i class="fa-solid fa-circle-notch fa-spin me-1"></i>{{ $t('sim.brief_loading') }}
          </p>
          <div v-if="store.currentMeta.complexity" class="flex gap-1.5 flex-wrap mb-3" dir="ltr">
            <span class="font-mono text-[0.65rem] px-2 py-0.5 rounded bg-cipher/10 border border-cipher/30 text-cipher">T: {{ store.currentMeta.complexity.time }}</span>
            <span class="font-mono text-[0.65rem] px-2 py-0.5 rounded bg-keyamber/10 border border-keyamber/30 text-keyamber">S: {{ store.currentMeta.complexity.space }}</span>
          </div>
          <div class="flex gap-2">
            <button @click="store.fillExample()" :disabled="store.loading" class="btn-ghost flex-1 py-2 text-xs disabled:opacity-50">
              <i class="fa-solid fa-wand-magic-sparkles me-1.5"></i>{{ $t('sim.example') }}
            </button>
            <router-link :to="'/algorithms/' + store.algorithm" class="btn-ghost flex-1 py-2 text-xs text-center">
              <i class="fa-solid fa-book-open me-1.5"></i>{{ $t('alg.learn_more') }}
            </router-link>
          </div>
        </div>

        <div class="hairline-t pt-5">
          <h2 class="text-sm font-semibold mb-3">
            <i class="fa-solid fa-keyboard text-cipher me-2"></i>{{ $t('sim.input') }}
          </h2>
          <label class="block text-xs text-muted mb-1.5">{{ $t('sim.text') }}</label>
          <input v-model="store.input" @keyup.enter="store.run()" class="field w-full px-3 py-2.5 text-sm font-mono mb-1" dir="ltr" placeholder="Hello World" />
          <p v-if="store.algorithm === 'brute_force'" class="text-[0.7rem] text-keyamber mb-4">
            <i class="fa-solid fa-burst me-1"></i>{{ $t('sim.attack_hint') }}
          </p>
          <p v-else-if="store.algorithm === 'rsa' && store.mode === 'decrypt'" class="text-[0.7rem] text-keyamber mb-4">
            <i class="fa-solid fa-circle-info me-1"></i>{{ $t('sim.rsa_decrypt_hint') }}
          </p>
          <p v-else-if="store.algorithm === 'rsa'" class="text-[0.7rem] text-muted mb-4">
            <i class="fa-solid fa-circle-info me-1"></i>{{ $t('sim.rsa_hint') }}
          </p>
          <div v-else class="mb-4"></div>
          <div v-if="store.algorithm === 'caesar'" class="mb-4">
            <label class="block text-xs text-muted mb-1.5">{{ $t('sim.key') }}</label>
            <input v-model.number="store.key" type="number" min="0" max="25" class="field w-full px-3 py-2.5 text-sm font-mono" dir="ltr" />
          </div>
          <div v-if="['caesar', 'aes', 'rsa'].includes(store.algorithm)" class="mb-4">
            <label class="block text-xs text-muted mb-1.5">{{ $t('sim.mode') }}</label>
            <select v-model="store.mode" class="field w-full px-3 py-2.5 text-sm">
              <option value="encrypt">{{ $t('sim.encrypt') }}</option>
              <option value="decrypt">{{ $t('sim.decrypt') }}</option>
            </select>
          </div>
          <div v-if="store.algorithm === 'aes'" class="grid grid-cols-2 gap-3 mb-4">
            <div class="col-span-2">
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.key_text') }}</label>
              <input v-model="store.aesKeyText" class="field w-full px-3 py-2.5 text-sm font-mono" dir="ltr" />
            </div>
            <div class="col-span-2">
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.key_size') }}</label>
              <select v-model.number="store.aesKeySize" class="field w-full px-3 py-2.5 text-sm font-mono" dir="ltr">
                <option :value="128">128</option>
                <option :value="192">192</option>
                <option :value="256">256</option>
              </select>
            </div>
          </div>
          <div v-if="store.algorithm === 'rsa'" class="grid grid-cols-3 gap-3 mb-4">
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">p</label>
              <input v-model.number="store.rsaP" type="number" class="field w-full px-3 py-2.5 text-sm font-mono" dir="ltr" />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">q</label>
              <input v-model.number="store.rsaQ" type="number" class="field w-full px-3 py-2.5 text-sm font-mono" dir="ltr" />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">e</label>
              <input v-model.number="store.rsaE" type="number" class="field w-full px-3 py-2.5 text-sm font-mono" dir="ltr" />
            </div>
          </div>
          <button @click="store.run()" :disabled="store.loading" class="btn-cipher w-full py-3 text-sm disabled:opacity-50">
            <i v-if="store.loading" class="fa-solid fa-circle-notch fa-spin me-2"></i>
            <i v-else class="fa-solid fa-play me-2"></i>{{ $t('sim.run') }}
          </button>
          <p v-if="store.error" class="text-dangerx text-xs mt-2">
            <i class="fa-solid fa-triangle-exclamation me-1"></i>{{ store.error }}
          </p>
        </div>
      </div>

      <!-- TERMINAL -->
      <div class="lg:col-span-3 space-y-4">
        <div class="panel p-5">
          <div class="flex items-center gap-1.5 mb-4" dir="ltr">
            <span class="w-2.5 h-2.5 rounded-full bg-dangerx/80"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-keyamber/80"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-cipher/80"></span>
            <span class="ms-2 font-mono text-xs text-muted">secsim — {{ store.algorithm }}</span>
          </div>
          <div v-if="store.result" class="panel-flat p-4 mb-1">
            <div class="flex items-center justify-between mb-1.5">
              <p class="text-xs text-muted">{{ $t('sim.result') }}</p>
              <button @click="copyResult()" class="btn-ghost px-2 py-1 text-[0.7rem]">
                <i :class="['me-1', copied ? 'fa-solid fa-check text-cipher' : 'fa-solid fa-copy']"></i>{{ copied ? $t('sim.copied') : $t('sim.copy') }}
              </button>
            </div>
            <p class="font-mono text-cipher break-all" dir="ltr">{{ store.result }}</p>
          </div>
          <div v-if="store.warning" class="flex items-start gap-2 bg-amber-50 border border-amber-300 text-amber-800 text-xs font-semibold rounded-xl px-3.5 py-3 mt-3">
            <i class="fa-solid fa-triangle-exclamation mt-0.5 shrink-0"></i>
            <span>{{ store.warning[locale] || store.warning.en }}</span>
          </div>
          <p v-if="!store.result" class="text-sm text-muted">
            <i class="fa-solid fa-terminal me-2"></i>{{ $t('sim.need_run') }}
          </p>
        </div>

        <VisualizationArea v-if="store.steps.length" />
        <SecurityMetrics v-if="store.analysis" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSimulationStore } from '../stores/simulationStore'
import VisualizationArea from '../components/simulation/VisualizationArea.vue'
import SecurityMetrics from '../components/analysis/SecurityMetrics.vue'
const store = useSimulationStore()
const route = useRoute()
const { t, locale } = useI18n()
const copied = ref(false)
function algoIcon(type) {
  if (type === 'attack') return 'fa-solid fa-burst'
  if (type === 'hashing') return 'fa-solid fa-fingerprint'
  return 'fa-solid fa-key'
}
// Breadcrumb for the masthead badge, e.g. "symmetric · stream".
// Falls back to the flat type for entries without taxonomy.
const taxBreadcrumb = computed(() => {
  const m = store.currentMeta
  if (!m) return '—'
  if (m.type === 'encryption' && m.family) {
    return m.kind ? `${m.family} · ${m.kind}` : m.family
  }
  return m.type
})
// Grouped picker sections mirroring the navbar dropdown taxonomy:
// one section per (family, kind) under encryption, flat sections for
// hashing and attacks. Catalog order is preserved inside groups.
const pickerGroups = computed(() => {
  const groups = []
  const enc = store.algorithms.filter((a) => a.type === 'encryption')
  for (const family of ['symmetric', 'asymmetric']) {
    const members = enc.filter((a) => a.family === family)
    const kinds = []
    for (const a of members) {
      if (!kinds.includes(a.kind)) kinds.push(a.kind)
    }
    for (const kind of kinds) {
      groups.push({
        key: `${family}/${kind}`,
        title: t('tax.' + family),
        sub: kind ? t('tax.' + kind) : '',
        items: members.filter((a) => a.kind === kind)
      })
    }
  }
  const flat = (type) => ({
    key: type,
    title: t('tax.' + type),
    sub: '',
    items: store.algorithms.filter((a) => a.type === type)
  })
  // Only append non-empty sections (robust to catalog changes).
  for (const sec of [flat('hashing'), flat('attack')]) {
    if (sec.items.length) groups.push(sec)
  }
  return groups
})
const briefText = computed(() => {
  const d = store.currentDetail?.details?.overview
  if (d) return d[locale.value] || d.en
  const m = store.currentMeta?.description
  return m ? m[locale.value] || m.en : ''
})
async function copyResult() {
  if (!store.result) return
  try {
    await navigator.clipboard.writeText(store.result)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = store.result
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    ta.remove()
  }
  copied.value = true
  setTimeout(() => { copied.value = false }, 1500)
}
watch(
  () => store.algorithm,
  async () => {
    copied.value = false
    await store.fetchDetails()
    if (store.input) await store.run()
  }
)
onMounted(async () => {
  try { await store.fetchAlgorithms() } catch { /* offline */ }
  const preset = route.query.algo
  if (preset && store.algorithms.some((a) => a.id === preset)) store.algorithm = preset
  await store.fetchDetails()
  if (store.input && !store.result) await store.run()
})
// React to navbar-dropdown navigation while already on this view:
// /simulator?algo=aes must switch the bench without a full reload.
watch(
  () => route.query.algo,
  async (id) => {
    if (id && id !== store.algorithm && store.algorithms.some((a) => a.id === id)) {
      store.algorithm = id
    }
  }
)
</script>

<!--
  ComparePanel — side-by-side algorithm comparison.
  Preset duels (MD5 vs SHA-256, AES-128 vs AES-256, SHA family) run
  POST /api/compare on the bench's live input; results render as
  columns with digest size, avalanche %, time and key facts + a
  bilingual verdict banner. Nothing is saved to history.
-->
<template>
  <div class="panel p-5">
    <h3 class="font-semibold text-sm mb-1">
      <i class="fa-solid fa-scale-balanced text-cipher me-2"></i>{{ $t('compare.title') }}
    </h3>
    <p class="text-[0.7rem] text-muted mb-3">{{ $t('compare.subtitle') }}</p>

    <div class="flex gap-1.5 flex-wrap mb-4">
      <button
        v-for="preset in presets"
        :key="preset.key"
        :disabled="store.compareLoading"
        :class="[
          'px-3 py-2 rounded-xl text-[0.7rem] font-bold border transition disabled:opacity-50',
          activePreset === preset.key
            ? 'bg-cipher/10 border-cipher text-cipher'
            : 'bg-panel2 border-[rgba(148,163,184,0.16)] text-muted hover:border-muted'
        ]"
        @click="runPreset(preset)"
      >
        <i :class="[preset.icon, 'me-1.5']"></i>{{ preset.title }}
      </button>
    </div>

    <p v-if="store.compareLoading" class="text-xs text-muted">
      <i class="fa-solid fa-circle-notch fa-spin me-1"></i>{{ $t('compare.loading') }}
    </p>

    <div
      v-if="store.compareVerdict && !store.compareLoading"
      class="rounded-xl border border-keyamber/40 bg-keyamber/5 px-3.5 py-3 mb-3"
    >
      <p class="flex items-center gap-2 text-sm font-extrabold text-keyamber mb-1">
        <i class="fa-solid fa-trophy"></i>{{ $t('ux.winner') }}
      </p>
      <p class="text-xs text-mist/90 font-semibold leading-relaxed">
        {{ store.compareVerdict[locale] || store.compareVerdict.en }}
      </p>
    </div>

    <div v-if="store.compareResults.length && !store.compareLoading" class="grid md:grid-cols-3 gap-3">
      <div v-for="r in store.compareResults" :key="r.algorithm + JSON.stringify(r.analysis_metrics)" class="panel-flat p-4">
        <div class="flex items-center gap-2 mb-2">
          <p class="font-display font-bold text-sm" dir="ltr">{{ columnTitle(r) }}</p>
          <span
            v-if="r.meta?.security"
            :class="[
              'ms-auto font-mono text-[0.6rem] px-1.5 py-px rounded border shrink-0',
              r.meta.security === 'secure'
                ? 'bg-cipher/10 border-cipher/30 text-cipher'
                : r.meta.security === 'broken'
                  ? 'bg-dangerx/10 border-dangerx/30 text-dangerx'
                  : 'bg-keyamber/10 border-keyamber/30 text-keyamber'
            ]"
            >{{ $t('alg.badge_' + r.meta.security) }}</span
          >
        </div>
        <p v-if="showOut[r.algorithm + (r.analysis_metrics?.key_bits || '')]" class="font-mono text-[0.65rem] text-muted break-all mb-3" dir="ltr">{{ r.result }}</p>
        <button
          class="text-[0.65rem] text-cipher hover:underline mb-3"
          @click="toggleOut(r)"
        >
          {{ showOut[r.algorithm + (r.analysis_metrics?.key_bits || '')] ? $t('ux.hide_output') : $t('ux.show_output') }}
        </button>
        <dl class="space-y-1.5 text-[0.7rem]">
          <div v-if="r.digest_bits" class="flex justify-between gap-2">
            <dt class="text-muted">{{ $t('compare.digest') }}</dt>
            <dd class="font-mono font-bold" dir="ltr">{{ r.digest_bits }}-bit</dd>
          </div>
          <div v-if="r.avalanche_pct !== null && r.avalanche_pct !== undefined" class="flex justify-between gap-2">
            <dt class="text-muted">{{ $t('compare.avalanche') }}</dt>
            <dd class="font-mono font-bold" dir="ltr">{{ r.avalanche_pct }}%</dd>
          </div>
          <div v-if="keyFact(r)" class="flex justify-between gap-2">
            <dt class="text-muted">{{ keyFact(r).label }}</dt>
            <dd class="font-mono font-bold" dir="ltr">{{ keyFact(r).value }}</dd>
          </div>
          <div class="flex justify-between gap-2">
            <dt class="text-muted">{{ $t('sim.time') }} ({{ $t('sim.ms') }})</dt>
            <dd class="font-mono font-bold" dir="ltr">{{ r.metrics.time_ms }}</dd>
          </div>
          <div class="flex justify-between gap-2">
            <dt class="text-muted">{{ $t('sim.steps') }}</dt>
            <dd class="font-mono font-bold" dir="ltr">{{ r.metrics.steps }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSimulationStore } from '../../stores/simulationStore'

const { locale, t } = useI18n()
const store = useSimulationStore()
const activePreset = ref(null)
/** Full-output visibility per result column (keyed by algorithm+keysize). */
const showOut = ref({})
function toggleOut(r) {
  const k = r.algorithm + (r.analysis_metrics?.key_bits || '')
  showOut.value[k] = !showOut.value[k]
}

const presets = computed(() => [
  {
    key: 'md5_sha256',
    title: t('compare.preset_hash'),
    icon: 'fa-solid fa-fingerprint',
    entries: [{ algorithm: 'md5' }, { algorithm: 'sha256' }]
  },
  {
    key: 'aes_sizes',
    title: t('compare.preset_aes'),
    icon: 'fa-solid fa-key',
    entries: [
      { algorithm: 'aes', overrides: { aesKeySize: 128 } },
      { algorithm: 'aes', overrides: { aesKeySize: 256 } }
    ]
  },
  {
    key: 'sha_family',
    title: t('compare.preset_sha_family'),
    icon: 'fa-solid fa-layer-group',
    entries: [{ algorithm: 'sha256' }, { algorithm: 'sha512' }, { algorithm: 'sha3' }]
  }
])

function columnTitle(r) {
  if (r.algorithm === 'aes') {
    const kb = r.analysis_metrics?.key_bits
    return kb ? `aes-${kb}` : r.algorithm
  }
  return r.algorithm
}

function keyFact(r) {
  const m = r.analysis_metrics || {}
  if (m.key_bits) return { label: t('compare.keysize'), value: `${m.key_bits}-bit` }
  if (typeof m.keyspace === 'number') return { label: t('compare.keyspace'), value: m.keyspace.toLocaleString() }
  if (m.keyspace) return { label: t('compare.keyspace'), value: String(m.keyspace) }
  if (m.rounds) return { label: t('compare.rounds'), value: String(m.rounds) }
  return null
}

async function runPreset(preset) {
  activePreset.value = preset.key
  await store.fetchCompare(preset.entries)
}
</script>

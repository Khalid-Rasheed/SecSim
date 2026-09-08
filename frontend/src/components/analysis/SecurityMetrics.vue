<template>
  <div v-if="store.analysis" class="panel p-5">
    <h3 class="font-semibold text-sm mb-4">
      <i class="fa-solid fa-magnifying-glass-chart text-cipher me-2"></i>{{ $t('sim.analysis') }}
    </h3>

    <div class="grid grid-cols-2 gap-3 mb-4">
      <div class="panel-flat p-3 text-center">
        <i class="fa-solid fa-stopwatch text-cipher text-lg mb-1"></i>
        <div class="font-display font-bold text-xl" dir="ltr">{{ store.metrics?.time_ms }}</div>
        <div class="text-[0.7rem] text-muted">{{ $t('sim.time') }} ({{ $t('sim.ms') }})</div>
      </div>
      <div class="panel-flat p-3 text-center">
        <i class="fa-solid fa-list-ol text-keyamber text-lg mb-1"></i>
        <div class="font-display font-bold text-xl" dir="ltr">{{ store.metrics?.steps }}</div>
        <div class="text-[0.7rem] text-muted">{{ $t('sim.steps') }}</div>
      </div>
    </div>

    <div class="grid md:grid-cols-2 gap-3 mb-4">
      <div class="rounded-xl border border-cipher/30 bg-cipher/5 p-4">
        <p class="text-sm font-semibold mb-2 text-cipher">
          <i class="fa-solid fa-circle-check me-1.5"></i>{{ $t('sim.strengths') }}
        </p>
        <ul class="space-y-1.5">
          <li v-for="(s, i) in strengths" :key="i" class="text-xs text-mist/90 flex gap-2">
            <i class="fa-solid fa-plus text-cipher text-[0.6rem] mt-1"></i>{{ s }}
          </li>
        </ul>
      </div>
      <div class="rounded-xl border border-dangerx/30 bg-dangerx/5 p-4">
        <p class="text-sm font-semibold mb-2 text-dangerx">
          <i class="fa-solid fa-triangle-exclamation me-1.5"></i>{{ $t('sim.weaknesses') }}
        </p>
        <ul class="space-y-1.5">
          <li v-for="(w, i) in weaknesses" :key="i" class="text-xs text-mist/90 flex gap-2">
            <i class="fa-solid fa-minus text-dangerx text-[0.6rem] mt-1"></i>{{ w }}
          </li>
        </ul>
      </div>
    </div>

    <div v-if="complexity" class="panel-flat p-4 mb-4">
      <p class="text-sm font-semibold mb-3">
        <i class="fa-solid fa-chart-line text-cipher me-1.5"></i>{{ $t('sim.complexity') }}
      </p>
      <div class="flex gap-2 flex-wrap mb-2" dir="ltr">
        <span class="font-mono text-xs px-3 py-1.5 rounded-lg bg-cipher/10 border border-cipher/30 text-cipher">
          Time {{ complexity.time }}
        </span>
        <span class="font-mono text-xs px-3 py-1.5 rounded-lg bg-keyamber/10 border border-keyamber/30 text-keyamber">
          Space {{ complexity.space }}
        </span>
      </div>
      <p class="text-xs text-muted">
        {{ $t('sim.n_is') }} {{ complexity.n?.[locale] || complexity.n?.en }}.
        {{ complexity.note?.[locale] || complexity.note?.en }}
      </p>
    </div>

    <canvas ref="chartEl" height="120"></canvas>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { useSimulationStore } from '../../stores/simulationStore'
Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const { locale } = useI18n()
const store = useSimulationStore()
const chartEl = ref(null)
let chart = null

const strengths = computed(() => store.analysis?.strengths?.[locale.value] || store.analysis?.strengths?.en || [])
const weaknesses = computed(() => store.analysis?.weaknesses?.[locale.value] || store.analysis?.weaknesses?.en || [])
const complexity = computed(() => store.analysis?.complexity || null)

function draw() {
  if (!chartEl.value || !store.metrics) return
  if (chart) chart.destroy()
  chart = new Chart(chartEl.value, {
    type: 'bar',
    data: {
      labels: [store.algorithm],
      datasets: [{
        label: 'ms',
        data: [store.metrics.time_ms],
        backgroundColor: 'rgba(13, 148, 136, 0.75)',
        borderColor: '#0d9488',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: '#64748b', font: { family: 'Tajawal' } } } },
      scales: {
        x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(15,23,42,0.07)' } },
        y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(15,23,42,0.07)' } }
      }
    }
  })
}
onMounted(draw)
watch(() => store.metrics, draw)
</script>

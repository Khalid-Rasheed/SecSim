<template>
  <div class="max-w-4xl mx-auto px-4 py-10">
    <p class="eyebrow mb-2"><i class="fa-solid fa-clock-rotate-left me-2"></i>{{ $t('history.title') }}</p>
    <h1 class="font-display text-3xl font-bold mb-1">{{ $t('history.title') }}</h1>
    <p class="text-muted text-sm mb-8">{{ $t('history.subtitle') }}</p>

    <div v-if="!auth.isLoggedIn" class="panel p-8 text-center">
      <i class="fa-solid fa-lock text-3xl text-muted mb-3"></i>
      <p class="text-sm text-muted mb-4">{{ $t('history.login_required') }}</p>
      <router-link to="/login" class="btn-cipher px-5 py-2.5 text-sm inline-block">
        <i class="fa-solid fa-right-to-bracket me-2"></i>{{ $t('nav.login') }}
      </router-link>
    </div>

    <template v-else>
      <div class="flex justify-between items-center mb-4">
        <span class="font-mono text-xs text-muted" dir="ltr">{{ sim.history.length }} records</span>
        <button @click="load" class="btn-ghost px-3 py-1.5 text-xs">
          <i class="fa-solid fa-rotate me-1.5"></i>Refresh
        </button>
      </div>

      <div v-if="!sim.history.length" class="panel p-8 text-center">
        <i class="fa-solid fa-flask text-3xl text-muted mb-3"></i>
        <p class="text-sm text-muted mb-4">{{ $t('history.empty') }}</p>
        <router-link to="/simulator" class="btn-cipher px-5 py-2.5 text-sm inline-block">
          <i class="fa-solid fa-play me-2"></i>{{ $t('history.go') }}
        </router-link>
      </div>

      <div v-for="h in sim.history" :key="h.id" class="panel-flat p-4 mb-3 flex items-start gap-3">
        <span class="w-9 h-9 rounded-lg bg-cipher/10 border border-cipher/30 flex items-center justify-center shrink-0">
          <i :class="[histIcon(h.algorithm), 'text-cipher text-sm']"></i>
        </span>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-mono font-semibold text-sm" dir="ltr">#{{ h.id }} · {{ h.algorithm }}</span>
            <span class="font-mono text-[0.7rem] text-muted" dir="ltr">{{ h.duration_ms }} ms · {{ h.steps_count }} {{ $t('history.steps') }}</span>
          </div>
          <p class="font-mono text-xs text-muted truncate mt-1" dir="ltr">{{ h.input }} → {{ h.result }}</p>
        </div>
        <span class="font-mono text-[0.7rem] text-muted shrink-0" dir="ltr">{{ (h.created_at || '').slice(0, 10) }}</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { useSimulationStore } from '../stores/simulationStore'
const auth = useAuthStore()
const sim = useSimulationStore()
function load() { if (auth.isLoggedIn) sim.fetchHistory().catch(() => {}) }
function histIcon(algo) {
  if (algo === 'brute_force') return 'fa-solid fa-burst'
  if (algo === 'md5' || algo === 'sha256') return 'fa-solid fa-fingerprint'
  return 'fa-solid fa-key'
}
onMounted(load)
</script>

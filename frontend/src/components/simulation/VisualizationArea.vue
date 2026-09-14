<template>
  <div class="panel p-5">
    <div class="flex items-center justify-between flex-wrap gap-2 mb-4">
      <h3 class="font-semibold text-sm">
        <i class="fa-solid fa-list-ol text-cipher me-2"></i>{{ $t('sim.steps') }}
      </h3>
      <span class="font-mono text-xs text-muted" dir="ltr"
        >{{ store.currentStep + 1 }} / {{ store.steps.length }}</span
      >
    </div>

    <!-- progress rail -->
    <div class="h-1 rounded bg-panel2 overflow-hidden mb-4 border border-[rgba(15,23,42,0.1)]" dir="ltr">
      <div
        class="h-full bg-cipher transition-all"
        :style="{ width: ((store.currentStep + 1) / store.steps.length) * 100 + '%' }"
      ></div>
    </div>

    <!-- current step -->
    <div v-if="step" class="panel-flat p-4 mb-4">
      <div class="font-display font-semibold text-sm mb-1">{{ step.title?.[locale] || step.title?.en }}</div>
      <p class="text-sm text-muted leading-relaxed mb-3">
        {{ step.description?.[locale] || step.description?.en }}
      </p>
      <p class="text-[0.7rem] font-mono text-muted mb-1.5 uppercase tracking-widest">
        {{ $t('sim.snapshot') }}
      </p>
      <pre class="font-mono text-xs text-cipher/90 overflow-auto max-h-40" dir="ltr">{{
        JSON.stringify(step.snapshot, null, 2)
      }}</pre>
    </div>

    <!-- transport -->
    <div class="flex items-center gap-2 flex-wrap mb-4">
      <button class="btn-ghost px-3 py-2 text-xs" :title="$t('sim.prev')" @click="store.prev()">
        <i class="fa-solid fa-backward-step"></i>
      </button>
      <button v-if="!store.playing" class="btn-cipher px-4 py-2 text-xs" @click="store.play()">
        <i class="fa-solid fa-play me-1.5"></i>{{ $t('sim.play') }}
      </button>
      <button
        v-else
        class="px-4 py-2 text-xs rounded-[10px] bg-dangerx text-white font-bold"
        @click="store.stop()"
      >
        <i class="fa-solid fa-stop me-1.5"></i>{{ $t('sim.pause') }}
      </button>
      <button class="btn-ghost px-3 py-2 text-xs" :title="$t('sim.next')" @click="store.next()">
        <i class="fa-solid fa-forward-step"></i>
      </button>
      <label class="text-xs text-muted flex items-center gap-2 ms-1">
        <i class="fa-solid fa-gauge-high"></i>{{ $t('sim.speed') }}
        <input
          type="range"
          min="200"
          max="2000"
          step="200"
          :value="store.speed"
          class="w-28"
          dir="ltr"
          @input="store.setSpeed(Number($event.target.value))"
        />
      </label>
    </div>

    <!-- step dots -->
    <div class="flex gap-1.5 flex-wrap" dir="ltr">
      <button
        v-for="(s, i) in store.steps"
        :key="i"
        :class="['step-dot', { current: i === store.currentStep }]"
        :title="s.title?.[locale] || s.title?.en"
        @click="store.currentStep = i"
      >
        {{ i + 1 }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSimulationStore } from '../../stores/simulationStore'
const { locale } = useI18n()
const store = useSimulationStore()
const step = computed(() => store.steps[store.currentStep])
</script>

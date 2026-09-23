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
      <div class="flex items-center gap-2 mb-1 flex-wrap">
        <div class="font-display font-semibold text-sm">{{ step.title?.[locale] || step.title?.en }}</div>
        <span
          v-if="step.meta?.phase"
          class="font-mono text-[0.6rem] px-1.5 py-px rounded bg-cipher/10 border border-cipher/30 text-cipher"
          dir="ltr"
          >{{ step.meta.phase }}</span
        >
      </div>
      <p class="text-sm text-muted leading-relaxed mb-3">
        {{ step.description?.[locale] || step.description?.en }}
      </p>
      <!-- Readable snapshot table (replaces the raw JSON dump that
           scared beginners) with an expand toggle for long values. -->
      <div v-if="snapRows.length" class="rounded-xl border border-[rgba(148,163,184,0.2)] overflow-hidden">
        <button
          class="w-full flex items-center justify-between px-3 py-2 text-[0.7rem] font-bold text-muted hover:text-mist bg-panel2"
          @click="showSnap = !showSnap"
        >
          <span
            ><i class="fa-solid fa-table-list me-1.5 text-cipher"></i>{{ $t('sim.snapshot') }} ({{
              snapRows.length
            }})</span
          >
          <span class="text-cipher">{{ showSnap ? $t('ux.hide_snapshot') : $t('ux.show_snapshot') }}</span>
        </button>
        <dl v-show="showSnap" class="divide-y divide-[rgba(148,163,184,0.12)]">
          <div v-for="row in snapRows" :key="row.key" class="flex gap-3 px-3 py-1.5 text-xs">
            <dt class="text-muted shrink-0 min-w-[7rem]" dir="ltr">{{ row.label }}</dt>
            <dd class="font-mono text-mist/90 break-all" dir="ltr" :title="row.full">{{ row.display }}</dd>
          </div>
        </dl>
      </div>
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
          class="w-20"
          dir="ltr"
          :aria-label="$t('sim.speed')"
          @input="store.setSpeed(Number($event.target.value))"
        />
        <span class="text-[0.65rem] font-mono" dir="ltr">{{ speedLabel }}</span>
      </label>
    </div>

    <!-- step dots (numbered + named via title tooltip and aria-label) -->
    <div class="flex gap-1.5 flex-wrap" dir="ltr">
      <button
        v-for="(s, i) in store.steps"
        :key="i"
        :class="['step-dot', { current: i === store.currentStep }]"
        :title="s.title?.[locale] || s.title?.en"
        :aria-label="`${i + 1}: ${s.title?.[locale] || s.title?.en}`"
        @click="store.currentStep = i"
      >
        {{ i + 1 }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSimulationStore } from '../../stores/simulationStore'
import { snapshotRows } from '../../utils/ux'
const { locale, t } = useI18n()
const store = useSimulationStore()
const step = computed(() => store.steps[store.currentStep])
/** Snapshot table rows for the current step (human labels + truncation). */
const snapRows = computed(() => snapshotRows(step.value?.snapshot))
/** Details table starts open on short snapshots, collapsed on long ones. */
const showSnap = ref(true)
/** Plain-language speed readout: slider ms/step → slower/faster words. */
const speedLabel = computed(() =>
  store.speed >= 1200 ? t('ux.viz.slower') : store.speed <= 600 ? t('ux.viz.faster') : '•'
)
</script>

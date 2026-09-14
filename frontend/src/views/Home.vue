<template>
  <div>
    <!-- HERO -->
    <section class="max-w-6xl mx-auto px-4 pt-14 pb-10 grid lg:grid-cols-2 gap-10 items-center">
      <div>
        <p class="eyebrow mb-4"><i class="fa-solid fa-terminal me-2"></i>{{ $t('hero.eyebrow') }}</p>
        <h1 class="font-display text-4xl md:text-5xl font-bold leading-tight mb-4">
          {{ $t('hero.title') }}
        </h1>
        <p class="text-muted leading-relaxed mb-8 max-w-xl">{{ $t('hero.subtitle') }}</p>
        <div class="flex gap-3 flex-wrap">
          <router-link to="/simulator" class="btn-cipher px-6 py-3 text-sm">
            <i class="fa-solid fa-flask me-2"></i>{{ $t('hero.cta') }}
          </router-link>
          <a href="#how" class="btn-ghost px-6 py-3 text-sm">
            {{ $t('hero.secondary') }}
          </a>
        </div>
      </div>

      <!-- live cipher tape demo -->
      <div class="panel p-5">
        <div class="flex items-center justify-between mb-4">
          <span class="font-mono text-xs text-muted" dir="ltr">
            <span class="inline-block w-2 h-2 rounded-full bg-cipher animate-pulse me-2"></span
            >{{ $t('hero.live') }}
          </span>
          <span
            class="font-mono text-xs text-keyamber border border-keyamber/40 rounded px-2 py-0.5"
            dir="ltr"
            >key = 3</span
          >
        </div>
        <p class="text-xs text-muted mb-2">
          {{ $t('hero.plain') }} <span class="font-mono" dir="ltr">HELLO</span>
        </p>
        <CipherTape :chars="tape" :lit-up-to="lit" />
        <p class="text-xs text-muted mt-3 mb-2">
          {{ $t('hero.ciphered') }} <span class="font-mono text-cipher" dir="ltr">KHOOR</span>
        </p>
        <div class="hairline-t pt-3 mt-1 font-mono text-[0.7rem] text-muted" dir="ltr">
          H(07) +3 → K(10) · E(04) +3 → H(07) · L(11) +3 → O(14) · O(14) +3 → R(17)
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section id="how" class="max-w-6xl mx-auto px-4 py-10">
      <p class="eyebrow mb-6">{{ $t('features.eyebrow') }}</p>
      <div class="grid md:grid-cols-3 gap-4">
        <div v-for="(f, i) in $tm('features.items')" :key="i" class="panel p-5">
          <span
            class="w-10 h-10 rounded-lg bg-cipher/10 border border-cipher/30 flex items-center justify-center mb-4"
          >
            <i :class="[$rt(f.icon), 'text-cipher']"></i>
          </span>
          <h3 class="font-semibold mb-1.5">{{ $rt(f.title) }}</h3>
          <p class="text-sm text-muted leading-relaxed">{{ $rt(f.text) }}</p>
        </div>
      </div>
    </section>

    <!-- ALGORITHMS -->
    <section class="max-w-6xl mx-auto px-4 py-10">
      <div class="flex items-center justify-between mb-6">
        <p class="eyebrow">{{ $t('home.algos') }}</p>
        <router-link to="/simulator" class="text-sm text-cipher hover:underline">
          {{ $t('home.open_sim') }} <i class="fa-solid fa-arrow-left text-xs ms-1 rtl:rotate-180"></i>
        </router-link>
      </div>
      <div class="grid sm:grid-cols-2 gap-4">
        <div v-for="a in sim.algorithms" :key="a.id" class="panel-flat p-5 flex gap-4 items-start">
          <span
            class="w-10 h-10 rounded-lg bg-keyamber/10 border border-keyamber/30 flex items-center justify-center shrink-0"
          >
            <i :class="[algoIcon(a.type), 'text-keyamber']"></i>
          </span>
          <div class="flex-1">
            <h3 class="font-display font-semibold" dir="ltr">{{ a.id }}</h3>
            <p class="text-xs font-mono text-muted mb-1.5" dir="ltr">{{ a.type }}</p>
            <p class="text-sm text-muted mb-2">{{ a.description?.[locale] || a.description?.en }}</p>
            <div v-if="a.complexity" class="flex gap-1.5 flex-wrap mb-2" dir="ltr">
              <span
                class="font-mono text-[0.65rem] px-2 py-0.5 rounded bg-cipher/10 border border-cipher/30 text-cipher"
                >T: {{ a.complexity.time }}</span
              >
              <span
                class="font-mono text-[0.65rem] px-2 py-0.5 rounded bg-keyamber/10 border border-keyamber/30 text-keyamber"
                >S: {{ a.complexity.space }}</span
              >
            </div>
            <router-link :to="'/algorithms/' + a.id" class="text-xs text-cipher hover:underline">
              {{ $t('alg.learn_more') }}
              <i class="fa-solid fa-arrow-left text-[0.6rem] ms-1 rtl:rotate-180"></i>
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSimulationStore } from '../stores/simulationStore'
import CipherTape from '../components/common/CipherTape.vue'

const { locale } = useI18n()
const sim = useSimulationStore()

function algoIcon(type) {
  if (type === 'attack') return 'fa-solid fa-burst'
  if (type === 'hashing') return 'fa-solid fa-fingerprint'
  return 'fa-solid fa-key'
}

const tape = [
  { in: 'H', out: 'K' },
  { in: 'E', out: 'H' },
  { in: 'L', out: 'O' },
  { in: 'L', out: 'O' },
  { in: 'O', out: 'R' }
]
const lit = ref(-1)
let timer = null

onMounted(() => {
  sim.fetchAlgorithms().catch(() => {})
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    lit.value = tape.length
    return
  }
  timer = setInterval(() => {
    lit.value = lit.value >= tape.length ? -1 : lit.value + 1
  }, 450)
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

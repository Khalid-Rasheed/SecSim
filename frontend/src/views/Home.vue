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

    <!-- HOW IT WORKS (static onboarding for first-time visitors) -->
    <section class="max-w-6xl mx-auto px-4 py-10">
      <p class="eyebrow mb-2">{{ $t('ux.how.eyebrow') }}</p>
      <h2 class="font-display text-2xl md:text-3xl font-bold mb-8">{{ $t('ux.how.title') }}</h2>
      <div class="grid md:grid-cols-3 gap-4">
        <div v-for="(s, i) in howSteps" :key="i" class="panel p-5 relative overflow-hidden">
          <span
            class="font-display font-extrabold text-5xl text-cipher/10 absolute top-3 end-4 select-none"
            dir="ltr"
            >{{ i + 1 }}</span
          >
          <span
            class="w-10 h-10 rounded-lg bg-cipher/10 border border-cipher/30 flex items-center justify-center mb-4"
          >
            <i :class="[s.icon, 'text-cipher']"></i>
          </span>
          <h3 class="font-semibold mb-1.5">{{ s.title }}</h3>
          <p class="text-sm text-muted leading-relaxed">{{ s.text }}</p>
        </div>
      </div>
      <div class="mt-6 flex gap-3 flex-wrap">
        <router-link to="/learn" class="btn-cipher px-6 py-3 text-sm">
          <i class="fa-solid fa-route me-2"></i>{{ $t('ux.learn.title') }}
        </router-link>
        <router-link to="/simulator" class="btn-ghost px-6 py-3 text-sm">
          <i class="fa-solid fa-flask me-2"></i>{{ $t('hero.cta') }}
        </router-link>
      </div>
    </section>

    <!-- ALGORITHMS: 3 tabs -->
    <section class="max-w-6xl mx-auto px-4 py-10">
      <div class="flex items-center justify-between mb-4">
        <p class="eyebrow">{{ $t('home.algos') }}</p>
        <router-link to="/simulator" class="text-sm text-cipher hover:underline">
          {{ $t('home.open_sim') }} <i class="fa-solid fa-arrow-left text-xs ms-1 rtl:rotate-180"></i>
        </router-link>
      </div>
      <p class="text-[0.7rem] text-muted mb-3">{{ $t('tax.tabs_title') }}</p>
      <div class="flex gap-1.5 mb-3 flex-wrap">
        <button
          v-for="tab in homeTabs"
          :key="tab.key"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-bold border transition',
            homeTab === tab.key
              ? 'bg-cipher/10 border-cipher text-cipher'
              : 'bg-panel2 border-[rgba(148,163,184,0.16)] text-muted hover:border-muted'
          ]"
          @click="homeTab = tab.key"
        >
          <i :class="[tab.icon, 'me-1.5']"></i>{{ tab.title }}
        </button>
      </div>
      <!-- One-line human explanation of the active tab (beginners shouldn't
           have to guess what "symmetric" means). -->
      <p class="text-xs text-muted mb-6">
        <i class="fa-solid fa-circle-info me-1.5 text-cipher"></i>{{ $t('ux.tabs_desc.' + homeTab) }}
      </p>
      <div class="grid sm:grid-cols-2 gap-4">
        <div
          v-for="a in homeItems"
          :key="a.id"
          class="panel-flat p-5 flex gap-4 items-start"
        >
          <span
            class="w-10 h-10 rounded-lg bg-keyamber/10 border border-keyamber/30 flex items-center justify-center shrink-0"
          >
            <i :class="[algoIcon(a.type), 'text-keyamber']"></i>
          </span>
          <div class="flex-1">
            <!-- Human name first (raw ids like diffie_hellman scare beginners). -->
            <h3 class="font-display font-semibold">{{ displayName(a) }}</h3>
            <p class="text-xs font-mono text-muted mb-1.5" dir="ltr">{{ a.id }}</p>
            <p class="text-sm text-muted mb-2">{{ a.description?.[locale] || a.description?.en }}</p>
            <div class="flex gap-1.5 flex-wrap mb-2" dir="ltr">
              <span
                :class="[
                  'font-mono text-[0.65rem] px-2 py-0.5 rounded border inline-flex items-center gap-1',
                  levelBadgeClasses(levelFor(a))
                ]"
                ><i :class="[levelIcon(levelFor(a)), 'text-[0.6rem]']"></i
                >{{ $t('ux.level_' + levelFor(a)) }}</span
              >
              <span
                v-if="a.security"
                :class="[
                  'font-mono text-[0.65rem] px-2 py-0.5 rounded border',
                  a.security === 'secure'
                    ? 'bg-cipher/10 border-cipher/30 text-cipher'
                    : a.security === 'broken'
                      ? 'bg-dangerx/10 border-dangerx/30 text-dangerx'
                      : 'bg-keyamber/10 border-keyamber/30 text-keyamber'
                ]"
                >{{ $t('alg.badge_' + a.security) }}</span
              >
            </div>
            <div class="flex gap-3 flex-wrap">
              <router-link :to="'/algorithms/' + a.id" class="text-xs text-cipher hover:underline">
                {{ $t('alg.learn_more') }}
                <i class="fa-solid fa-arrow-left text-[0.6rem] ms-1 rtl:rotate-180"></i>
              </router-link>
              <router-link
                :to="{ path: '/simulator', query: { algo: a.id } }"
                class="text-xs text-keyamber hover:underline"
              >
                {{ $t('alg.try_it') }}
                <i class="fa-solid fa-flask text-[0.6rem] ms-1"></i>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSimulationStore } from '../stores/simulationStore'
import CipherTape from '../components/common/CipherTape.vue'
import { levelFor, levelBadgeClasses, levelIcon } from '../utils/ux'

const { locale, t } = useI18n()
const sim = useSimulationStore()

function algoIcon(type) {
  if (type === 'attack') return 'fa-solid fa-burst'
  if (type === 'hashing') return 'fa-solid fa-fingerprint'
  return 'fa-solid fa-key'
}

/** Human display name: bilingual name first, raw id only as fallback. */
function displayName(a) {
  return a.name?.[locale.value] || a.name?.en || a.id
}

/** Static onboarding steps (ux.how.*) with matching icons. */
const howSteps = computed(() => [
  { icon: 'fa-solid fa-hand-pointer', title: t('ux.how.step1_title'), text: t('ux.how.step1_text') },
  { icon: 'fa-solid fa-play', title: t('ux.how.step2_title'), text: t('ux.how.step2_text') },
  { icon: 'fa-solid fa-magnifying-glass-chart', title: t('ux.how.step3_title'), text: t('ux.how.step3_text') }
])

const homeTab = ref('symmetric')
const homeTabs = computed(() => [
  { key: 'symmetric', title: t('tax.symmetric'), icon: 'fa-solid fa-key' },
  { key: 'asymmetric', title: t('tax.asymmetric'), icon: 'fa-solid fa-key' },
  { key: 'hashing', title: t('tax.hashing'), icon: 'fa-solid fa-fingerprint' }
])
const homeItems = computed(() => sim.algorithms.filter((a) => a.family === homeTab.value))

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

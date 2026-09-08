<template>
  <div class="max-w-4xl mx-auto px-4 py-10">
    <router-link to="/simulator" class="text-sm text-muted hover:text-cipher">
      <i class="fa-solid fa-arrow-right text-xs me-1 rtl:rotate-180"></i>{{ $t('alg.back') }}
    </router-link>

    <div v-if="error" class="panel p-8 text-center mt-6">
      <i class="fa-solid fa-triangle-exclamation text-3xl text-dangerx mb-3"></i>
      <p class="text-sm text-muted">{{ $t('alg.not_found') }}</p>
    </div>

    <template v-else-if="algo">
      <!-- HERO -->
      <div class="panel p-6 md:p-8 mt-6">
        <div class="flex items-start gap-4 flex-wrap">
          <span class="w-14 h-14 rounded-2xl bg-cipher/10 border border-cipher/30 flex items-center justify-center shrink-0">
            <i :class="[algoIcon(algo.type), 'text-cipher text-2xl']"></i>
          </span>
          <div class="flex-1 min-w-[200px]">
            <p class="eyebrow mb-1">{{ $t('alg.type_' + algo.type) }}</p>
            <h1 class="font-display text-3xl font-bold" dir="ltr">{{ algo.name?.[locale] || algo.id }}</h1>
            <p class="text-muted text-sm mt-2 leading-relaxed">{{ algo.description?.[locale] || algo.description?.en }}</p>
          </div>
        </div>
        <div v-if="algo.complexity" class="flex gap-2 flex-wrap mt-5" dir="ltr">
          <span class="font-mono text-xs px-3 py-1.5 rounded-lg bg-cipher/10 border border-cipher/30 text-cipher">Time {{ algo.complexity.time }}</span>
          <span class="font-mono text-xs px-3 py-1.5 rounded-lg bg-keyamber/10 border border-keyamber/30 text-keyamber">Space {{ algo.complexity.space }}</span>
        </div>
        <router-link :to="'/simulator?algo=' + algo.id" class="btn-cipher px-6 py-3 text-sm inline-block mt-5">
          <i class="fa-solid fa-flask me-2"></i>{{ $t('alg.try_it') }}
        </router-link>
      </div>

      <!-- OVERVIEW -->
      <section class="panel p-6 mt-4">
        <h2 class="font-semibold text-sm mb-3"><i class="fa-solid fa-book-open text-cipher me-2"></i>{{ $t('alg.overview') }}</h2>
        <p class="text-sm text-mist/90 leading-loose">{{ t(details.overview) }}</p>
      </section>

      <!-- HISTORY -->
      <section class="panel p-6 mt-4 border-s-4 !border-s-keyamber">
        <h2 class="font-semibold text-sm mb-3"><i class="fa-solid fa-landmark text-keyamber me-2"></i>{{ $t('alg.history') }}</h2>
        <p class="text-sm text-mist/90 leading-loose">{{ t(details.history) }}</p>
      </section>

      <!-- HOW IT WORKS -->
      <section class="panel p-6 mt-4">
        <h2 class="font-semibold text-sm mb-4"><i class="fa-solid fa-gears text-cipher me-2"></i>{{ $t('alg.how') }}</h2>
        <ol class="space-y-3">
          <li v-for="(s, i) in steps" :key="i" class="flex gap-3 items-start">
            <span class="w-7 h-7 rounded-lg bg-cipher/10 border border-cipher/30 text-cipher font-mono text-xs flex items-center justify-center shrink-0" dir="ltr">{{ i + 1 }}</span>
            <p class="text-sm text-mist/90 leading-relaxed pt-1">{{ s }}</p>
          </li>
        </ol>
      </section>

      <!-- PARAMS -->
      <section v-if="params.length" class="panel p-6 mt-4">
        <h2 class="font-semibold text-sm mb-4"><i class="fa-solid fa-sliders text-cipher me-2"></i>{{ $t('alg.params') }}</h2>
        <div class="space-y-2">
          <div v-for="(p, i) in params" :key="i" class="panel-flat p-3 flex gap-3 items-start">
            <code class="font-mono text-xs text-keyamber bg-keyamber/10 border border-keyamber/30 rounded px-2 py-1 shrink-0" dir="ltr">{{ p.name }}</code>
            <p class="text-xs text-mist/90 leading-relaxed">{{ p.desc }}</p>
          </div>
        </div>
      </section>

      <!-- SECURITY -->
      <section class="rounded-[14px] border border-dangerx/30 bg-dangerx/5 p-6 mt-4">
        <h2 class="font-semibold text-sm mb-3 text-dangerx"><i class="fa-solid fa-shield-halved me-2"></i>{{ $t('alg.security') }}</h2>
        <p class="text-sm text-mist/90 leading-loose">{{ t(details.security) }}</p>
      </section>

      <!-- USES -->
      <section class="panel p-6 mt-4">
        <h2 class="font-semibold text-sm mb-3"><i class="fa-solid fa-briefcase text-cipher me-2"></i>{{ $t('alg.uses') }}</h2>
        <div class="flex gap-2 flex-wrap">
          <span v-for="(u, i) in uses" :key="i" class="text-xs px-3 py-1.5 rounded-full bg-panel2 border border-[rgba(148,163,184,0.16)] text-mist/90">
            <i class="fa-solid fa-check text-cipher text-[0.6rem] me-1.5"></i>{{ u }}
          </span>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '../services/api'

const { locale } = useI18n()
const route = useRoute()
const algo = ref(null)
const error = ref(false)

const details = computed(() => algo.value?.details || {})
const t = (obj) => obj?.[locale.value] || obj?.en || ''
const steps = computed(() => details.value.how_it_works?.[locale.value] || details.value.how_it_works?.en || [])
const params = computed(() => details.value.parameters?.[locale.value] || details.value.parameters?.en || [])
const uses = computed(() => details.value.uses?.[locale.value] || details.value.uses?.en || [])

function algoIcon(type) {
  if (type === 'attack') return 'fa-solid fa-burst'
  if (type === 'hashing') return 'fa-solid fa-fingerprint'
  return 'fa-solid fa-key'
}

async function load() {
  error.value = false
  algo.value = null
  try {
    const { data } = await api.get(`/algorithms/${route.params.id}`)
    algo.value = data
  } catch {
    error.value = true
  }
}
onMounted(load)
watch(() => route.params.id, load)
</script>

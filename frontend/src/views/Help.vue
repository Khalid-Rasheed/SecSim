<!--
  Help — FAQ-only page (MVP). Searchable, collapsible questions,
  bilingual from i18n. Designed to expand later with tabs.
-->
<template>
  <div class="max-w-4xl mx-auto px-4 py-10">
    <p class="eyebrow mb-2"><i class="fa-solid fa-circle-question me-2"></i>{{ $t('help.title') }}</p>
    <h1 class="font-display text-3xl font-bold mb-1">{{ $t('help.title') }}</h1>
    <p class="text-muted text-sm mb-6">{{ $t('help.subtitle') }}</p>

    <!-- Search -->
    <div class="mb-6">
      <div class="relative">
        <i class="fa-solid fa-magnifying-glass absolute start-3 top-1/2 -translate-y-1/2 text-muted text-xs"></i>
        <input
          v-model="query"
          class="field w-full ps-8 pe-3 py-2 text-sm"
          :placeholder="$t('help.search')"
          dir="auto"
        />
      </div>
    </div>

    <p v-if="!filtered.length" class="text-xs text-muted text-center py-4">
      {{ $t('help.no_results') }}
    </p>

    <!-- FAQ Accordion -->
    <div v-else class="space-y-2">
      <div
        v-for="(item, i) in filtered"
        :key="i"
        class="panel rounded-xl overflow-hidden border border-[rgba(148,163,184,0.16)]"
      >
        <button
          class="w-full flex items-center justify-between p-4 text-start focus:outline-none focus:ring-2 focus:ring-cipher/50"
          :aria-expanded="openIdx === i"
          @click="toggle(i)"
        >
          <span class="font-semibold text-sm text-mist pr-4 text-start">{{ item.q }}</span>
          <i
            class="fa-solid fa-chevron-down text-muted transition-transform duration-200 shrink-0"
            :class="{ 'rotate-180': openIdx === i }"
          ></i>
        </button>
        <div
          v-show="openIdx === i"
          class="px-4 pb-4 border-t border-[rgba(148,163,184,0.12)] pt-3"
        >
          <p class="text-sm text-muted leading-relaxed">{{ item.a }}</p>
        </div>
      </div>
    </div>

    <!-- Footer hint -->
    <div class="panel p-4 mt-8 flex flex-col sm:flex-row items-center gap-3 justify-between">
      <p class="text-xs text-muted">
        <i class="fa-solid fa-lightbulb text-keyamber me-1.5"></i>{{ $t('help.cta_text') }}
      </p>
      <div class="flex gap-2">
        <router-link to="/learn" class="btn-cipher px-4 py-2 text-xs">
          <i class="fa-solid fa-route me-1.5"></i>{{ $t('ux.learn.eyebrow') }}
        </router-link>
        <router-link to="/simulator" class="btn-ghost px-4 py-2 text-xs">
          <i class="fa-solid fa-flask me-1.5"></i>{{ $t('nav.simulator') }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { tm } = useI18n()
const openIdx = ref(null)
const query = ref('')

/** FAQ items from i18n (both languages) — uses $tm pattern like Home features. */
const faqItems = computed(() => {
  try {
    const items = tm('help.faq.items')
    return Array.isArray(items) ? items : []
  } catch {
    return []
  }
})

const filtered = computed(() => {
  if (!query.value.trim()) return faqItems.value
  const q = query.value.trim().toLowerCase()
  return faqItems.value.filter(
    (item) => item.q.toLowerCase().includes(q) || item.a.toLowerCase().includes(q)
  )
})

function toggle(idx) {
  openIdx.value = openIdx.value === idx ? null : idx
}
</script>
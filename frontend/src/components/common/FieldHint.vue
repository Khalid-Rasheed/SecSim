<!--
  FieldHint — one-line contextual help for simulator inputs.
  A small "?" badge showing the ux.hints.* sentence on hover AND
  keyboard focus (accessible via a real <button> + focus ring —
  touch users tap to toggle). Usage:
    <FieldHint tip-key="rsa_p" />
-->
<template>
  <!-- group-hover shows the bubble on desktop hover; tap toggles `open`
       for touch users; focus-within covers keyboard tab navigation. -->
  <span class="group relative inline-flex items-center align-middle">
    <button
      type="button"
      class="w-4 h-4 rounded-full bg-cipher/10 border border-cipher/30 text-cipher text-[0.55rem] font-bold inline-flex items-center justify-center ms-1.5 hover:bg-cipher/20 focus:outline-none focus:ring-2 focus:ring-cipher/50"
      :aria-label="$t('ux.what_is_this')"
      @click="open = !open"
      @blur="open = false"
    >
      <i class="fa-solid fa-question"></i>
    </button>
    <span
      :class="open ? '!block' : ''"
      class="absolute bottom-full mb-2 start-0 z-30 w-56 rounded-xl border border-cipher/30 bg-white p-3 text-xs text-mist leading-relaxed shadow-card hidden group-hover:block group-focus-within:block"
    >
      {{ $t('ux.hints.' + tipKey) }}
    </span>
  </span>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  /** Key inside ux.hints.* (e.g. "rsa_p", "collision_bits"). */
  tipKey: { type: String, required: true }
})

/** Touch toggle state (hover/focus are pure CSS via group classes). */
const open = ref(false)
</script>

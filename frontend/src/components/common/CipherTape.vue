<template>
  <div class="flex gap-1.5 flex-wrap" dir="ltr">
    <div
      v-for="(ch, i) in chars"
      :key="i"
      :class="['tape-cell', { lit: i <= litUpTo }]"
    >
      <span class="text-[0.65rem] text-muted leading-none">{{ ch.in }}</span>
      <i class="fa-solid fa-arrow-down text-[0.55rem] text-cipher my-0.5"></i>
      <span class="text-sm font-semibold text-mist leading-none">{{ ch.out }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  chars: { type: Array, default: () => [] }, // [{in, out}]
  litUpTo: { type: Number, default: -1 } // highlight cells 0..litUpTo (-1 = none, big = all)
})
</script>

<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path v-for="(d, i) in paths" :key="`${name}-${i}`" :d="d" />
  </svg>
</template>

<script>
import { computed } from 'vue'

// Feather/Heroicons-style paths — 24×24 viewBox, stroke-only
const ICONS = {
  home:           ['M3 10.5 12 3l9 7.5', 'M5 9.5V21h14V9.5'],
  package:        ['M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z', 'M3.27 6.96L12 12.01l8.73-5.05', 'M12 22.08V12'],
  'shopping-cart':['M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z', 'M3 6h18', 'M16 10a4 4 0 0 1-8 0'],
  'trending-up':  ['M23 6l-9.5 9.5-5-5L1 17', 'M17 6h6v6'],
  'refresh-cw':   ['M23 4v6h-6', 'M1 20v-6h6', 'M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15'],
  'bar-chart':    ['M12 20V10', 'M18 20V4', 'M6 20v-4'],
  'file-text':    ['M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z', 'M14 2v6h6', 'M16 13H8', 'M16 17H8', 'M10 9H8'],
  menu:           ['M4 6h16', 'M4 12h16', 'M4 18h16'],
  'chevron-left': ['M15 18l-6-6 6-6'],
  'chevron-right':['M9 18l6-6-6-6'],
}

export default {
  name: 'AppIcon',
  props: {
    name: { type: String, required: true }
  },
  setup(props) {
    const paths = computed(() => ICONS[props.name] ?? [])
    return { paths }
  }
}
</script>

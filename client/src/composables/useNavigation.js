import { computed } from 'vue'
import { useRouter } from 'vue-router'

// Navigation group definitions — order determines sidebar section order
const GROUPS = [
  { id: 'overview',    labelKey: 'nav.groups.overview' },
  { id: 'operations', labelKey: 'nav.groups.operations' },
  { id: 'finance',    labelKey: 'nav.groups.finance' },
]

export function useNavigation() {
  const router = useRouter()

  const groups = computed(() => {
    const items = router.getRoutes()
      .filter(r => r.meta?.nav)
      .map(r => ({ path: r.path, ...r.meta.nav }))
      .sort((a, b) => a.order - b.order)

    return GROUPS
      .map(g => ({ ...g, items: items.filter(i => i.group === g.id) }))
      .filter(g => g.items.length > 0)
  })

  return { groups }
}

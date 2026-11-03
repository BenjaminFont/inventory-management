import { ref, watch } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'
const readPref = () => {
  try { return localStorage.getItem(STORAGE_KEY) === '1' } catch { return false }
}

// Module-level refs so every component shares one state instance
const collapsed = ref(readPref())
const drawerOpen = ref(false)

watch(collapsed, v => {
  try { localStorage.setItem(STORAGE_KEY, v ? '1' : '0') } catch { /* private browsing */ }
})

export function useSidebar() {
  return {
    collapsed,
    drawerOpen,
    toggleCollapsed: () => { collapsed.value = !collapsed.value },
    openDrawer:  () => { drawerOpen.value = true },
    closeDrawer: () => { drawerOpen.value = false },
  }
}

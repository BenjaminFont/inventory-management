<template>
  <header class="topbar">
    <!-- Mobile: hamburger to open the drawer -->
    <button
      ref="menuBtn"
      class="menu-btn"
      type="button"
      :aria-label="t('nav.openMenu')"
      @click="openDrawer"
    >
      <AppIcon name="menu" />
    </button>

    <!-- Current page title from route meta -->
    <div class="topbar-title">{{ title }}</div>

    <!-- Right-side actions: LanguageSwitcher -->
    <div class="topbar-actions">
      <LanguageSwitcher />
    </div>
  </header>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../AppIcon.vue'
import LanguageSwitcher from '../LanguageSwitcher.vue'
import { useSidebar } from '../../composables/useSidebar'
import { useI18n } from '../../composables/useI18n'

export default {
  name: 'AppTopbar',
  components: { AppIcon, LanguageSwitcher },
  setup() {
    const { drawerOpen, openDrawer } = useSidebar()
    const { t } = useI18n()
    const route = useRoute()
    const menuBtn = ref(null)

    // Translate the current route's nav label key
    const title = computed(() =>
      route.meta?.nav ? t(route.meta.nav.labelKey) : ''
    )

    // Return focus to the hamburger button when the drawer closes
    // (on desktop the button is hidden so focus() does nothing — harmless)
    watch(drawerOpen, open => {
      if (!open) menuBtn.value?.focus?.()
    })

    return { t, title, menuBtn, openDrawer }
  }
}
</script>

<style>
.topbar {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  height: var(--topbar-h);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding-inline: var(--page-pad);
  /* Frosted-glass effect */
  background: color-mix(in srgb, var(--color-surface) 88%, transparent);
  backdrop-filter: saturate(1.4) blur(8px);
  border-bottom: 1px solid var(--color-border);
}

.topbar-title {
  font-weight: var(--weight-semibold);
  font-size: var(--text-base);
  color: var(--color-text);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.topbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* Menu button only visible on mobile */
.menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-muted);
  cursor: pointer;
  flex-shrink: 0;
}
.menu-btn:hover { background: var(--color-surface-muted); color: var(--color-text); }
.menu-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
.menu-btn svg { width: 20px; height: 20px; }

@media (max-width: 767px) {
  .menu-btn { display: inline-flex; }
}
</style>

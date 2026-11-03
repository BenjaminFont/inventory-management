<template>
  <div class="app-shell" :class="{ 'is-collapsed': collapsed }">
    <!-- Skip-to-content link for keyboard/screen-reader users -->
    <a class="skip-link" href="#main-content">{{ t('a11y.skipToContent') }}</a>

    <AppSidebar>
      <!-- Forward App.vue's sidebar-footer slot into AppSidebar's footer slot -->
      <template v-if="$slots['sidebar-footer']" #footer>
        <slot name="sidebar-footer" />
      </template>
    </AppSidebar>

    <div class="app-main">
      <AppTopbar />
      <!-- Subbar slot: FilterBar renders here, directly below the topbar -->
      <slot name="subbar" />
      <main id="main-content" class="app-content" tabindex="-1">
        <slot />
      </main>
    </div>
  </div>
</template>

<script>
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'
import { useSidebar } from '../../composables/useSidebar'
import { useI18n } from '../../composables/useI18n'

export default {
  name: 'AppShell',
  components: { AppSidebar, AppTopbar },
  setup() {
    const { collapsed } = useSidebar()
    const { t } = useI18n()
    return { collapsed, t }
  }
}
</script>

<style>
/* Shell grid: sidebar column | main column */
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-w) minmax(0, 1fr);
  min-height: 100dvh;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
}
.app-shell.is-collapsed {
  grid-template-columns: var(--sidebar-w-collapsed) minmax(0, 1fr);
}

/*
 * min-width: 0 prevents the main column from growing past its grid cell
 * when wide tables or charts overflow — they scroll inside instead of
 * widening the whole page.
 * NO overflow: hidden/auto here — that would break position: sticky in
 * Spending.vue and Orders.vue.
 */
.app-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  margin-inline: auto;
  padding: var(--page-pad);
  display: grid;
  gap: var(--space-6);
  align-content: start;
}
/* Suppress focus ring — the skip link focuses #main-content programmatically */
.app-content:focus { outline: none; }

/* Skip link: off-screen by default, visible on focus */
.skip-link {
  position: absolute;
  left: -999px;
  top: var(--space-2);
  z-index: var(--z-modal);
  background: var(--color-surface);
  color: var(--color-primary);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  text-decoration: none;
}
.skip-link:focus { left: var(--space-2); }

/* Tablet: always collapsed rail (no JS toggle) */
@media (min-width: 768px) and (max-width: 1023px) {
  .app-shell,
  .app-shell.is-collapsed {
    grid-template-columns: var(--sidebar-w-collapsed) minmax(0, 1fr);
  }
}

/* Mobile: sidebar slides off-canvas; main takes full width */
@media (max-width: 767px) {
  .app-shell,
  .app-shell.is-collapsed {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>

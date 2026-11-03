<template>
  <!-- Mobile overlay: closes the drawer on click -->
  <div v-if="drawerOpen" class="sidebar-overlay" @click="closeDrawer" />

  <aside
    ref="panel"
    class="sidebar"
    :class="{ 'is-open': drawerOpen, 'is-collapsed': collapsed }"
    :aria-label="t('nav.primary')"
    @keydown.esc="closeDrawer"
  >
    <!-- Brand / logo -->
    <div class="sidebar-brand">
      <div class="brand-mark" aria-hidden="true"></div>
      <span class="brand-name label">{{ t('nav.companyName') }}</span>
    </div>

    <!-- Navigation grouped by section -->
    <nav class="sidebar-nav">
      <div v-for="group in groups" :key="group.id" class="nav-group">
        <div class="nav-group-label label">{{ t(group.labelKey) }}</div>
        <router-link
          v-for="item in group.items"
          :key="item.path"
          :to="item.path"
          custom
          v-slot="{ href, navigate, isActive, isExactActive }"
        >
          <!--
            Root route ('/') must use isExactActive to avoid highlighting
            on every page — all routes are children of '/' for vue-router.
            aria-label/title are always set: the tablet rail hides labels via
            CSS media query (collapsed ref stays false), so JS can't tell
            when the icon is the only visible content.
          -->
          <a
            :href="href"
            class="nav-item"
            :class="{ active: item.path === '/' ? isExactActive : isActive }"
            :aria-current="(item.path === '/' ? isExactActive : isActive) ? 'page' : undefined"
            :aria-label="t(item.labelKey)"
            :title="t(item.labelKey)"
            @click="navigate"
          >
            <AppIcon :name="item.icon" class="nav-icon" />
            <span class="label">{{ t(item.labelKey) }}</span>
          </a>
        </router-link>
      </div>
    </nav>

    <!-- Footer: profile slot + collapse toggle -->
    <div class="sidebar-footer">
      <slot name="footer" />
      <button
        class="collapse-btn"
        type="button"
        :aria-label="t(collapsed ? 'nav.expand' : 'nav.collapse')"
        @click="toggleCollapsed"
      >
        <AppIcon :name="collapsed ? 'chevron-right' : 'chevron-left'" />
      </button>
    </div>
  </aside>
</template>

<script>
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../AppIcon.vue'
import { useSidebar } from '../../composables/useSidebar'
import { useNavigation } from '../../composables/useNavigation'
import { useI18n } from '../../composables/useI18n'

export default {
  name: 'AppSidebar',
  components: { AppIcon },
  setup() {
    const { collapsed, drawerOpen, toggleCollapsed, closeDrawer } = useSidebar()
    const { groups } = useNavigation()
    const { t } = useI18n()
    const route = useRoute()
    const panel = ref(null)

    // Close mobile drawer on every navigation
    watch(() => route.fullPath, closeDrawer)

    // When drawer opens: lock body scroll and move focus into the panel
    watch(drawerOpen, async open => {
      document.documentElement.style.overflow = open ? 'hidden' : ''
      if (open) {
        await nextTick()
        panel.value?.querySelector('a, button')?.focus()
      }
    })

    return { collapsed, drawerOpen, toggleCollapsed, closeDrawer, groups, t, panel }
  }
}
</script>

<style>
/* ─── Sidebar panel ────────────────────────────────────────────────── */
.sidebar {
  /* Sticky within the grid column so it doesn't scroll with the page */
  position: sticky;
  top: 0;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  /*
   * No overflow clipping on the panel itself: the ProfileMenu dropdown in the
   * footer is wider than the sidebar (esp. the 72px rail) and must spill over
   * the main column. Scrolling lives on .sidebar-nav instead. z-index keeps
   * that spill-over above the sticky topbar/FilterBar.
   */
  overflow: visible;
  z-index: var(--z-dropdown);
  /* Ensure drawers animate smoothly (reduced-motion override below) */
  transition: width 0.2s ease;
}

/* Brand strip */
.sidebar-brand {
  height: var(--topbar-h);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-inline: var(--space-5);
  font-weight: var(--weight-semibold);
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border);
}

.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  flex-shrink: 0;
}

.brand-name {
  font-size: var(--text-base);
  color: var(--color-text);
  white-space: nowrap;
}

/* Nav area */
.sidebar-nav {
  flex: 1;
  padding: var(--space-3);
  display: grid;
  gap: var(--space-5);
  align-content: start;
  /* min-height: 0 lets this flex child shrink so it scrolls instead of the panel */
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-group { display: grid; gap: 2px; }

.nav-group-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  padding: var(--space-2) var(--space-3);
}

/* Nav item */
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 38px;
  padding-inline: var(--space-3);
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  white-space: nowrap;
  transition: background 0.15s ease, color 0.15s ease;
}
.nav-item:hover { background: var(--sidebar-item-hover-bg); color: var(--color-text); }
.nav-item.active {
  background: var(--sidebar-item-active-bg);
  color: var(--color-primary);
}
.nav-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.nav-icon { width: 18px; height: 18px; flex: none; }

/* Footer */
.sidebar-footer {
  border-top: 1px solid var(--color-border);
  padding: var(--space-3);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-muted);
  cursor: pointer;
  margin-left: auto;
  flex-shrink: 0;
}
.collapse-btn:hover { background: var(--color-surface-muted); color: var(--color-text); }
.collapse-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
.collapse-btn svg { width: 16px; height: 16px; }

/* ─── Collapsed / icon-rail state ───────────────────────────────────── */
/* Hide text labels; center icons */
.sidebar.is-collapsed .label { display: none; }
.sidebar.is-collapsed .nav-item { justify-content: center; padding-inline: 0; }
.sidebar.is-collapsed .sidebar-brand { justify-content: center; padding-inline: 0; }

/*
 * Rail footer: the 72px column can't fit avatar + name + chevron + toggle
 * side by side (the expand button was pushed out of view, trapping the user
 * in collapsed mode). Stack vertically and reduce ProfileMenu to its avatar.
 * ProfileMenu styles are scoped, so these unscoped selectors (higher
 * specificity) override them only inside the rail.
 */
.sidebar.is-collapsed .sidebar-footer {
  flex-direction: column;
  padding-inline: var(--space-2);
}
.sidebar.is-collapsed .collapse-btn { margin-left: 0; }
.sidebar.is-collapsed .profile-button {
  width: auto;
  padding: 0;
  border-color: transparent;
  background: transparent;
  border-radius: 50%;
}
.sidebar.is-collapsed .profile-name,
.sidebar.is-collapsed .profile-button .chevron { display: none; }

/* Tablet (768–1023px): always rail, collapse button hidden */
@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar .label { display: none; }
  .sidebar .nav-item { justify-content: center; padding-inline: 0; }
  .sidebar .sidebar-brand { justify-content: center; padding-inline: 0; }
  .collapse-btn { display: none; }
  /* Same avatar-only footer as the collapsed rail above */
  .sidebar .sidebar-footer { justify-content: center; padding-inline: var(--space-2); }
  /* Extra .sidebar-footer bumps specificity past ProfileMenu's scoped rule */
  .sidebar .sidebar-footer .profile-button {
    width: auto;
    padding: 0;
    border-color: transparent;
    background: transparent;
    border-radius: 50%;
  }
  .sidebar .profile-name,
  .sidebar .profile-button .chevron { display: none; }
}

/* ─── Mobile: off-canvas drawer ─────────────────────────────────────── */
@media (max-width: 767px) {
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    width: min(280px, 85vw);
    z-index: var(--z-drawer);
    transform: translateX(-100%);
    transition: transform 0.2s ease;
  }
  .sidebar.is-open {
    transform: none;
    box-shadow: var(--shadow-lg);
  }
  /* Show full labels even when the global collapsed ref is true */
  .sidebar .label { display: revert; }
  .sidebar .nav-item { justify-content: flex-start; padding-inline: var(--space-3); }
  .sidebar .sidebar-brand { justify-content: flex-start; padding-inline: var(--space-5); }
  .collapse-btn { display: none; }

  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: rgb(15 23 42 / 0.4);
    z-index: var(--z-overlay);
  }
}

@media (prefers-reduced-motion: reduce) {
  .sidebar { transition: none; }
}
</style>

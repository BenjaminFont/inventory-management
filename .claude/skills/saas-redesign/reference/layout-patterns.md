# Layout patterns for the SaaS redesign

Reference implementations for the shell, sidebar, navigation model and tokens. Adapt names, colors and syntax (`<script setup>` vs `setup()`, JS vs TS) to the project. If the project uses Tailwind or a UI library, translate these patterns into that system rather than adding this CSS.

## 1. Tokens

Map the color roles to the project's existing palette. The values below are a neutral slate default.

```css
/* src/styles/tokens.css: imported once from main.js */
:root {
  /* Color roles */
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f5f9;
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-text: #0f172a;
  --color-text-muted: #64748b;
  --color-primary: #2563eb;
  --color-primary-soft: #eff6ff;
  --color-success: #059669;
  --color-warning: #d97706;
  --color-danger: #dc2626;
  --color-info: #0284c7;

  /* Sidebar (light by default; a dark sidebar swaps these four) */
  --sidebar-bg: #ffffff;
  --sidebar-text: #475569;
  --sidebar-text-active: #0f172a;
  --sidebar-item-active-bg: #f1f5f9;

  /* Spacing: 4px base */
  --space-1: 4px;  --space-2: 8px;   --space-3: 12px;  --space-4: 16px;
  --space-5: 20px; --space-6: 24px;  --space-8: 32px;  --space-10: 40px;
  --space-12: 48px; --space-16: 64px;

  /* Type */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --text-xs: 0.75rem;  --text-sm: 0.875rem; --text-base: 0.9375rem;
  --text-lg: 1.125rem; --text-xl: 1.375rem; --text-2xl: 1.75rem;
  --leading-tight: 1.25; --leading-normal: 1.55;

  /* Shape and depth */
  --radius-sm: 6px; --radius-md: 8px; --radius-lg: 12px;
  --shadow-sm: 0 1px 2px rgb(15 23 42 / 0.05);
  --shadow-md: 0 4px 12px rgb(15 23 42 / 0.08);
  --shadow-lg: 0 12px 32px rgb(15 23 42 / 0.12);

  /* Layout */
  --sidebar-w: 248px;
  --sidebar-w-collapsed: 72px;
  --topbar-h: 60px;
  --content-max: 1440px;
  --page-pad: var(--space-8);

  /* Layers */
  --z-sticky: 20; --z-overlay: 40; --z-drawer: 50; --z-modal: 60;
}

@media (max-width: 767px) {
  :root { --page-pad: var(--space-4); }
}
```

## 2. Navigation model in route meta

Use one source of truth, so the sidebar, page titles and breadcrumbs never drift apart.

```js
// main.js (or router/index.js)
const routes = [
  { path: '/', component: Dashboard,
    meta: { nav: { labelKey: 'nav.overview', icon: 'home', group: 'overview', order: 10 } } },
  { path: '/orders', component: Orders,
    meta: { nav: { labelKey: 'nav.orders', icon: 'orders', group: 'operations', order: 30 } } },
  // A route without meta.nav is reachable but hidden from the sidebar
]
```

```js
// composables/useNavigation.js
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const GROUPS = [
  { id: 'overview', labelKey: 'nav.groups.overview' },
  { id: 'operations', labelKey: 'nav.groups.operations' },
  { id: 'finance', labelKey: 'nav.groups.finance' },
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
      .filter(g => g.items.length)
  })
  return { groups }
}
```

## 3. Shell state

Holds the collapsed rail and the mobile drawer. The refs live at module level, so every component shares one state.

```js
// composables/useSidebar.js
import { ref, watch } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'
const readPref = () => { try { return localStorage.getItem(STORAGE_KEY) === '1' } catch { return false } }

const collapsed = ref(readPref())
const drawerOpen = ref(false)

watch(collapsed, v => { try { localStorage.setItem(STORAGE_KEY, v ? '1' : '0') } catch { /* private mode */ } })

export function useSidebar() {
  return {
    collapsed,
    drawerOpen,
    toggleCollapsed: () => { collapsed.value = !collapsed.value },
    openDrawer: () => { drawerOpen.value = true },
    closeDrawer: () => { drawerOpen.value = false },
  }
}
```

## 4. AppShell

```vue
<!-- components/layout/AppShell.vue -->
<template>
  <div class="app-shell" :class="{ 'is-collapsed': collapsed }">
    <a class="skip-link" href="#main-content">{{ t('a11y.skipToContent') }}</a>
    <AppSidebar />
    <div class="app-main">
      <AppTopbar />
      <slot name="subbar" /> <!-- e.g. a global FilterBar -->
      <main id="main-content" class="app-content" tabindex="-1">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'
import { useSidebar } from '../../composables/useSidebar'
import { useI18n } from '../../composables/useI18n' // or vue-i18n, whichever the project uses
const { collapsed } = useSidebar()
const { t } = useI18n()
</script>

<style>
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-w) minmax(0, 1fr);
  min-height: 100dvh;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
}
.app-shell.is-collapsed { grid-template-columns: var(--sidebar-w-collapsed) minmax(0, 1fr); }
/* min-width: 0 lets wide tables scroll inside the column instead of widening the page */
.app-main { min-width: 0; display: flex; flex-direction: column; }
.app-content {
  width: 100%;
  max-width: var(--content-max);
  margin-inline: auto;
  padding: var(--page-pad);
  display: grid;
  gap: var(--space-6);
  align-content: start;
}
.app-content:focus { outline: none; }
.skip-link { position: absolute; left: -999px; top: var(--space-2); z-index: var(--z-modal); }
.skip-link:focus { left: var(--space-2); background: var(--color-surface); padding: var(--space-2) var(--space-3); border-radius: var(--radius-sm); }

@media (min-width: 768px) and (max-width: 1023px) {
  .app-shell { grid-template-columns: var(--sidebar-w-collapsed) minmax(0, 1fr); }
}
@media (max-width: 767px) {
  .app-shell, .app-shell.is-collapsed { grid-template-columns: minmax(0, 1fr); }
}
</style>
```

`App.vue` then becomes:

```vue
<template>
  <AppShell>
    <template #subbar><FilterBar /></template>
    <router-view />
  </AppShell>
  <!-- keep root-mounted modals here, unchanged -->
</template>
```

## 5. AppSidebar

```vue
<!-- components/layout/AppSidebar.vue -->
<template>
  <div v-if="drawerOpen" class="sidebar-overlay" @click="closeDrawer" />
  <aside
    ref="panel"
    class="sidebar"
    :class="{ 'is-open': drawerOpen, 'is-collapsed': collapsed }"
    :aria-label="t('nav.primary')"
    @keydown.esc="closeDrawer"
  >
    <div class="sidebar-brand">
      <slot name="brand"><span class="brand-mark" aria-hidden="true" /> <span class="brand-name label">{{ t('nav.companyName') }}</span></slot>
    </div>

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
          <!-- The root route must use exact matching, or it would light up on every page -->
          <a
            :href="href"
            class="nav-item"
            :class="{ active: item.path === '/' ? isExactActive : isActive }"
            :aria-current="(item.path === '/' ? isExactActive : isActive) ? 'page' : undefined"
            :title="collapsed ? t(item.labelKey) : undefined"
            @click="navigate"
          >
            <AppIcon :name="item.icon" class="nav-icon" />
            <span class="label">{{ t(item.labelKey) }}</span>
          </a>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer" />
      <button class="collapse-btn" type="button" :aria-label="t(collapsed ? 'nav.expand' : 'nav.collapse')" @click="toggleCollapsed">
        <AppIcon :name="collapsed ? 'chevron-right' : 'chevron-left'" />
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../AppIcon.vue'
import { useSidebar } from '../../composables/useSidebar'
import { useNavigation } from '../../composables/useNavigation'
import { useI18n } from '../../composables/useI18n'

const { collapsed, drawerOpen, toggleCollapsed, closeDrawer } = useSidebar()
const { groups } = useNavigation()
const { t } = useI18n()
const route = useRoute()
const panel = ref(null)

// The mobile drawer closes whenever navigation happens
watch(() => route.fullPath, closeDrawer)

// Move focus into the drawer when it opens and lock page scroll behind it
watch(drawerOpen, async open => {
  document.documentElement.style.overflow = open ? 'hidden' : ''
  if (open) { await nextTick(); panel.value?.querySelector('a, button')?.focus() }
})
</script>

<style>
.sidebar {
  position: sticky; top: 0; height: 100dvh; /* stays put while the main column scrolls */
  display: flex; flex-direction: column;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--color-border);
  overflow-y: auto; overflow-x: hidden;
}
.sidebar-brand { height: var(--topbar-h); display: flex; align-items: center; gap: var(--space-3); padding-inline: var(--space-5); font-weight: 600; }
.sidebar-nav { flex: 1; padding: var(--space-3); display: grid; gap: var(--space-5); align-content: start; }
.nav-group { display: grid; gap: 2px; }
.nav-group-label { font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--color-text-muted); padding: var(--space-2) var(--space-3); }
.nav-item {
  display: flex; align-items: center; gap: var(--space-3);
  height: 38px; padding-inline: var(--space-3);
  border-radius: var(--radius-md);
  color: var(--sidebar-text); text-decoration: none; font-size: var(--text-sm); font-weight: 500;
  white-space: nowrap;
}
.nav-item:hover { background: var(--color-surface-muted); color: var(--sidebar-text-active); }
.nav-item.active { background: var(--sidebar-item-active-bg); color: var(--color-primary); }
.nav-item:focus-visible, .collapse-btn:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }
.nav-icon { width: 18px; height: 18px; flex: none; }
.sidebar-footer { border-top: 1px solid var(--color-border); padding: var(--space-3); display: flex; align-items: center; gap: var(--space-2); }

/* Icon rail: hide text, center icons */
.sidebar.is-collapsed .label { display: none; }
.sidebar.is-collapsed .nav-item { justify-content: center; padding-inline: 0; }
@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar .label { display: none; }
  .sidebar .nav-item { justify-content: center; padding-inline: 0; }
}

/* Mobile: off-canvas drawer */
@media (max-width: 767px) {
  .sidebar {
    position: fixed; inset: 0 auto 0 0; width: min(280px, 85vw); z-index: var(--z-drawer);
    transform: translateX(-100%); transition: transform 0.2s ease;
  }
  .sidebar.is-open { transform: none; box-shadow: var(--shadow-lg); }
  .sidebar .label { display: revert; }
  .sidebar .nav-item { justify-content: flex-start; padding-inline: var(--space-3); }
  .collapse-btn { display: none; }
  .sidebar-overlay { position: fixed; inset: 0; background: rgb(15 23 42 / 0.4); z-index: var(--z-overlay); }
}
@media (prefers-reduced-motion: reduce) { .sidebar { transition: none; } }
</style>
```

## 6. AppTopbar

```vue
<template>
  <header class="topbar">
    <button ref="menuBtn" class="menu-btn" type="button" :aria-label="t('nav.openMenu')" @click="openDrawer">
      <AppIcon name="menu" />
    </button>
    <div class="topbar-title">{{ title }}</div>
    <div class="topbar-actions"><slot /></div> <!-- locale switcher, notifications, profile -->
  </header>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../AppIcon.vue'
import { useSidebar } from '../../composables/useSidebar'
import { useI18n } from '../../composables/useI18n'

const { drawerOpen, openDrawer } = useSidebar()
const { t } = useI18n()
const route = useRoute()
const menuBtn = ref(null)
const title = computed(() => route.meta?.nav ? t(route.meta.nav.labelKey) : '')

// Return focus to the menu button when the drawer closes
watch(drawerOpen, open => { if (!open) menuBtn.value?.focus?.() })
</script>

<style>
.topbar {
  position: sticky; top: 0; z-index: var(--z-sticky);
  height: var(--topbar-h); display: flex; align-items: center; gap: var(--space-4);
  padding-inline: var(--page-pad);
  background: color-mix(in srgb, var(--color-surface) 88%, transparent);
  backdrop-filter: saturate(1.4) blur(8px);
  border-bottom: 1px solid var(--color-border);
}
.topbar-title { font-weight: 600; font-size: var(--text-base); min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.topbar-actions { margin-left: auto; display: flex; align-items: center; gap: var(--space-3); }
.menu-btn { display: none; }
@media (max-width: 767px) { .menu-btn { display: inline-flex; } }
</style>
```

Note: the focus-return watcher fires on every close, including closes caused by navigation. On desktop the button is hidden and `focus()` on a hidden element does nothing, so this is harmless.

## 7. PageHeader and surfaces

```vue
<!-- components/PageHeader.vue -->
<template>
  <div class="page-header">
    <div class="page-header-text">
      <h1>{{ title }}</h1>
      <p v-if="description">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="page-header-actions"><slot name="actions" /></div>
  </div>
</template>
<script setup>
defineProps({ title: { type: String, required: true }, description: { type: String, default: '' } })
</script>
<style>
.page-header { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: var(--space-4); }
.page-header-text { min-width: 0; display: grid; gap: var(--space-1); }
.page-header h1 { margin: 0; font-size: var(--text-2xl); line-height: var(--leading-tight); letter-spacing: -0.01em; }
.page-header p { margin: 0; color: var(--color-text-muted); font-size: var(--text-sm); max-width: 70ch; }
.page-header-actions { display: flex; gap: var(--space-2); }
</style>
```

Shared surface styles, in a global stylesheet next to the tokens:

```css
.card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.card-header { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); padding: var(--space-4) var(--space-5); border-bottom: 1px solid var(--color-border); }
.card-body { padding: var(--space-5); }
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4); }
.table-scroll { overflow-x: auto; }
.table-scroll table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.table-scroll th { font-size: var(--text-xs); text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-muted); text-align: left; padding: var(--space-3) var(--space-4); background: var(--color-surface-muted); }
.table-scroll td { padding: var(--space-3) var(--space-4); border-top: 1px solid var(--color-border); font-size: var(--text-sm); }
.btn { display: inline-flex; align-items: center; gap: var(--space-2); height: 36px; padding-inline: var(--space-4); border-radius: var(--radius-md); font-weight: 500; font-size: var(--text-sm); border: 1px solid var(--color-border); background: var(--color-surface); color: var(--color-text); cursor: pointer; }
.btn-primary { background: var(--color-primary); border-color: var(--color-primary); color: #fff; }
.btn:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }
```

## 8. Icons

Render a small `AppIcon` component from a map of inline SVG paths: 24×24 viewBox, `stroke="currentColor"`, `fill="none"`, stroke width 1.75. Icons then inherit text color in every state. Keep the map to the icons the nav and top bar actually use.

```vue
<template>
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path v-for="(d, i) in paths" :key="`${name}-${i}`" :d="d" />
  </svg>
</template>
<script setup>
import { computed } from 'vue'
const ICONS = {
  home: ['M3 10.5 12 3l9 7.5', 'M5 9.5V21h14V9.5'],
  menu: ['M4 6h16', 'M4 12h16', 'M4 18h16'],
  'chevron-left': ['M15 18l-6-6 6-6'],
  'chevron-right': ['M9 18l6-6-6-6'],
  // add only what the nav uses
}
const props = defineProps({ name: { type: String, required: true } })
const paths = computed(() => ICONS[props.name] ?? [])
</script>
```

## 9. Vue-specific pitfalls

- **Scoped styles don't reach child components.** Put shell and primitive styles in plain (unscoped) `<style>` blocks or a global stylesheet. Use `:deep()` only for one-off overrides.
- **Root route active state.** `isActive` on `/` matches only `/` for flat routes, but nested route records make it match ancestors. Use `isExactActive` for `/` explicitly, as above.
- **`position: sticky` silently fails** if any ancestor has `overflow: hidden|auto`. Keep overflow off `.app-shell` and `.app-main`.
- **Mobile viewport height.** Use `100dvh`, not `100vh`, or the drawer and sidebar are cut off behind mobile browser chrome.
- **Do not key or `v-if` the `<router-view>` wrapper** while toggling the sidebar. That remounts the page and refetches its data.
- **Teleport** modals to `body` if they were previously positioned relative to the old header.
- **Old global CSS** often styles bare elements (`header`, `nav`, `h2`). Grep for these selectors in `App.vue` and global styles, and remove or scope them, or they will restyle the new shell.

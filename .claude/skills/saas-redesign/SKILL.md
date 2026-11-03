---
name: saas-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface - a vertical navigation sidebar on the left instead of a top nav bar, a token-based spacing and type system, and consistent, polished page layouts. Use when the user asks to modernize, restyle, or "make professional" a Vue 3 app, move navigation into a sidebar, or apply a SaaS/dashboard look. Audits the current UI, proposes a plan for approval, then applies it and verifies in a browser.
---

# SaaS Redesign for Vue 3

Turn an existing Vue 3 app into a SaaS-style product UI: a left sidebar for navigation, a slim top bar for page context and global controls, and every page built from the same spacing, type and surface rules.

This is a **visual and structural** redesign. Routes, data loading, API calls, state, i18n keys and business logic stay exactly as they are. If a change would alter behavior, stop and ask.

Work in four phases. Do not skip the approval gate between Plan and Apply.

Patterns and code to reuse are in [reference/layout-patterns.md](reference/layout-patterns.md). Read it before Phase 2.

---

## Phase 1: Audit

Goal: know what exists before proposing anything. Record findings as you go; they feed the plan.

1. **Project rules.** Read every `CLAUDE.md` (root and nested) and any design docs. Note mandated colors, fonts, "no emoji" rules, component conventions, and workflow rules such as "delegate `.vue` edits to a subagent". Project rules override this skill.
2. **Stack** (`package.json`, `vite.config.*`, `main.js|ts`):
   - Vue and Vue Router versions; Options API, Composition API, `<script setup>`, or a mix.
   - Styling approach: scoped CSS, global CSS, Tailwind, CSS modules, Sass, or a UI library (Vuetify, PrimeVue, Element Plus, Naive UI, Quasar). **If a UI library or Tailwind is present, build on it. Never add a second styling system.**
   - TypeScript or plain JS. Match it.
3. **App shell.** Find where the current header and nav render (usually `App.vue` or a `layouts/` component). List everything in it: logo, nav links, search, filters, locale switcher, profile menu, notifications, modals mounted at the root.
4. **Navigation source.** Are links hardcoded in the template, or derived from the routes? List every route, its label, and whether it is reachable from the nav. Note routes with no nav entry and nav entries with no route.
5. **Global styles and tokens.** Find existing CSS variables, theme files, and where global styles live. Collect the colors, font stacks, radii, shadows and spacing values actually in use (grep for hex colors and `px` values) to see how inconsistent they are.
6. **Page anatomy.** Open each view. Note the repeated patterns: page title and description, stat cards, cards with headers, tables, filters, modals, empty and loading states, buttons, badges. These become the shared primitives.
7. **i18n and content length.** If there are multiple locales, note the longest nav labels. The sidebar must fit them.
8. **Current look.** If browser tooling is available (Playwright MCP, or headless Chrome), screenshot two or three representative routes at 1440px and 390px wide. These are the "before" images.

Summarize the audit for the user in a short list: stack, shell contents, routes, styling approach, and the main inconsistencies found.

---

## Phase 2: Plan

Read [reference/layout-patterns.md](reference/layout-patterns.md), then write a plan with these sections. Keep it concrete: file names, token names and values.

1. **Design tokens.** One tokens file (e.g. `src/styles/tokens.css`, or the theme config if Tailwind or a UI library is in use) containing:
   - Color roles, not raw hues: background, surface, muted surface, border, text, muted text, primary (plus its soft tint), success, warning, danger, info, and sidebar colors. **Map these to the project's existing palette.** Only invent colors where none exist.
   - Spacing on a 4px base: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64.
   - A type scale (about 6 steps), font weights, and line heights.
   - Radii (small, medium, large), two or three shadow levels, and z-index layers.
   - Layout sizes: sidebar width (around 240-260px), collapsed width (around 64-72px), top bar height (56-64px), and a content max width.
   - Dark mode **only** if the app already supports it or the user asks for it.
2. **Shell architecture.**
   - `AppShell`: a CSS grid of sidebar plus main column.
   - `AppSidebar`: brand, grouped nav, and a footer slot for the profile and settings.
   - `AppTopbar`: mobile menu button, page title or breadcrumb, and global controls.
   - Say which existing widgets move where. Typically the profile menu goes to the sidebar footer or top bar right, the locale switcher to the top bar, and global filters to a bar under the top bar or into the pages that use them.
3. **Navigation model.** One source of truth, preferably route `meta` (label key, icon, group, order). List the proposed groups (for example "Overview", "Operations", "Finance") and the order of items.
4. **Responsive behavior.**
   - At 1024px and wider: full sidebar, collapsible to an icon rail, with the preference remembered.
   - From 768px to 1023px: icon rail by default.
   - Below 768px: the sidebar becomes an off-canvas drawer opened from the top bar, with an overlay. It closes on route change, on Escape and on overlay click.
5. **Page scaffold.** A `PageHeader` component (title, optional description, actions slot) and a consistent content container. List each view and the shared primitives it will use: `PageHeader`, card, stat card, table wrapper, badge, button.
6. **Icons.** Inline SVG icon components, or the icon set the project already uses. No emoji. Add no icon dependency unless the user approves one.
7. **File list.** New files, modified files, and CSS to delete (the old top-nav styles).
8. **Risks.** For example: views with heavy scoped CSS that fights the new tokens, components that rely on the header's height, fixed-position elements, and very long translated labels.

Present the plan and **wait for explicit approval**. Adjust the plan and re-present it if the user asks for changes.

---

## Phase 3: Apply

Follow project workflow rules from the audit. For example, if CLAUDE.md requires `.vue` changes to go through a specific subagent, delegate those edits and give it the approved plan, the token file and the patterns reference.

Apply in this order, so the app stays runnable after each step:

1. **Tokens.** Add the tokens file and import it once in the app entry. Change nothing else yet.
2. **Shell.** Create `AppShell`, `AppSidebar`, `AppTopbar` and the nav config or route meta. Swap `App.vue` to render the shell around `<router-view>`. Move the existing header widgets into their planned slots **without changing their logic or props**. Keep root-mounted modals where they were.
3. **Primitives.** Add `PageHeader` and any shared card, table or badge styles. Prefer a small global component stylesheet over copying the same scoped CSS into every view.
4. **Views.** Migrate one view at a time:
   - Replace its ad-hoc page header with `PageHeader`.
   - Replace hardcoded colors, spacing and radii with tokens.
   - Normalize gaps between sections using grid or flex `gap`, not stacked margins.
   - Wrap tables in a horizontal-scroll container.
   - Leave the template's data bindings, `v-for` keys, events and computed properties untouched.
5. **Cleanup.** Delete the old top-nav markup and CSS, and any styles that are now dead. Grep for leftover hex colors in the files you touched.

Rules while applying:
- Do not rename routes, change URLs, rename i18n keys or change API calls.
- Add a new i18n key for every new user-facing string (for example "Collapse sidebar" or "Open menu"), in every locale file.
- Give every interactive element a visible `:focus-visible` style, and give icon-only buttons an `aria-label`.
- Respect `prefers-reduced-motion` for the drawer and collapse transitions.
- Comment non-obvious layout decisions, such as why a container is `min-width: 0` or why the sidebar is sticky.

---

## Phase 4: Verify

1. **Build:** `npm run build` (or the project's build script) must succeed with no new warnings. Remove the build output afterwards if it is not gitignored.
2. **Tests:** run any existing frontend and end-to-end tests.
3. **Browser check**, using Playwright MCP if available, otherwise headless Chrome. Visit **every route** at 1440px, 1024px and 390px, and confirm:
   - The active nav item is highlighted on each route, including the root route.
   - Collapse and expand work, and the setting survives a reload.
   - On mobile, the drawer opens, closes on navigation, Escape and overlay click, and returns focus to the menu button.
   - The page never scrolls horizontally. Wide tables scroll inside their container.
   - There are no console errors beyond ones that existed before.
   - Every locale fits: switch locales and check the longest labels in the sidebar and top bar.
   - You can tab through the sidebar, top bar and page in a sensible order, with focus always visible.
4. **Before and after:** take the same screenshots as in the audit and show them to the user.
5. **Report:** what changed, which files were touched, anything deferred, and any pre-existing issues you noticed but did not fix.

---

## Quality bar

- **Consistent rhythm:** the same page padding, section gap and card padding on every route.
- **Clear hierarchy:** one H1 per page, in `PageHeader`; card titles one step down; muted color for secondary text.
- **Calm surfaces:** borders or a light shadow, not both heavy at once. Use one radius scale everywhere.
- **Restraint:** the primary color is reserved for the active nav item, primary buttons, links and focus rings. Status colors are only for status.
- **Density fit for the job:** data tables stay compact (rows around 40-44px), forms get more air.
- **Tabular numbers** in tables, stat cards and anything else that lines up digits.

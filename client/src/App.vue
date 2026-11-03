<template>
  <AppShell>
    <!-- ProfileMenu lives in the sidebar footer -->
    <template #sidebar-footer>
      <ProfileMenu
        @show-profile-details="showProfileDetails = true"
        @show-tasks="showTasks = true"
      />
    </template>

    <!-- FilterBar renders in the subbar slot, directly below the topbar -->
    <template #subbar>
      <FilterBar />
    </template>

    <router-view />
  </AppShell>

  <!-- Root-mounted modals — unchanged internals, always present -->
  <ProfileDetailsModal
    :is-open="showProfileDetails"
    @close="showProfileDetails = false"
  />

  <TasksModal
    :is-open="showTasks"
    :tasks="tasks"
    @close="showTasks = false"
    @add-task="addTask"
    @delete-task="deleteTask"
    @toggle-task="toggleTask"
  />
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import AppShell from './components/layout/AppShell.vue'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'

export default {
  name: 'App',
  components: {
    AppShell,
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
/* ─── Reset ──────────────────────────────────────────────────────────── */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: var(--leading-normal);
}

/* ─── Page-level header ──────────────────────────────────────────────── */
/*
 * .page-header is rendered by PageHeader.vue (unscoped) and used by all
 * 8 views. Keep ALL existing class names so the views don't need changes
 * to their class strings.
 */
.page-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
}
.page-header-text {
  min-width: 0;
  display: grid;
  gap: var(--space-1);
}
.page-header h1 {
  margin: 0;
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  line-height: var(--leading-tight);
  letter-spacing: -0.01em;
  color: var(--color-text);
}
/* Views that still have .page-header h2 (transitional) */
.page-header h2 {
  margin: 0;
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  line-height: var(--leading-tight);
  letter-spacing: -0.01em;
  color: var(--color-text);
}
.page-header p {
  margin: 0;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  max-width: 70ch;
}
.page-header-actions { display: flex; gap: var(--space-2); }

/* ─── Stat cards ─────────────────────────────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
}

.stat-card {
  background: var(--color-surface);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.stat-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-md);
}
.stat-label {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}
.stat-value {
  font-size: 2.25rem;
  font-weight: var(--weight-bold);
  color: var(--color-text);
  letter-spacing: -0.025em;
  font-variant-numeric: tabular-nums;
}
.stat-card.warning .stat-value { color: var(--color-warning); }
.stat-card.success .stat-value { color: var(--color-success); }
.stat-card.danger  .stat-value { color: var(--color-danger); }
.stat-card.info    .stat-value { color: var(--color-info); }

/* ─── Cards ──────────────────────────────────────────────────────────── */
/*
 * Agreed treatment: 1px border + 12px radius (--radius-lg) + soft shadow.
 * margin-bottom is kept for existing views that rely on card spacing.
 */
.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-5);
  padding: var(--space-5);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}
.card-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
  color: var(--color-text);
  letter-spacing: -0.01em;
  margin: 0;
}

/* ─── Tables ─────────────────────────────────────────────────────────── */
.table-container { overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

thead {
  background: var(--color-surface-muted);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  font-weight: var(--weight-semibold);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ~40-44px row height with tabular-nums on cells */
td {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  font-variant-numeric: tabular-nums;
}

tbody tr { transition: background-color 0.1s ease; }
tbody tr:hover { background: var(--color-bg); }

/* ─── Badges ─────────────────────────────────────────────────────────── */
.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-pill);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  white-space: nowrap;
}
.badge.success    { background: var(--color-success-soft); color: var(--color-success-text); }
.badge.warning    { background: var(--color-warning-soft); color: var(--color-warning-text); }
.badge.danger     { background: var(--color-danger-soft);  color: var(--color-danger-text); }
.badge.info       { background: var(--color-info-soft);    color: var(--color-info-text); }
.badge.increasing { background: var(--color-success-soft); color: var(--color-success-text); }
.badge.decreasing { background: var(--color-danger-soft);  color: var(--color-danger-text); }
.badge.stable     { background: #e0e7ff; color: #3730a3; }
.badge.high       { background: var(--color-danger-soft);  color: var(--color-danger-text); }
.badge.medium     { background: var(--color-warning-soft); color: var(--color-warning-text); }
.badge.low        { background: var(--color-info-soft);    color: var(--color-info-text); }

/* ─── Loading / error states ─────────────────────────────────────────── */
.loading {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.error {
  background: var(--color-danger-soft);
  border: 1px solid #fca5a5;
  color: var(--color-danger-text);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: var(--text-sm);
}
</style>

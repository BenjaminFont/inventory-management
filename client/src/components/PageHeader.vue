<template>
  <div class="page-header">
    <div class="page-header-text">
      <h1>{{ title }}</h1>
      <p v-if="description">{{ description }}</p>
      <!-- Slot for extra content (e.g. a note paragraph) -->
      <slot />
    </div>
    <div v-if="$slots.actions" class="page-header-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageHeader',
  props: {
    title:       { type: String, required: true },
    description: { type: String, default: '' }
  }
}
</script>

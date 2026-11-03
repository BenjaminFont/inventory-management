<template>
  <div class="restocking">
    <PageHeader :title="t('restocking.title')" :description="t('restocking.description')">
      <p class="filters-note">{{ t('restocking.filtersNote') }}</p>
    </PageHeader>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="card budget-card">
        <div class="budget-row">
          <label for="restock-budget" class="budget-label">{{ t('restocking.budgetLabel') }}</label>
          <span class="budget-value">{{ formatMoney(budget, 0) }}</span>
        </div>
        <input
          id="restock-budget"
          class="budget-slider"
          type="range"
          min="0"
          :max="sliderMax"
          :step="BUDGET_STEP"
          v-model.number="budget"
        />
        <div class="budget-scale">
          <span>{{ formatMoney(0, 0) }}</span>
          <span>{{ formatMoney(sliderMax, 0) }}</span>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.budget') }}</div>
          <div class="stat-value">{{ formatMoney(budget) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.recommendedTotal') }}</div>
          <div class="stat-value">{{ formatMoney(recommendation.total) }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.remaining') }}</div>
          <div class="stat-value">{{ formatMoney(recommendation.remaining) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.items') }}</div>
          <div class="stat-value">{{ recommendation.items.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ recommendation.items.length }})</h3>
          <button
            type="button"
            class="place-order-btn"
            :disabled="recommendation.items.length === 0 || submitting || submittedOrder"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.submitting') : submittedOrder ? t('restocking.orderPlacedButton') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="submittedOrder" class="notice success-notice" role="status">
          {{ t('restocking.orderPlaced', { orderNumber: submittedOrder.order_number }) }}
          <router-link to="/orders">{{ t('restocking.viewOrders') }}</router-link>
        </div>
        <div v-if="submitError" class="notice error-notice" role="alert">{{ submitError }}</div>

        <div v-if="recommendation.items.length === 0" class="empty-state">
          {{ sliderMax === 0 ? t('restocking.noGaps') : t('restocking.empty') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.gap') }}</th>
                <th class="num">{{ t('restocking.table.quantity') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendation.items" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ translateProductName(item.item_name) }}</td>
                <td>
                  <span :class="['badge', item.trend]">{{ t(`trends.${item.trend}`) }}</span>
                </td>
                <td class="num">{{ item.gap }}</td>
                <td class="num"><strong>{{ item.quantity }}</strong></td>
                <td class="num">{{ formatMoney(item.unit_cost) }}</td>
                <td class="num"><strong>{{ formatMoney(item.line_total) }}</strong></td>
                <td class="num">{{ t('restocking.leadTimeDays', { count: item.lead_time_days }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'
import { recommendRestock, maxUsefulBudget } from '../utils/restocking'
import PageHeader from '../components/PageHeader.vue'

const BUDGET_STEP = 100

export default {
  name: 'Restocking',
  components: { PageHeader },
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()

    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(0)

    const submitting = ref(false)
    const submittedOrder = ref(null)
    const submitError = ref(null)

    // Slider max: cost of covering every gap, rounded up to the next step
    const sliderMax = computed(() => {
      const max = maxUsefulBudget(forecasts.value)
      return Math.ceil(max / BUDGET_STEP) * BUDGET_STEP
    })

    const recommendation = computed(() => recommendRestock(forecasts.value, budget.value))

    // Budget is held in USD; formatting converts to JPY when the locale is ja
    const formatMoney = (usd, decimals = 2) =>
      formatCurrencyWithDecimals(usd, currentCurrency.value, decimals)

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
        // Default to 50% of max, snapped to the slider step
        budget.value = Math.round(sliderMax.value * 0.5 / BUDGET_STEP) * BUDGET_STEP
      } catch (err) {
        error.value = t('restocking.loadFailed') + err.message
      } finally {
        loading.value = false
      }
    }

    // A previous confirmation/error no longer describes the current selection
    watch(budget, () => {
      submittedOrder.value = null
      submitError.value = null
    })

    // FastAPI 422 responses return detail as an array of { msg, loc } objects
    const formatErrorDetail = (err) => {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') return detail
      if (Array.isArray(detail)) {
        return detail.map(d => (typeof d === 'string' ? d : d.msg)).filter(Boolean).join('; ')
      }
      return t('restocking.orderFailed')
    }

    const placeOrder = async () => {
      if (submitting.value || submittedOrder.value || recommendation.value.items.length === 0) return
      submitting.value = true
      submittedOrder.value = null
      submitError.value = null
      try {
        // Server re-prices items itself; only SKU and quantity are sent
        submittedOrder.value = await api.createRestockOrder({
          budget: budget.value,
          items: recommendation.value.items.map(i => ({
            item_sku: i.item_sku,
            quantity: i.quantity
          }))
        })
      } catch (err) {
        submitError.value = formatErrorDetail(err) || t('restocking.orderFailed')
        console.error('Restock order failed:', err)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      BUDGET_STEP,
      loading,
      error,
      budget,
      sliderMax,
      recommendation,
      submitting,
      submittedOrder,
      submitError,
      formatMoney,
      translateProductName,
      placeOrder
    }
  }
}
</script>

<style scoped>
.filters-note {
  margin-top: 0.25rem;
  font-size: 0.813rem;
  font-style: italic;
}

.budget-card {
  padding: 1.25rem 1.5rem;
}

.budget-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.75rem;
}

.budget-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.budget-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

.budget-slider {
  width: 100%;
  accent-color: #2563eb;
  cursor: pointer;
}

.budget-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
}

.place-order-btn {
  padding: 0.5rem 1.25rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  background: #cbd5e1;
  color: #64748b;
  cursor: not-allowed;
}

.notice {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.success-notice {
  background: #d1fae5;
  border: 1px solid #a7f3d0;
  color: #065f46;
}

.success-notice a {
  margin-left: 0.5rem;
  color: #1e40af;
  font-weight: 600;
}

.error-notice {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.938rem;
}

th.num,
td.num {
  text-align: right;
}
</style>

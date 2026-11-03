// Pure helpers for the Restocking view.
// All money math is done in integer cents to avoid floating point drift.

const TREND_RANK = { increasing: 0, stable: 1, decreasing: 2 }

const toCents = (usd) => Math.round(usd * 100)
const fromCents = (cents) => cents / 100

// Demand gap for a forecast; only positive gaps need restocking.
const getGap = (forecast) => forecast.forecasted_demand - forecast.current_demand

// A forecast is usable only if it has a positive, finite unit cost
// (guards against a backend that has not been updated with unit_cost yet).
const hasValidCost = (forecast) =>
  Number.isFinite(forecast.unit_cost) && forecast.unit_cost > 0

/**
 * Greedy restock recommendation within a budget.
 * Priority: trend (increasing first), then largest gap.
 * A partial fill does not stop the walk, so cheaper items later in the
 * list can still use the leftover budget.
 */
export function recommendRestock(forecasts, budget) {
  const budgetCents = Math.max(0, toCents(Number(budget) || 0))

  const candidates = (forecasts || [])
    .filter(hasValidCost)
    .map(f => ({ ...f, gap: getGap(f) }))
    .filter(f => f.gap > 0)
    .sort((a, b) => {
      const rankA = TREND_RANK[a.trend] ?? TREND_RANK.decreasing
      const rankB = TREND_RANK[b.trend] ?? TREND_RANK.decreasing
      if (rankA !== rankB) return rankA - rankB
      return b.gap - a.gap
    })

  let remainingCents = budgetCents
  const items = []

  for (const f of candidates) {
    const unitCents = toCents(f.unit_cost)
    if (unitCents <= 0) continue
    const quantity = Math.min(f.gap, Math.floor(remainingCents / unitCents))
    if (quantity <= 0) continue
    const lineCents = quantity * unitCents
    remainingCents -= lineCents
    items.push({ ...f, quantity, line_total: fromCents(lineCents) })
  }

  return {
    items,
    total: fromCents(budgetCents - remainingCents),
    remaining: fromCents(remainingCents)
  }
}

/**
 * Cost to cover every positive demand gap in full.
 * Budgets above this amount buy nothing extra.
 */
export function maxUsefulBudget(forecasts) {
  const cents = (forecasts || [])
    .filter(hasValidCost)
    .reduce((sum, f) => {
      const gap = getGap(f)
      return gap > 0 ? sum + gap * toCents(f.unit_cost) : sum
    }, 0)
  return fromCents(cents)
}

import './styles/tokens.css'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Inventory from './views/Inventory.vue'
import Orders from './views/Orders.vue'
import Demand from './views/Demand.vue'
import Restocking from './views/Restocking.vue'
import Spending from './views/Spending.vue'
import Reports from './views/Reports.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Dashboard,
      meta: { nav: { labelKey: 'nav.overview', icon: 'home', group: 'overview', order: 10 } }
    },
    {
      path: '/inventory',
      component: Inventory,
      meta: { nav: { labelKey: 'nav.inventory', icon: 'package', group: 'operations', order: 20 } }
    },
    {
      path: '/orders',
      component: Orders,
      meta: { nav: { labelKey: 'nav.orders', icon: 'shopping-cart', group: 'operations', order: 30 } }
    },
    {
      path: '/demand',
      component: Demand,
      meta: { nav: { labelKey: 'nav.demandForecast', icon: 'trending-up', group: 'operations', order: 40 } }
    },
    {
      path: '/restocking',
      component: Restocking,
      meta: { nav: { labelKey: 'nav.restocking', icon: 'refresh-cw', group: 'operations', order: 50 } }
    },
    {
      path: '/spending',
      component: Spending,
      meta: { nav: { labelKey: 'nav.finance', icon: 'bar-chart', group: 'finance', order: 60 } }
    },
    {
      path: '/reports',
      component: Reports,
      meta: { nav: { labelKey: 'nav.reports', icon: 'file-text', group: 'finance', order: 70 } }
    }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')

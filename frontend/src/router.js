import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path: '/mmu',
    name: 'MMUList',
    component: () => import('@/pages/mmu/MMUList.vue'),
  },
  {
    path: '/mmu/new',
    name: 'MMUFormNew',
    component: () => import('@/pages/mmu/MMUForm.vue'),
  },
  {
    path: '/mmu/:id',
    name: 'MMUFormEdit',
    component: () => import('@/pages/mmu/MMUForm.vue'),
  },
  {
    path: '/referrals',
    name: 'ReferralList',
    component: () => import('@/pages/ReferralList.vue'),
  },
  {
    path: '/village-health',
    name: 'VillageHealthList',
    component: () => import('@/pages/VillageHealthList.vue'),
  },
  {
    path: '/dashboards',
    name: 'Dashboards',
    component: () => import('@/pages/Dashboards.vue'),
  },
  {
    path: '/dashboards/:name',
    name: 'DashboardEmbed',
    component: () => import('@/pages/Dashboards.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/portal'),
  routes,
})

export default router

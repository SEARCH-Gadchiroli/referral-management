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
    meta: { app: 'mmu' },
  },
  {
    path: '/mmu/new',
    name: 'MMUFormNew',
    component: () => import('@/pages/mmu/MMUForm.vue'),
    meta: { app: 'mmu' },
  },
  {
    path: '/mmu/:id',
    name: 'MMUFormEdit',
    component: () => import('@/pages/mmu/MMUForm.vue'),
    meta: { app: 'mmu' },
  },
  {
    path: '/referrals',
    name: 'ReferralList',
    component: () => import('@/pages/ReferralList.vue'),
    meta: { app: 'referrals' },
  },
  {
    path: '/village-health',
    name: 'VillageHealthList',
    component: () => import('@/pages/VillageHealthList.vue'),
    meta: { app: 'tribal_health' },
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
  {
    path: '/census',
    name: 'CensusDashboard',
    component: () => import('@/pages/CensusDashboard.vue'),
    meta: { app: 'census' },
  },
]

let router = createRouter({
  history: createWebHistory('/portal'),
  routes,
})

let cachedUserProfile = null

async function getUserProfile() {
  if (cachedUserProfile) return cachedUserProfile
  try {
    const res = await fetch('/api/method/referral.api.get_current_user_profile')
    const json = await res.json()
    cachedUserProfile = json.message || {}
    return cachedUserProfile
  } catch (e) {
    return {}
  }
}

router.beforeEach(async (to, from, next) => {
  if (!to.meta || !to.meta.app) {
    return next()
  }

  const profile = await getUserProfile()
  if (profile.is_system_manager) {
    return next()
  }

  if (to.meta.app === 'mmu' && !profile.can_access_mmu) {
    if (profile.can_access_referrals) return next('/referrals')
    if (profile.can_access_tribal_health) return next('/village-health')
    return next('/')
  }

  if (to.meta.app === 'referrals' && !profile.can_access_referrals) {
    if (profile.can_access_mmu) return next('/mmu')
    if (profile.can_access_tribal_health) return next('/village-health')
    return next('/')
  }

  if (to.meta.app === 'tribal_health' && !profile.can_access_tribal_health) {
    if (profile.can_access_referrals) return next('/referrals')
    if (profile.can_access_mmu) return next('/mmu')
    return next('/')
  }

  if (to.meta.app === 'census' && !profile.can_view_census) {
    return next('/')
  }

  next()
})

export default router


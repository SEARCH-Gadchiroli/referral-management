<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      <!-- Permission Checking State -->
      <div v-if="isCheckingPermission" class="py-24 flex flex-col items-center justify-center">
        <div class="w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-sm font-medium text-slate-500">Verifying role permissions...</p>
      </div>

      <!-- Access Denied State (For Non-System Managers) -->
      <div
        v-else-if="!isSystemManager"
        class="bg-white dark:bg-slate-900 rounded-3xl p-10 border border-slate-200 dark:border-slate-800 shadow-sm max-w-xl mx-auto text-center space-y-4 my-12"
      >
        <div class="w-14 h-14 rounded-2xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center justify-center mx-auto">
          <FeatherIcon name="shield-off" class="w-7 h-7" />
        </div>
        <h2 class="text-xl font-bold text-slate-900 dark:text-slate-100">Access Restricted</h2>
        <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
          Census infographics and household registry data are confidential and restricted strictly to users with the <strong>System Manager</strong> role.
        </p>
        <div class="pt-4">
          <router-link
            to="/"
            class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200 font-semibold text-sm transition"
          >
            <FeatherIcon name="home" class="w-4 h-4" />
            <span>Return to Home</span>
          </router-link>
        </div>
      </div>

      <!-- Authorized Dashboard Content -->
      <template v-else>
        <!-- Dashboard Top Header & Banner (Crisp, High-Contrast Solid Design) -->
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 text-white shadow-lg">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div class="space-y-2.5">
              <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-950 border border-teal-800 text-teal-300 text-xs font-semibold">
                <FeatherIcon name="database" class="w-3.5 h-3.5" />
                <span>Dhanora Taluka 232 Tribal Villages Registry</span>
              </div>
              <h1 class="text-2xl sm:text-3xl font-black tracking-tight text-white">Census Infographics & Household Explorer</h1>
              <p class="text-sm text-slate-300 max-w-2xl leading-relaxed">
                Comprehensive demographic, housing, education, health schemes, and socio-economic analytics across 232 tribal villages.
              </p>
            </div>

            <!-- Solid, High-Contrast Stat Counters -->
            <div class="flex items-center gap-4 self-start lg:self-auto bg-slate-800/90 border border-slate-700/80 px-6 py-4 rounded-2xl shadow-inner">
              <div class="text-center px-3">
                <div class="text-2xl sm:text-3xl font-black text-teal-400">{{ totalVillagesCount }}</div>
                <div class="text-[11px] uppercase tracking-wider font-bold text-slate-400 mt-0.5">Villages</div>
              </div>
              <div class="w-px h-10 bg-slate-700"></div>
              <div class="text-center px-3">
                <div class="text-2xl sm:text-3xl font-black text-indigo-400">{{ totalHouseholdsCount }}</div>
                <div class="text-[11px] uppercase tracking-wider font-bold text-slate-400 mt-0.5">Households</div>
              </div>
              <div class="w-px h-10 bg-slate-700"></div>
              <div class="text-center px-3">
                <div class="text-2xl sm:text-3xl font-black text-amber-400">{{ totalPopulationCount }}</div>
                <div class="text-[11px] uppercase tracking-wider font-bold text-slate-400 mt-0.5">Population</div>
              </div>
            </div>
          </div>

          <!-- Mode Toggle Tabs -->
          <div class="mt-8 flex items-center gap-3 border-t border-slate-800 pt-5">
            <button
              @click="activeTab = 'infographics'"
              :class="[
                activeTab === 'infographics'
                  ? 'bg-teal-600 text-white font-bold shadow-sm'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white font-semibold',
                'px-4 py-2.5 rounded-xl text-xs sm:text-sm flex items-center gap-2 transition duration-150 cursor-pointer'
              ]"
            >
              <FeatherIcon name="pie-chart" class="w-4 h-4" />
              <span>Village Infographics (Macro)</span>
            </button>

            <button
              @click="activeTab = 'explorer'"
              :class="[
                activeTab === 'explorer'
                  ? 'bg-teal-600 text-white font-bold shadow-sm'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white font-semibold',
                'px-4 py-2.5 rounded-xl text-xs sm:text-sm flex items-center gap-2 transition duration-150 cursor-pointer'
              ]"
            >
              <FeatherIcon name="search" class="w-4 h-4" />
              <span>Household Explorer (Micro)</span>
            </button>
          </div>
        </div>

        <!-- Tab View 1: Village Infographics -->
        <VillageInfographics
          v-if="activeTab === 'infographics'"
          :selected-village="selectedVillage"
          :villages="villagesList"
          :analytics="analyticsData"
          :loading="loadingAnalytics"
          @update:selected-village="handleVillageChange"
          @refresh="fetchAnalytics"
        />

        <!-- Tab View 2: Household Explorer -->
        <HouseholdExplorer
          v-else-if="activeTab === 'explorer'"
          :selected-village="selectedVillage"
          :villages="villagesList"
          @update:selected-village="handleVillageChange"
        />
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import VillageInfographics from '@/components/census/VillageInfographics.vue'
import HouseholdExplorer from '@/components/census/HouseholdExplorer.vue'

const isCheckingPermission = ref(true)
const isSystemManager = ref(false)

const activeTab = ref('infographics')
const selectedVillage = ref('ALL')
const villagesList = ref([])
const totalVillagesCount = ref(0)
const totalHouseholdsCount = ref(0)
const totalPopulationCount = ref(0)

const analyticsData = ref(null)
const loadingAnalytics = ref(false)

const checkPermission = async () => {
  try {
    const res = await fetch('/api/method/referral.api.get_current_user_profile')
    const json = await res.json()
    const data = json.message || {}
    isSystemManager.value = Boolean(data.is_system_manager)
  } catch (err) {
    console.error('Error checking user permissions:', err)
    isSystemManager.value = false
  } finally {
    isCheckingPermission.value = false
  }
}

const fetchVillages = async () => {
  try {
    const res = await fetch('/api/method/referral.api.get_census_villages')
    const json = await res.json()
    const data = json.message || {}

    if (data.success) {
      villagesList.value = data.villages || []
      totalVillagesCount.value = data.total_villages || 0
      totalHouseholdsCount.value = data.total_households || 0
      totalPopulationCount.value = data.total_population || 0
    }
  } catch (err) {
    console.error('Error fetching census villages:', err)
  }
}

const fetchAnalytics = async () => {
  loadingAnalytics.value = true
  try {
    const param = encodeURIComponent(selectedVillage.value || 'ALL')
    const res = await fetch(`/api/method/referral.api.get_village_census_analytics?village=${param}`)
    const json = await res.json()
    const data = json.message || {}

    if (data.success) {
      analyticsData.value = data
    }
  } catch (err) {
    console.error('Error fetching village analytics:', err)
  } finally {
    loadingAnalytics.value = false
  }
}

const handleVillageChange = (newVillage) => {
  selectedVillage.value = newVillage
  fetchAnalytics()
}

onMounted(async () => {
  await checkPermission()
  if (isSystemManager.value) {
    await fetchVillages()
    await fetchAnalytics()
  }
})
</script>

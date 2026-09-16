<template>
  <div class="space-y-6">
    <!-- Top Filter Bar: Cascading Village & Smart Search -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
      <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <!-- Village Filter -->
        <div class="flex items-center gap-3">
          <label class="text-xs font-bold uppercase tracking-wider text-slate-500 whitespace-nowrap">Village:</label>
          <select
            v-model="localVillage"
            @change="handleVillageChange"
            class="bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-teal-500 min-w-[220px]"
          >
            <option value="ALL">🌐 All Villages</option>
            <option v-for="v in villages" :key="v.village_name" :value="v.village_name">
              {{ v.village_name }} ({{ v.total_households }} HH)
            </option>
          </select>
        </div>

        <!-- Smart Search Input -->
        <div class="relative flex-1 max-w-md">
          <FeatherIcon name="search" class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            @input="debounceSearch"
            type="text"
            placeholder="Search by House No, Family Head, Member, or Phone..."
            class="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-sm font-medium text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
          <button
            v-if="searchQuery"
            @click="clearSearch"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
          >
            <FeatherIcon name="x" class="w-4 h-4" />
          </button>
        </div>

        <!-- House No Direct Jump -->
        <div class="flex items-center gap-2">
          <input
            v-model="houseNumberFilter"
            @change="fetchHouseholds(1)"
            type="number"
            placeholder="House #"
            class="w-24 bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
          <button
            @click="fetchHouseholds(1)"
            class="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs transition"
          >
            Filter
          </button>
        </div>
      </div>

      <!-- Results Count Bar -->
      <div class="flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 dark:border-slate-800 pt-3">
        <span>Found <strong>{{ totalRecords }}</strong> households in directory</span>
        <span v-if="totalPages > 1">Page <strong>{{ currentPage }}</strong> of <strong>{{ totalPages }}</strong></span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-16 flex flex-col items-center justify-center">
      <div class="w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-4 text-sm font-medium text-slate-600 dark:text-slate-400">Loading household registry...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!households.length" class="bg-white dark:bg-slate-900 rounded-2xl p-12 text-center border border-slate-200 dark:border-slate-800">
      <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
        <FeatherIcon name="home" class="w-6 h-6" />
      </div>
      <h4 class="font-bold text-slate-800 dark:text-slate-200 text-sm">No households found</h4>
      <p class="text-xs text-slate-500 mt-1">Try clearing your search query or selecting a different village.</p>
    </div>

    <!-- Household Cards Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="hh in households"
        :key="hh.household_id"
        @click="openDossier(hh.household_id)"
        class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 shadow-xs hover:shadow-md hover:border-teal-500/50 dark:hover:border-teal-500/50 transition cursor-pointer flex flex-col justify-between group"
      >
        <div class="space-y-2.5">
          <!-- Card Header: ID & Village -->
          <div class="flex items-center justify-between gap-2">
            <span class="text-xs font-mono font-bold text-teal-600 dark:text-teal-400 truncate">{{ hh.household_id }}</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 truncate">
              {{ hh.village }}
            </span>
          </div>

          <!-- Family Head & Numbers -->
          <div>
            <h4 class="font-bold text-sm text-slate-900 dark:text-slate-100 group-hover:text-teal-600 transition truncate">
              {{ hh.head_of_household || 'Head Unspecified' }}
            </h4>
            <div class="text-[11px] text-slate-500 mt-0.5">
              House #<strong>{{ hh.house_number }}</strong> | Family #<strong>{{ hh.family_number }}</strong>
            </div>
          </div>

          <!-- Key Badges -->
          <div class="flex flex-wrap gap-1.5 text-[11px]">
            <span class="px-2 py-0.5 rounded-md bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 font-semibold">
              {{ hh.total_family_members }} Members
            </span>
            <span v-if="hh.caste_of_head" class="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
              {{ hh.caste_of_head }}
            </span>
            <span v-if="hh.total_land_acres > 0" class="px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
              {{ hh.total_land_acres.toFixed(1) }} ac
            </span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
          <span class="flex items-center gap-1">
            <FeatherIcon name="phone" class="w-3.5 h-3.5" />
            <span>{{ hh.mobile_number || '—' }}</span>
          </span>
          <span class="text-teal-600 dark:text-teal-400 font-bold group-hover:translate-x-0.5 transition flex items-center gap-0.5 text-[11px]">
            <span>Dossier</span>
            <FeatherIcon name="chevron-right" class="w-3.5 h-3.5" />
          </span>
        </div>
      </div>
    </div>

    <!-- Pagination Footer -->
    <div v-if="totalPages > 1" class="flex items-center justify-between bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200 dark:border-slate-800">
      <button
        @click="fetchHouseholds(currentPage - 1)"
        :disabled="currentPage <= 1 || loading"
        class="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-1.5"
      >
        <FeatherIcon name="chevron-left" class="w-4 h-4" />
        <span>Previous</span>
      </button>

      <span class="text-xs font-semibold text-slate-600 dark:text-slate-400">
        Page {{ currentPage }} of {{ totalPages }}
      </span>

      <button
        @click="fetchHouseholds(currentPage + 1)"
        :disabled="currentPage >= totalPages || loading"
        class="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-1.5"
      >
        <span>Next</span>
        <FeatherIcon name="chevron-right" class="w-4 h-4" />
      </button>
    </div>

    <!-- Dossier Modal Component -->
    <HouseholdDossierModal
      :is-open="isModalOpen"
      :household="selectedHouseholdDoc"
      :loading="loadingDossier"
      @close="isModalOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import HouseholdDossierModal from './HouseholdDossierModal.vue'

const props = defineProps({
  selectedVillage: { type: String, default: 'ALL' },
  villages: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:selectedVillage'])

const localVillage = ref(props.selectedVillage)
const searchQuery = ref('')
const houseNumberFilter = ref('')
const households = ref([])
const totalRecords = ref(0)
const totalPages = ref(1)
const currentPage = ref(1)
const loading = ref(false)

// Modal state
const isModalOpen = ref(false)
const selectedHouseholdDoc = ref(null)
const loadingDossier = ref(false)

let debounceTimer = null

watch(() => props.selectedVillage, (newVal) => {
  localVillage.value = newVal
  fetchHouseholds(1)
})

const handleVillageChange = () => {
  emit('update:selectedVillage', localVillage.value)
  fetchHouseholds(1)
}

const debounceSearch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchHouseholds(1)
  }, 350)
}

const clearSearch = () => {
  searchQuery.value = ''
  fetchHouseholds(1)
}

const fetchHouseholds = async (page = 1) => {
  loading.value = true
  currentPage.value = page

  try {
    const params = new URLSearchParams({
      village: localVillage.value || 'ALL',
      house_number: houseNumberFilter.value || '',
      query: searchQuery.value || '',
      page: page,
      page_size: 24
    })

    const res = await fetch(`/api/method/referral.api.search_census_households?${params.toString()}`)
    const json = await res.json()
    const data = json.message || {}

    if (data.success) {
      households.value = data.households || []
      totalRecords.value = data.total_records || 0
      totalPages.value = data.total_pages || 1
    }
  } catch (err) {
    console.error('Error fetching households:', err)
  } finally {
    loading.value = false
  }
}

const openDossier = async (householdId) => {
  isModalOpen.value = true
  loadingDossier.value = true
  selectedHouseholdDoc.value = null

  try {
    const res = await fetch(`/api/method/referral.api.get_household_dossier?household_id=${encodeURIComponent(householdId)}`)
    const json = await res.json()
    const data = json.message || {}

    if (data.success) {
      selectedHouseholdDoc.value = data.household
    }
  } catch (err) {
    console.error('Error loading dossier:', err)
  } finally {
    loadingDossier.value = false
  }
}

onMounted(() => {
  fetchHouseholds(1)
})
</script>

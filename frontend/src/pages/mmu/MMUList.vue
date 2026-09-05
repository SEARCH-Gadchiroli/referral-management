<template>
  <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
    
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">Mobile Medical Unit Visits</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Track and review patient encounters recorded during field MMU rounds.</p>
      </div>
      <div class="mt-4 sm:mt-0 flex flex-wrap items-center gap-2">
        
        <!-- Refresh Button -->
        <button
          @click="loadRecords"
          type="button"
          :disabled="loading"
          class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-3.5 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 rounded-xl transition-colors cursor-pointer"
        >
          <FeatherIcon name="refresh-cw" class="w-4 h-4 shrink-0" :class="{ 'animate-spin': loading }" />
          <span>Refresh</span>
        </button>

        <!-- New Visit Record Button -->
        <router-link
          to="/mmu/new"
          class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-4 py-2 text-sm font-semibold text-white bg-rose-600 hover:bg-rose-700 active:bg-rose-800 rounded-xl shadow-xs transition-colors cursor-pointer"
        >
          <FeatherIcon name="plus" class="w-4 h-4 shrink-0" />
          <span>New Visit Record</span>
        </router-link>

      </div>
    </div>

    <!-- Filters Bar -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3.5">
        
        <!-- Search -->
        <div class="relative flex items-center">
          <input
            type="text"
            v-model="filters.search"
            @input="debouncedSearch"
            placeholder="Search patient, ID, visit #..."
            class="w-full pl-9 pr-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          />
          <FeatherIcon name="search" class="w-4 h-4 text-slate-400 absolute left-3" />
        </div>

        <!-- Area Filter -->
        <div>
          <select
            v-model="filters.area_name"
            @change="onAreaFilterChange"
            class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          >
            <option value="">All Areas</option>
            <option v-for="a in masterData.areas || []" :key="a.code" :value="a.name">
              {{ a.name }}
            </option>
          </select>
        </div>

        <!-- Village Filter -->
        <div>
          <select
            v-model="filters.village_name"
            @change="loadRecords"
            class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          >
            <option value="">All Villages</option>
            <option v-for="v in filteredVillages" :key="v.code" :value="v.name">
              {{ v.name }}
            </option>
          </select>
        </div>

        <!-- Patient Sex Filter -->
        <div>
          <select
            v-model="filters.patient_sex"
            @change="loadRecords"
            class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          >
            <option value="">All Genders</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>

      </div>

      <!-- Secondary filter line -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 text-sm">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 text-slate-600 dark:text-slate-400 font-medium">
            <span>From:</span>
            <input
              type="date"
              v-model="filters.start_date"
              @change="loadRecords"
              class="px-2.5 py-1.5 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>
          <div class="flex items-center gap-2 text-slate-600 dark:text-slate-400 font-medium">
            <span>To:</span>
            <input
              type="date"
              v-model="filters.end_date"
              @change="loadRecords"
              class="px-2.5 py-1.5 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>
        </div>

        <div class="flex items-center gap-3">
          <span class="text-xs text-slate-400 font-medium">Total: {{ records.length }} records</span>
          <button
            v-if="hasActiveFilters"
            @click="clearFilters"
            class="text-sm text-rose-600 dark:text-rose-400 hover:underline font-semibold cursor-pointer"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
      
      <div v-if="loading" class="p-16 text-center text-slate-500 dark:text-slate-400">
        <div class="w-9 h-9 border-3 border-rose-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <span class="text-sm font-medium">Loading patient visit records...</span>
      </div>

      <div v-else-if="records.length === 0" class="p-16 text-center text-slate-500 dark:text-slate-400 space-y-2">
        <FeatherIcon name="inbox" class="w-10 h-10 text-slate-300 dark:text-slate-600 mx-auto" />
        <h3 class="text-base font-bold text-slate-800 dark:text-slate-200">No Patient Visits Found</h3>
        <p class="text-sm text-slate-400">Try adjusting your search criteria or register a new visit record.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200/80 dark:divide-slate-800 text-left text-sm">
          <thead class="bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider text-xs">
            <tr>
              <th class="px-4 py-3.5">Visit Details</th>
              <th class="px-4 py-3.5">Patient Details</th>
              <th class="px-4 py-3.5">Location</th>
              <th class="px-4 py-3.5">Diagnoses</th>
              <th class="px-4 py-3.5">Census Linkage</th>
              <th class="px-4 py-3.5">Referral Status</th>
              <th class="px-4 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800/80 text-slate-800 dark:text-slate-200">
            <tr
              v-for="rec in records"
              :key="rec.name"
              class="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors"
            >
              <td class="px-4 py-3.5 whitespace-nowrap">
                <div class="font-bold text-slate-900 dark:text-slate-100">{{ rec.name }}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1 mt-0.5">
                  <FeatherIcon name="calendar" class="w-3.5 h-3.5 shrink-0" />
                  <span>{{ rec.date_of_visit }}</span>
                </div>
              </td>

              <td class="px-4 py-3.5 whitespace-nowrap">
                <div class="font-bold text-slate-900 dark:text-slate-100">{{ rec.patient_name }}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  <span class="font-semibold text-rose-600 dark:text-rose-400">{{ rec.patient_unique_id }}</span> • {{ rec.patient_sex }} • {{ rec.total_age || 0 }} yrs
                </div>
              </td>

              <td class="px-4 py-3.5 whitespace-nowrap">
                <div class="text-slate-900 dark:text-slate-100 font-medium">{{ rec.village_name || '-' }}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400">{{ rec.area_name || '-' }}</div>
              </td>

              <td class="px-4 py-3.5 max-w-xs">
                <div class="truncate text-slate-800 dark:text-slate-200 font-medium">
                  {{ [rec.diagnosis_1, rec.diagnosis_2, rec.diagnosis_3, rec.diagnosis_4, rec.diagnosis_5, rec.diagnosis_6, rec.dental_diagnosis, rec.dental_diagnosis_2].filter(Boolean).join(', ') || '-' }}
                </div>
              </td>

              <td class="px-4 py-3.5 whitespace-nowrap">
                <span
                  v-if="rec.match_status === 'Auto-Matched' || rec.match_status === 'Manually Verified'"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
                  :title="rec.matched_member_name ? `${rec.matched_member_name} (${rec.census_match})` : ''"
                >
                  <FeatherIcon name="check" class="w-3 h-3" />
                  {{ rec.match_status }}
                </span>
                <span
                  v-else-if="rec.match_status === 'Multiple Matches'"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800"
                >
                  <FeatherIcon name="alert-circle" class="w-3 h-3" />
                  Multiple
                </span>
                <span v-else class="text-slate-400 text-xs font-medium">Unmatched</span>
              </td>

              <td class="px-4 py-3.5 whitespace-nowrap">
                <span
                  v-if="rec.patient_referred && rec.patient_referred !== 'No' && rec.patient_referred !== 'Not Applicable'"
                  class="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border border-rose-100 dark:border-rose-900/50"
                >
                  {{ rec.patient_referred }}
                </span>
                <span v-else class="text-slate-400 text-xs">None</span>
              </td>

              <td class="px-4 py-3.5 whitespace-nowrap text-right">
                <router-link
                  :to="'/mmu/' + encodeURIComponent(rec.name)"
                  class="inline-flex items-center flex-row gap-1.5 whitespace-nowrap px-3 py-1.5 text-xs font-bold text-rose-600 dark:text-rose-400 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl transition-colors"
                >
                  <FeatherIcon name="edit-2" class="w-3.5 h-3.5 shrink-0" />
                  <span>Edit</span>
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'MMUList',
  components: {
    FeatherIcon,
  },
  data() {
    return {
      loading: false,
      records: [],
      masterData: {
        areas: [],
        villages: {},
      },
      filters: {
        search: '',
        area_name: '',
        village_name: '',
        patient_sex: '',
        start_date: '',
        end_date: '',
      },
      searchTimeout: null,
    }
  },
  computed: {
    hasActiveFilters() {
      return (
        this.filters.search ||
        this.filters.area_name ||
        this.filters.village_name ||
        this.filters.patient_sex ||
        this.filters.start_date ||
        this.filters.end_date
      )
    },
    filteredVillages() {
      if (!this.filters.area_name || !this.masterData.villages) {
        let all = []
        Object.values(this.masterData.villages || {}).forEach(arr => {
          all = all.concat(arr)
        })
        return all
      }
      const area = (this.masterData.areas || []).find(a => a.name === this.filters.area_name)
      if (!area) return []
      return this.masterData.villages[String(area.code)] || []
    },
  },
  created() {
    this.fetchMasterData()
    this.loadRecords()
  },
  methods: {
    async fetchMasterData() {
      try {
        const res = await fetch('/api/method/mmu.mmu.page.mmu_patient_record.mmu_patient_record.get_master_data')
        const data = await res.json()
        if (data.message) {
          this.masterData = data.message
        }
      } catch (e) {
        console.error('Failed to load MMU master data', e)
      }
    },
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.loadRecords()
      }, 300)
    },
    onAreaFilterChange() {
      this.filters.village_name = ''
      this.loadRecords()
    },
    clearFilters() {
      this.filters = {
        search: '',
        area_name: '',
        village_name: '',
        patient_sex: '',
        start_date: '',
        end_date: '',
      }
      this.loadRecords()
    },
    async loadRecords() {
      this.loading = true
      try {
        const params = new URLSearchParams({
          search: this.filters.search || '',
          area_name: this.filters.area_name || '',
          village_name: this.filters.village_name || '',
          patient_sex: this.filters.patient_sex || '',
          start_date: this.filters.start_date || '',
          end_date: this.filters.end_date || '',
          page: '1',
          page_size: '100',
        })

        const res = await fetch(`/api/method/mmu.mmu.page.mmu_patient_record.mmu_patient_record.get_portal_mmu_records?${params.toString()}`)
        const data = await res.json()
        if (data.message && data.message.records) {
          this.records = data.message.records
        } else {
          this.records = []
        }
      } catch (e) {
        console.error('Failed to load MMU records', e)
        this.records = []
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

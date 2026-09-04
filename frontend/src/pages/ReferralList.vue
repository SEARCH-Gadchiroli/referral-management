<template>
  <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
    
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">Patient Referrals</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Monitor secondary hospital referrals and track patient arrival status.</p>
      </div>
      <div class="mt-4 sm:mt-0 flex flex-wrap items-center gap-2">
        
        <!-- Export Excel Button -->
        <button
          @click="exportReport('excel')"
          class="inline-flex items-center gap-1.5 px-3.5 py-2 text-sm font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 border border-emerald-200 dark:border-emerald-800 rounded-xl transition-colors cursor-pointer"
          title="Export referrals list to Excel sheet"
        >
          <FeatherIcon name="file-text" class="w-4 h-4 text-emerald-600" />
          <span>Export Excel</span>
        </button>

        <!-- Export PDF Button -->
        <button
          @click="exportReport('pdf')"
          class="inline-flex items-center gap-1.5 px-3.5 py-2 text-sm font-semibold text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-900/60 border border-rose-200 dark:border-rose-800 rounded-xl transition-colors cursor-pointer"
          title="Export referrals report as printable PDF"
        >
          <FeatherIcon name="printer" class="w-4 h-4 text-rose-600" />
          <span>Export PDF</span>
        </button>

        <!-- Refresh Button -->
        <Button
          @click="loadReferrals"
          variant="subtle"
          class="text-sm text-slate-600 dark:text-slate-300"
          :loading="loading"
        >
          <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-1.5" />
          Refresh
        </Button>
      </div>
    </div>

    <!-- Top Search & Filter Bar -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 sm:p-5 border border-slate-200/80 dark:border-slate-800 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      
      <!-- Search Input -->
      <div class="relative flex-1 max-w-lg">
        <input
          type="text"
          v-model="filters.search"
          @input="debouncedSearch"
          placeholder="Search patient name, phone, ref number, or referrer..."
          class="w-full pl-9 pr-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
        />
        <FeatherIcon name="search" class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
      </div>

      <!-- Filter Controls & Counter -->
      <div class="flex items-center gap-3">
        <button
          @click="filterDrawerOpen = true"
          class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border font-semibold text-sm transition-all cursor-pointer"
          :class="activeFilterCount > 0
            ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800 shadow-xs'
            : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:bg-slate-50'"
        >
          <FeatherIcon name="sliders" class="w-4 h-4" />
          <span>Filters</span>
          <span
            v-if="activeFilterCount > 0"
            class="px-2 py-0.5 rounded-full text-xs font-extrabold bg-blue-600 text-white"
          >
            {{ activeFilterCount }}
          </span>
        </button>

        <span class="text-xs text-slate-400 font-medium whitespace-nowrap">
          {{ totalRecords }} records
        </span>

        <button
          v-if="hasActiveFilters"
          @click="resetAllFilters"
          class="text-sm text-blue-600 dark:text-blue-400 hover:underline font-semibold whitespace-nowrap cursor-pointer"
        >
          Reset All
        </button>
      </div>
    </div>

    <!-- Referrals Table: Exactly 10 Columns -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
      
      <div v-if="loading" class="p-16 text-center text-slate-500 dark:text-slate-400">
        <div class="w-9 h-9 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <span class="text-sm font-medium">Loading patient referrals...</span>
      </div>

      <div v-else-if="referrals.length === 0" class="p-16 text-center text-slate-500 dark:text-slate-400 space-y-2">
        <FeatherIcon name="inbox" class="w-10 h-10 text-slate-300 dark:text-slate-600 mx-auto" />
        <h3 class="text-base font-bold text-slate-800 dark:text-slate-200">No Patient Referrals Found</h3>
        <p class="text-sm text-slate-400">Try clearing filters or checking other search terms.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200/80 dark:divide-slate-800 text-left text-sm">
          <thead class="bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider text-xs">
            <tr>
              <th class="px-4 py-3.5">Ref Number</th>
              <th class="px-4 py-3.5">Status</th>
              <th class="px-4 py-3.5">Point of Referral</th>
              <th class="px-4 py-3.5">Referrer Name</th>
              <th class="px-4 py-3.5">Patient Name</th>
              <th class="px-4 py-3.5">Age</th>
              <th class="px-4 py-3.5">Gender</th>
              <th class="px-4 py-3.5">Village</th>
              <th class="px-4 py-3.5">OPD Department</th>
              <th class="px-4 py-3.5">Referral Date</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800/80 text-slate-800 dark:text-slate-200">
            <tr
              v-for="ref in referrals"
              :key="ref.name"
              @click="openModal(ref)"
              class="hover:bg-blue-50/40 dark:hover:bg-blue-950/20 transition-colors cursor-pointer"
            >
              <!-- 1. Ref Number -->
              <td class="px-4 py-3.5 whitespace-nowrap">
                <span class="font-bold text-indigo-600 dark:text-indigo-400 hover:underline">
                  {{ ref.reference_number || ref.name }}
                </span>
              </td>

              <!-- 2. Status -->
              <td class="px-4 py-3.5 whitespace-nowrap">
                <span
                  class="px-2.5 py-1 rounded-full text-xs font-bold"
                  :class="statusBadgeClass(ref.status)"
                >
                  {{ ref.status || 'Pending' }}
                </span>
              </td>

              <!-- 3. Point of Referral -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300">
                {{ ref.referred_by_who || '-' }}
              </td>

              <!-- 4. Referrer Name -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300">
                {{ ref.referrer_name || '-' }}
              </td>

              <!-- 5. Patient Name -->
              <td class="px-4 py-3.5 whitespace-nowrap font-semibold text-slate-900 dark:text-slate-100">
                {{ ref.patient_name }}
              </td>

              <!-- 6. Age -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-600 dark:text-slate-400">
                {{ ref.patient_age ? ref.patient_age + ' yrs' : '-' }}
              </td>

              <!-- 7. Gender -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-600 dark:text-slate-400">
                {{ ref.patient_gender || '-' }}
              </td>

              <!-- 8. Village -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300 font-medium">
                {{ ref.patient_village || '-' }}
              </td>

              <!-- 9. OPD Department -->
              <td class="px-4 py-3.5 whitespace-nowrap font-medium text-blue-700 dark:text-blue-400">
                {{ ref.opd_departments || '-' }}
              </td>

              <!-- 10. Referral Date -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-600 dark:text-slate-400">
                {{ ref.referral_date || '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

    <!-- Comprehensive Filter Drawer Component -->
    <ReferralFilterDrawer
      :is-open="filterDrawerOpen"
      :filters="filters"
      :options="filterOptions"
      @close="filterDrawerOpen = false"
      @apply="onApplyFilters"
      @reset="resetAllFilters"
    />

    <!-- Referral Detail Modal Component -->
    <ReferralDetailModal
      :is-open="modalOpen"
      :referral="selectedReferral"
      @close="modalOpen = false"
      @updated="loadReferrals"
    />

  </div>
</template>

<script>
import { FeatherIcon, Button } from 'frappe-ui'
import ReferralFilterDrawer from '@/components/ReferralFilterDrawer.vue'
import ReferralDetailModal from '@/components/ReferralDetailModal.vue'

export default {
  name: 'ReferralList',
  components: {
    FeatherIcon,
    Button,
    ReferralFilterDrawer,
    ReferralDetailModal,
  },
  data() {
    return {
      loading: false,
      referrals: [],
      totalRecords: 0,
      selectedReferral: null,
      modalOpen: false,
      filterDrawerOpen: false,
      filterOptions: {},
      filters: {
        search: '',
        status: [],
        gender: [],
        min_age: '',
        max_age: '',
        village: [],
        taluka: [],
        tribal_classification: [],
        phc: [],
        service_facility_type: [],
        opd_category: [],
        opd_department: [],
        facility_visited: [],
        referred_by_who: [],
        referrer_name: [],
        referrer_department: [],
        referring_doctor: [],
        start_date: '',
        end_date: '',
      },
      searchTimeout: null,
    }
  },
  computed: {
    activeFilterCount() {
      const keys = [
        'status', 'gender', 'min_age', 'max_age', 'village', 'taluka',
        'tribal_classification', 'phc', 'service_facility_type', 'opd_category',
        'opd_department', 'facility_visited', 'referred_by_who', 'referrer_name',
        'referrer_department', 'referring_doctor', 'start_date', 'end_date'
      ]
      return keys.filter(k => {
        const val = this.filters[k]
        if (Array.isArray(val)) return val.length > 0
        return Boolean(val)
      }).length
    },
    hasActiveFilters() {
      return Boolean(this.filters.search) || this.activeFilterCount > 0
    },
  },
  created() {
    this.fetchFilterOptions()
    this.loadReferrals()
  },
  methods: {
    statusBadgeClass(status) {
      if (status === 'Visited') return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
      if (status === 'Follow-up In Progress') return 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
      if (status === 'Closed - Not Visited' || status === 'No-Show' || status === 'Cancelled') return 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'
      return 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300'
    },
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.loadReferrals()
      }, 300)
    },
    async fetchFilterOptions() {
      try {
        const res = await fetch('/api/method/referral.api.get_portal_referral_filter_options')
        const data = await res.json()
        if (data.message) {
          this.filterOptions = data.message
        }
      } catch (e) {
        console.warn('Failed to load filter options', e)
      }
    },
    onApplyFilters(newFilters) {
      this.filters = { ...newFilters }
      this.loadReferrals()
    },
    resetAllFilters() {
      this.filters = {
        search: '',
        status: [],
        gender: [],
        min_age: '',
        max_age: '',
        village: [],
        taluka: [],
        tribal_classification: [],
        phc: [],
        service_facility_type: [],
        opd_category: [],
        opd_department: [],
        facility_visited: [],
        referred_by_who: [],
        referrer_name: [],
        referrer_department: [],
        referring_doctor: [],
        start_date: '',
        end_date: '',
      }
      this.loadReferrals()
    },
    openModal(ref) {
      this.selectedReferral = ref
      this.modalOpen = true
    },
    buildFilterParams() {
      const params = new URLSearchParams()
      for (const [k, v] of Object.entries(this.filters)) {
        if (Array.isArray(v)) {
          if (v.length > 0) {
            params.set(k, v.join(','))
          }
        } else if (v !== '' && v !== null && v !== undefined) {
          params.set(k, v)
        }
      }
      return params
    },
    exportReport(format) {
      const params = this.buildFilterParams()
      let endpoint = '/api/method/referral.api.export_referrals_excel'
      if (format === 'pdf') {
        endpoint = '/api/method/referral.api.export_referrals_pdf'
      }
      window.location.href = `${endpoint}?${params.toString()}`
    },
    async loadReferrals() {
      this.loading = true
      try {
        const params = this.buildFilterParams()
        params.set('page_size', '50')

        const res = await fetch(`/api/method/referral.api.get_portal_referrals?${params.toString()}`)
        const data = await res.json()
        if (data.message && data.message.records) {
          this.referrals = data.message.records
          this.totalRecords = data.message.total_records || this.referrals.length
        } else {
          this.referrals = []
          this.totalRecords = 0
        }
      } catch (e) {
        console.error('Failed to load referrals', e)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

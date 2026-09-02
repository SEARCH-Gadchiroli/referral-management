<template>
  <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
    
    <!-- Header -->
    <div class="sm:flex sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">Village Health Education</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Record and review community health awareness sessions conducted in villages.</p>
      </div>
      <div class="mt-4 sm:mt-0 flex flex-wrap items-center gap-2">
        
        <!-- Refresh Button -->
        <button
          @click="loadSessions"
          type="button"
          :disabled="loading"
          class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-3.5 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 rounded-xl transition-colors cursor-pointer"
        >
          <FeatherIcon name="refresh-cw" class="w-4 h-4 shrink-0" :class="{ 'animate-spin': loading }" />
          <span>Refresh</span>
        </button>

        <!-- Log Session Button -->
        <button
          @click="createModalOpen = true"
          type="button"
          class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-4 py-2 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 rounded-xl shadow-xs transition-colors cursor-pointer"
        >
          <FeatherIcon name="plus" class="w-4 h-4 shrink-0" />
          <span>Log Session</span>
        </button>

      </div>
    </div>

    <!-- Filters Bar -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        
        <!-- Search -->
        <div class="relative flex items-center">
          <input
            type="text"
            v-model="filters.search"
            @input="debouncedSearch"
            placeholder="Search village, educator, ID..."
            class="w-full pl-9 pr-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          />
          <FeatherIcon name="search" class="w-4 h-4 text-slate-400 absolute left-3" />
        </div>

        <!-- Session Conducted Filter -->
        <div>
          <select
            v-model="filters.session_conducted"
            @change="loadSessions"
            class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          >
            <option value="">All Statuses</option>
            <option value="Yes">Conducted (Yes)</option>
            <option value="No">Not Conducted (No)</option>
          </select>
        </div>

        <!-- Date Range Filter -->
        <div class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 font-medium">
          <input
            type="date"
            v-model="filters.start_date"
            @change="loadSessions"
            class="w-full px-2.5 py-1.5 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          />
          <span>to</span>
          <input
            type="date"
            v-model="filters.end_date"
            @change="loadSessions"
            class="w-full px-2.5 py-1.5 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          />
        </div>

      </div>

      <div class="flex flex-wrap items-center justify-between gap-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 text-sm">
        <span class="text-xs text-slate-400 font-medium">Total: {{ totalRecords }} sessions</span>
        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="text-sm text-emerald-600 dark:text-emerald-400 hover:underline font-semibold cursor-pointer"
        >
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
      
      <div v-if="loading" class="p-16 text-center text-slate-500 dark:text-slate-400">
        <div class="w-9 h-9 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <span class="text-sm font-medium">Loading health education sessions...</span>
      </div>

      <div v-else-if="sessions.length === 0" class="p-16 text-center text-slate-500 dark:text-slate-400 space-y-2">
        <FeatherIcon name="inbox" class="w-10 h-10 text-slate-300 dark:text-slate-600 mx-auto" />
        <h3 class="text-base font-bold text-slate-800 dark:text-slate-200">No Sessions Found</h3>
        <p class="text-sm text-slate-400">Log a new session or adjust your search filters.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200/80 dark:divide-slate-800 text-left text-sm">
          <thead class="bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider text-xs">
            <tr>
              <th class="px-4 py-3.5">Session ID</th>
              <th class="px-4 py-3.5">Date</th>
              <th class="px-4 py-3.5">Village</th>
              <th class="px-4 py-3.5">Area</th>
              <th class="px-4 py-3.5">Conducted?</th>
              <th class="px-4 py-3.5">Participants</th>
              <th class="px-4 py-3.5">Educator</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800/80 text-slate-800 dark:text-slate-200">
            <tr
              v-for="s in sessions"
              :key="s.name"
              @click="openDetail(s)"
              class="hover:bg-emerald-50/40 dark:hover:bg-emerald-950/20 transition-colors cursor-pointer"
            >
              <!-- 1. Session ID -->
              <td class="px-4 py-3.5 whitespace-nowrap">
                <span class="font-bold text-emerald-700 dark:text-emerald-400 hover:underline">
                  {{ s.name }}
                </span>
              </td>

              <!-- 2. Date -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-600 dark:text-slate-400">
                {{ s.formatted_date || s.date }}
              </td>

              <!-- 3. Village -->
              <td class="px-4 py-3.5 whitespace-nowrap font-semibold text-slate-900 dark:text-slate-100">
                {{ s.village || '-' }}
              </td>

              <!-- 4. Area -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-700 dark:text-slate-300 font-medium">
                {{ s.area || '-' }}
              </td>

              <!-- 5. Conducted? -->
              <td class="px-4 py-3.5 whitespace-nowrap">
                <span
                  class="px-2.5 py-1 rounded-full text-xs font-bold"
                  :class="s.session_conducted === 'Yes' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'"
                >
                  {{ s.session_conducted || 'Yes' }}
                </span>
              </td>

              <!-- 6. Participants -->
              <td class="px-4 py-3.5 whitespace-nowrap">
                <span class="font-bold text-slate-900 dark:text-slate-100">{{ s.total_number_of_participants || 0 }}</span>
                <span class="text-xs text-slate-400 ml-1">attendees</span>
              </td>

              <!-- 7. Educator -->
              <td class="px-4 py-3.5 whitespace-nowrap text-slate-800 dark:text-slate-200 font-medium">
                {{ s.health_educator_name || '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

    <!-- Detail Dialog Modal Component -->
    <VillageHealthDetailModal
      :is-open="detailModalOpen"
      :session="selectedSession"
      @close="detailModalOpen = false"
    />

    <!-- Log Session Modal Component -->
    <VillageHealthModal
      :is-open="createModalOpen"
      @close="createModalOpen = false"
      @saved="loadSessions"
    />

  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import VillageHealthDetailModal from '@/components/VillageHealthDetailModal.vue'
import VillageHealthModal from '@/components/VillageHealthModal.vue'

export default {
  name: 'VillageHealthList',
  components: {
    FeatherIcon,
    VillageHealthDetailModal,
    VillageHealthModal,
  },
  data() {
    return {
      loading: false,
      sessions: [],
      totalRecords: 0,
      selectedSession: null,
      detailModalOpen: false,
      createModalOpen: false,
      filters: {
        search: '',
        session_conducted: '',
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
        this.filters.session_conducted ||
        this.filters.start_date ||
        this.filters.end_date
      )
    },
  },
  created() {
    this.loadSessions()
  },
  methods: {
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.loadSessions()
      }, 300)
    },
    clearFilters() {
      this.filters = {
        search: '',
        session_conducted: '',
        start_date: '',
        end_date: '',
      }
      this.loadSessions()
    },
    openDetail(s) {
      this.selectedSession = s
      this.detailModalOpen = true
    },
    async loadSessions() {
      this.loading = true
      try {
        const params = new URLSearchParams()
        if (this.filters.search) params.set('search', this.filters.search)
        if (this.filters.session_conducted) params.set('session_conducted', this.filters.session_conducted)
        if (this.filters.start_date) params.set('start_date', this.filters.start_date)
        if (this.filters.end_date) params.set('end_date', this.filters.end_date)
        params.set('page_size', '50')

        const res = await fetch(`/api/method/referral.api.get_portal_village_sessions?${params.toString()}`)
        const data = await res.json()
        if (data.message && data.message.records) {
          this.sessions = data.message.records
          this.totalRecords = data.message.total_records || this.sessions.length
        } else {
          this.sessions = []
          this.totalRecords = 0
        }
      } catch (e) {
        console.error('Failed to load sessions', e)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

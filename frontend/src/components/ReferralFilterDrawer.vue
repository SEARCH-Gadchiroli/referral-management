<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-hidden">
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
      @click="$emit('close')"
    ></div>

    <div class="fixed inset-y-0 right-0 max-w-full flex pl-10">
      <div class="w-screen max-w-md bg-white dark:bg-slate-900 shadow-2xl flex flex-col justify-between border-l border-slate-200 dark:border-slate-800">
        
        <!-- Header -->
        <div class="p-5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-800/50">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-sm">
              <FeatherIcon name="sliders" class="w-4 h-4" />
            </div>
            <div>
              <h2 class="text-base font-bold text-slate-900 dark:text-slate-100 leading-tight">Filter Referrals</h2>
              <p class="text-xs text-slate-400">Refine referral list by criteria</p>
            </div>
          </div>
          <button
            @click="$emit('close')"
            class="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <FeatherIcon name="x" class="w-4 h-4" />
          </button>
        </div>

        <!-- Scrollable Form Body -->
        <div class="p-5 overflow-y-auto space-y-4 flex-1 text-xs text-slate-700 dark:text-slate-300">
          
          <!-- Status -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Status</label>
            <select
              v-model="localFilters.status"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Statuses</option>
              <option v-for="opt in options.statuses || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Gender -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Gender</label>
            <select
              v-model="localFilters.gender"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Genders</option>
              <option v-for="opt in options.genders || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Age Range -->
          <div class="grid grid-cols-2 gap-2.5">
            <div>
              <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Min Age</label>
              <input
                type="number"
                min="0"
                v-model="localFilters.min_age"
                placeholder="e.g. 0"
                class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
              />
            </div>
            <div>
              <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Max Age</label>
              <input
                type="number"
                min="0"
                v-model="localFilters.max_age"
                placeholder="e.g. 100"
                class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
              />
            </div>
          </div>

          <!-- Patient Village -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Patient Village</label>
            <select
              v-model="localFilters.village"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Villages</option>
              <option v-for="opt in options.villages || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Taluka -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Taluka</label>
            <select
              v-model="localFilters.taluka"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Talukas</option>
              <option v-for="opt in options.talukas || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Tribal Classification -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Tribal Classification</label>
            <select
              v-model="localFilters.tribal_classification"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Classifications</option>
              <option v-for="opt in options.tribal_classifications || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- PHC -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">PHC</label>
            <select
              v-model="localFilters.phc"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All PHCs</option>
              <option v-for="opt in options.phcs || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Service Facility Type -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Service Facility Type</label>
            <select
              v-model="localFilters.service_facility_type"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Facilities</option>
              <option v-for="opt in options.service_facility_types || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- OPD Category -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">OPD Category</label>
            <select
              v-model="localFilters.opd_category"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Categories</option>
              <option v-for="opt in options.opd_categories || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- OPD Department -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">OPD Department</label>
            <select
              v-model="localFilters.opd_department"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Departments</option>
              <option v-for="opt in options.opd_departments || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Facility Visited -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Facility Visited</label>
            <select
              v-model="localFilters.facility_visited"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Visited Facilities</option>
              <option v-for="opt in options.facilities_visited || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Point of Referral -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Point of Referral</label>
            <select
              v-model="localFilters.referred_by_who"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Points of Referral</option>
              <option v-for="opt in options.referred_by_whos || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Referrer Name -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Referrer Name</label>
            <select
              v-model="localFilters.referrer_name"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Referrers</option>
              <option v-for="opt in options.referrer_names || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Referrer Department -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Referrer Department</label>
            <select
              v-model="localFilters.referrer_department"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Departments</option>
              <option v-for="opt in options.referrer_departments || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Referring Doctor -->
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Referring Doctor</label>
            <select
              v-model="localFilters.referring_doctor"
              class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
            >
              <option value="">All Doctors</option>
              <option v-for="opt in options.referring_doctors || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>

          <!-- Date Range -->
          <div class="grid grid-cols-2 gap-2.5">
            <div>
              <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">From Date</label>
              <input
                type="date"
                v-model="localFilters.start_date"
                class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
              />
            </div>
            <div>
              <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">To Date</label>
              <input
                type="date"
                v-model="localFilters.end_date"
                class="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-xs"
              />
            </div>
          </div>

        </div>

        <!-- Footer Actions -->
        <div class="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/60 flex items-center justify-between gap-3">
          <Button @click="resetDrawer" variant="subtle" class="text-xs text-slate-600 dark:text-slate-400">
            Clear All
          </Button>
          <div class="flex items-center gap-2">
            <Button @click="$emit('close')" variant="outline" class="text-xs">
              Cancel
            </Button>
            <Button
              @click="applyDrawer"
              variant="solid"
              class="text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium"
            >
              Apply Filters
            </Button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, Button } from 'frappe-ui'

export default {
  name: 'ReferralFilterDrawer',
  components: {
    FeatherIcon,
    Button,
  },
  props: {
    isOpen: Boolean,
    filters: Object,
    options: {
      type: Object,
      default: () => ({}),
    },
  },
  emits: ['close', 'apply', 'reset'],
  data() {
    return {
      localFilters: {},
    }
  },
  watch: {
    filters: {
      immediate: true,
      deep: true,
      handler(val) {
        this.localFilters = { ...val }
      },
    },
  },
  methods: {
    applyDrawer() {
      this.$emit('apply', { ...this.localFilters })
      this.$emit('close')
    },
    resetDrawer() {
      this.localFilters = {
        search: this.localFilters.search || '',
        status: '',
        gender: '',
        min_age: '',
        max_age: '',
        village: '',
        taluka: '',
        tribal_classification: '',
        phc: '',
        service_facility_type: '',
        opd_category: '',
        opd_department: '',
        facility_visited: '',
        referred_by_who: '',
        referrer_name: '',
        referrer_department: '',
        referring_doctor: '',
        start_date: '',
        end_date: '',
      }
      this.$emit('reset')
      this.$emit('close')
    },
  },
}
</script>

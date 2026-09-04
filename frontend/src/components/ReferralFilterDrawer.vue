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
              <p class="text-xs text-slate-400">Multi-select filters & criteria</p>
            </div>
          </div>
          <button
            @click="$emit('close')"
            class="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <FeatherIcon name="x" class="w-4 h-4" />
          </button>
        </div>

        <!-- Scrollable Form Body -->
        <div class="p-5 overflow-y-auto space-y-4 flex-1 text-xs text-slate-700 dark:text-slate-300">
          
          <!-- Status -->
          <MultiSelectDropdown
            label="Status"
            placeholder="All Statuses"
            :options="options.statuses || []"
            v-model="localFilters.status"
          />

          <!-- Gender -->
          <MultiSelectDropdown
            label="Gender"
            placeholder="All Genders"
            :options="options.genders || []"
            v-model="localFilters.gender"
          />

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
          <MultiSelectDropdown
            label="Patient Village"
            placeholder="All Villages"
            :options="options.villages || []"
            v-model="localFilters.village"
          />

          <!-- Taluka -->
          <MultiSelectDropdown
            label="Taluka"
            placeholder="All Talukas"
            :options="options.talukas || []"
            v-model="localFilters.taluka"
          />

          <!-- Tribal Classification -->
          <MultiSelectDropdown
            label="Tribal Classification"
            placeholder="All Classifications"
            :options="options.tribal_classifications || []"
            v-model="localFilters.tribal_classification"
          />

          <!-- PHC -->
          <MultiSelectDropdown
            label="PHC"
            placeholder="All PHCs"
            :options="options.phcs || []"
            v-model="localFilters.phc"
          />

          <!-- Service Facility Type -->
          <MultiSelectDropdown
            label="Service Facility Type"
            placeholder="All Facilities"
            :options="options.service_facility_types || []"
            v-model="localFilters.service_facility_type"
          />

          <!-- OPD Category -->
          <MultiSelectDropdown
            label="OPD Category"
            placeholder="All Categories"
            :options="options.opd_categories || []"
            v-model="localFilters.opd_category"
          />

          <!-- OPD Department -->
          <MultiSelectDropdown
            label="OPD Department"
            placeholder="All Departments"
            :options="options.opd_departments || []"
            v-model="localFilters.opd_department"
          />

          <!-- Facility Visited -->
          <MultiSelectDropdown
            label="Facility Visited"
            placeholder="All Visited Facilities"
            :options="options.facilities_visited || []"
            v-model="localFilters.facility_visited"
          />

          <!-- Point of Referral -->
          <MultiSelectDropdown
            label="Point of Referral"
            placeholder="All Points of Referral"
            :options="options.referred_by_whos || []"
            v-model="localFilters.referred_by_who"
          />

          <!-- Referrer Name -->
          <MultiSelectDropdown
            label="Referrer Name"
            placeholder="All Referrers"
            :options="options.referrer_names || []"
            v-model="localFilters.referrer_name"
          />

          <!-- Referrer Department -->
          <MultiSelectDropdown
            label="Referrer Department"
            placeholder="All Departments"
            :options="options.referrer_departments || []"
            v-model="localFilters.referrer_department"
          />

          <!-- Referring Doctor -->
          <MultiSelectDropdown
            label="Referring Doctor"
            placeholder="All Doctors"
            :options="options.referring_doctors || []"
            v-model="localFilters.referring_doctor"
          />

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
          <Button @click="resetDrawer" variant="subtle" class="text-xs text-slate-600 dark:text-slate-400 cursor-pointer">
            Clear All
          </Button>
          <div class="flex items-center gap-2">
            <Button @click="$emit('close')" variant="outline" class="text-xs cursor-pointer">
              Cancel
            </Button>
            <Button
              @click="applyDrawer"
              variant="solid"
              class="text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium cursor-pointer"
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
import MultiSelectDropdown from './MultiSelectDropdown.vue'

export default {
  name: 'ReferralFilterDrawer',
  components: {
    FeatherIcon,
    Button,
    MultiSelectDropdown,
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
        // Deep copy array values to prevent reference mutations
        const copy = {}
        for (const [k, v] of Object.entries(val || {})) {
          if (Array.isArray(v)) {
            copy[k] = [...v]
          } else if (typeof v === 'string' && ['status', 'gender', 'village', 'taluka', 'tribal_classification', 'phc', 'service_facility_type', 'opd_category', 'opd_department', 'facility_visited', 'referred_by_who', 'referrer_name', 'referrer_department', 'referring_doctor'].includes(k)) {
            copy[k] = v ? v.split(',').map(s => s.trim()).filter(Boolean) : []
          } else {
            copy[k] = v
          }
        }
        this.localFilters = copy
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
      this.$emit('reset')
      this.$emit('close')
    },
  },
}
</script>

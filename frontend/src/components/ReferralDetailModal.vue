<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
      @click="$emit('close')"
    ></div>

    <div class="flex min-h-full items-center justify-center p-4 sm:p-6">
      <div class="relative w-full max-w-3xl rounded-2xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[90vh]">
        
        <!-- Header -->
        <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/40">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-sm shrink-0">
              <FeatherIcon name="file-text" class="w-5 h-5" />
            </div>
            <div>
              <h2 class="text-base font-bold text-slate-900 dark:text-slate-100 leading-tight">Referral Details: {{ referral?.reference_number || referral?.name }}</h2>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Recorded on {{ referral?.referral_date || referral?.referral_recorded_date || '-' }}</p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <a
              :href="'/app/patient-referral/' + encodeURIComponent(referral?.name || '')"
              target="_blank"
              class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-3 py-1.5 text-xs font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 border border-indigo-200 dark:border-indigo-800 rounded-xl transition-colors cursor-pointer"
            >
              <FeatherIcon name="external-link" class="w-3.5 h-3.5 shrink-0" />
              <span>Open in Frappe Desk</span>
            </a>
            <button
              @click="$emit('close')"
              class="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <FeatherIcon name="x" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Scrollable Modal Body -->
        <div class="p-6 overflow-y-auto space-y-6 flex-1 text-sm text-slate-700 dark:text-slate-300">
          
          <!-- Status Banner & Quick Update -->
          <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div class="flex items-center gap-2.5">
              <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Current Status:</span>
              <span
                class="px-3 py-1 rounded-full font-bold text-xs"
                :class="statusBadgeClass(referral?.status)"
              >
                {{ referral?.status || 'Pending' }}
              </span>
            </div>

            <div class="flex items-center gap-2">
              <select
                v-model="updatedStatus"
                class="px-3 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium text-slate-900 dark:text-slate-100"
              >
                <option value="Pending">Pending</option>
                <option value="Follow-up In Progress">Follow-up In Progress</option>
                <option value="Visited">Visited</option>
                <option value="Closed - Not Visited">Closed - Not Visited</option>
                <option value="No-Show">No-Show</option>
                <option value="Cancelled">Cancelled</option>
              </select>
              <button
                @click="saveStatus"
                type="button"
                :disabled="updating"
                class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-3.5 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 rounded-xl transition-colors cursor-pointer disabled:opacity-50"
              >
                <div v-if="updating" class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin shrink-0"></div>
                <span>Update Status</span>
              </button>
            </div>
          </div>

          <!-- Patient Info -->
          <div>
            <h3 class="text-sm font-bold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-1.5">
              <FeatherIcon name="user" class="w-4 h-4 text-blue-600 shrink-0" />
              Patient Info
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50/70 dark:bg-slate-800/40 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700 text-xs">
              <div>
                <span class="text-slate-400 block text-[11px]">Patient Name</span>
                <span class="font-bold text-slate-900 dark:text-slate-100 text-sm">{{ referral?.patient_name }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Father's / Guardian Name</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.patient_father_name || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Age & Gender</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.patient_age }} yrs • {{ referral?.patient_gender }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Phone</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.patient_phone || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Village</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.patient_village || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Taluka</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.patient_taluka || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Referrer Info -->
          <div>
            <h3 class="text-sm font-bold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-1.5">
              <FeatherIcon name="send" class="w-4 h-4 text-blue-600 shrink-0" />
              Referrer Info
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50/70 dark:bg-slate-800/40 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700 text-xs">
              <div>
                <span class="text-slate-400 block text-[11px]">Referrer Name</span>
                <span class="font-bold text-slate-900 dark:text-slate-100 text-sm">{{ referral?.referrer_name || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Point of Referral</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.referred_by_who || referral?.referrer || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Referrer Phone</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.referrer_phone || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Department</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.referrer_department || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Referring Doctor</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.referred_doctor || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">PHC</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.phc || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Clinical & Visit Details -->
          <div>
            <h3 class="text-sm font-bold text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-1.5">
              <FeatherIcon name="activity" class="w-4 h-4 text-blue-600 shrink-0" />
              Clinical & Visit Details
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50/70 dark:bg-slate-800/40 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700 text-xs">
              <div>
                <span class="text-slate-400 block text-[11px]">Referral Date</span>
                <span class="font-semibold text-slate-900 dark:text-slate-100">{{ referral?.referral_date || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Recorded Date</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.referral_recorded_date || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Service Facility Type</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.service_facility_type || 'SEARCH' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">OPD Category</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.opd_category || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">OPD Department</span>
                <span class="font-bold text-blue-700 dark:text-blue-400 text-sm">{{ referral?.opd_departments || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Facility Actually Visited</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.facility_visited || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Hospital Registration No.</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.hospital_registration_number || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Visit Date</span>
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ referral?.visit_date || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Additional Notes -->
          <div v-if="referral?.additional_notes">
            <h3 class="text-sm font-bold text-slate-900 dark:text-slate-100 mb-2">Additional Notes</h3>
            <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
              {{ referral.additional_notes }}
            </div>
          </div>

          <!-- Supervisor Visits Child Table -->
          <div v-if="referral?.supervisor_visits && referral.supervisor_visits.length > 0">
            <h3 class="text-sm font-bold text-slate-900 dark:text-slate-100 mb-2">Supervisor Follow-up Visits</h3>
            <div class="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
              <table class="min-w-full divide-y divide-slate-100 dark:divide-slate-800 text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-semibold text-[11px]">
                  <tr>
                    <th class="px-3 py-2 text-left">Visit #</th>
                    <th class="px-3 py-2 text-left">Visit Date</th>
                    <th class="px-3 py-2 text-left">Visited?</th>
                    <th class="px-3 py-2 text-left">Facility</th>
                    <th class="px-3 py-2 text-left">Supervisor</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
                  <tr v-for="v in referral.supervisor_visits" :key="v.visit_number">
                    <td class="px-3 py-2 font-bold">{{ v.visit_number }}</td>
                    <td class="px-3 py-2">{{ v.visit_date }}</td>
                    <td class="px-3 py-2">{{ v.patient_visited || '-' }}</td>
                    <td class="px-3 py-2">{{ v.facility_visited || '-' }}</td>
                    <td class="px-3 py-2">{{ v.supervisor_name || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 flex items-center justify-end">
          <button
            @click="$emit('close')"
            type="button"
            class="inline-flex items-center justify-center flex-row whitespace-nowrap px-4 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 rounded-xl transition-colors cursor-pointer"
          >
            Close Dialog
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'ReferralDetailModal',
  components: {
    FeatherIcon,
  },
  props: {
    isOpen: Boolean,
    referral: Object,
  },
  emits: ['close', 'updated'],
  data() {
    return {
      updatedStatus: '',
      updating: false,
    }
  },
  watch: {
    referral: {
      immediate: true,
      handler(ref) {
        if (ref) {
          this.updatedStatus = ref.status || 'Pending'
        }
      },
    },
  },
  methods: {
    statusBadgeClass(status) {
      if (status === 'Visited') return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
      if (status === 'Follow-up In Progress') return 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
      if (status === 'Closed - Not Visited' || status === 'No-Show' || status === 'Cancelled') return 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'
      return 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300'
    },
    async saveStatus() {
      if (!this.referral || !this.referral.name) return
      this.updating = true
      try {
        const csrf = window.csrf_token || (document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || ''
        const res = await fetch(`/api/resource/Patient Referral/${encodeURIComponent(this.referral.name)}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Frappe-CSRF-Token': csrf,
          },
          body: JSON.stringify({
            status: this.updatedStatus,
          }),
        })
        if (res.ok) {
          this.referral.status = this.updatedStatus
          this.$emit('updated')
        } else {
          alert('Failed to update referral status.')
        }
      } catch (e) {
        alert('Error updating status: ' + e.message)
      } finally {
        this.updating = false
      }
    },
  },
}
</script>

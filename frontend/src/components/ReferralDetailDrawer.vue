<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-hidden">
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
      @click="$emit('close')"
    ></div>

    <div class="fixed inset-y-0 right-0 max-w-full flex pl-10">
      <div class="w-screen max-w-md bg-white shadow-2xl flex flex-col justify-between">
        
        <!-- Header -->
        <div class="p-6 border-b border-slate-100 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
              <FeatherIcon name="file-text" class="w-4 h-4" />
            </div>
            <div>
              <h2 class="text-sm font-bold text-slate-900 leading-tight">Referral Details</h2>
              <p class="text-[11px] text-slate-400">{{ referral?.name || referral?.reference_number }}</p>
            </div>
          </div>
          <button
            @click="$emit('close')"
            class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <FeatherIcon name="x" class="w-4 h-4" />
          </button>
        </div>

        <!-- Content -->
        <div class="p-6 overflow-y-auto space-y-6 flex-1 text-xs text-slate-700">
          
          <!-- Status Banner -->
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Referral Status</span>
              <span
                class="px-2.5 py-0.5 rounded-full font-bold text-[11px]"
                :class="statusBadgeClass(referral?.status)"
              >
                {{ referral?.status || 'Pending' }}
              </span>
            </div>

            <!-- Quick Status Change -->
            <div>
              <label class="block text-[11px] text-slate-500 mb-1">Update Status:</label>
              <select
                v-model="updatedStatus"
                class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-xs"
              >
                <option value="Pending">Pending</option>
                <option value="Follow-up In Progress">Follow-up In Progress</option>
                <option value="Visited">Visited</option>
                <option value="Closed - Not Visited">Closed - Not Visited</option>
                <option value="No-Show">No-Show</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          <!-- Patient Information -->
          <div class="space-y-2">
            <h3 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <FeatherIcon name="user" class="w-3.5 h-3.5 text-blue-600" />
              Patient Information
            </h3>
            <div class="grid grid-cols-2 gap-2 bg-slate-50/70 p-3.5 rounded-xl border border-slate-100">
              <div>
                <span class="text-[10px] text-slate-400 block">Name</span>
                <span class="font-semibold text-slate-800">{{ referral?.patient_name }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Demographics</span>
                <span>{{ referral?.patient_gender }} • {{ referral?.patient_age }} yrs</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Village & Taluka</span>
                <span>{{ referral?.patient_village || '-' }}, {{ referral?.patient_taluka || '-' }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Phone</span>
                <span>{{ referral?.patient_phone || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Clinical & Referral Info -->
          <div class="space-y-2">
            <h3 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <FeatherIcon name="activity" class="w-3.5 h-3.5 text-blue-600" />
              Referral Target & OPD
            </h3>
            <div class="grid grid-cols-2 gap-2 bg-slate-50/70 p-3.5 rounded-xl border border-slate-100">
              <div>
                <span class="text-[10px] text-slate-400 block">Facility Type</span>
                <span class="font-medium text-slate-800">{{ referral?.service_facility_type || 'SEARCH' }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">OPD Category</span>
                <span>{{ referral?.opd_category || '-' }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">OPD Department</span>
                <span class="font-semibold text-blue-700">{{ referral?.opd_departments || '-' }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Referred Doctor</span>
                <span>{{ referral?.referred_doctor || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Referrer Agent -->
          <div class="space-y-2">
            <h3 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <FeatherIcon name="send" class="w-3.5 h-3.5 text-blue-600" />
              Referrer Details
            </h3>
            <div class="grid grid-cols-2 gap-2 bg-slate-50/70 p-3.5 rounded-xl border border-slate-100">
              <div>
                <span class="text-[10px] text-slate-400 block">Referred By</span>
                <span class="font-medium">{{ referral?.referrer_name || referral?.referred_by_who || '-' }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Department</span>
                <span>{{ referral?.referrer_department || '-' }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Referral Date</span>
                <span>{{ referral?.referral_date }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">PHC</span>
                <span>{{ referral?.phc || '-' }}</span>
              </div>
            </div>
          </div>

        </div>

        <!-- Footer Actions -->
        <div class="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-end gap-2">
          <Button @click="$emit('close')" variant="outline" class="text-xs">
            Close
          </Button>
          <Button
            @click="saveStatus"
            variant="solid"
            class="text-xs bg-blue-600 hover:bg-blue-700 text-white"
            :loading="updating"
          >
            Save Status
          </Button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, Button } from 'frappe-ui'

export default {
  name: 'ReferralDetailDrawer',
  components: {
    FeatherIcon,
    Button,
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
      if (status === 'Visited') return 'bg-emerald-100 text-emerald-800'
      if (status === 'Follow-up In Progress') return 'bg-amber-100 text-amber-800'
      if (status === 'Closed - Not Visited' || status === 'No-Show' || status === 'Cancelled') return 'bg-rose-100 text-rose-800'
      return 'bg-blue-100 text-blue-800'
    },
    async saveStatus() {
      if (!this.referral || !this.referral.name) return
      this.updating = true
      try {
        const csrf = window.csrf_token || ''
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
          this.$emit('updated')
          this.$emit('close')
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

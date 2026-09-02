<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
      @click="$emit('close')"
    ></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div class="relative w-full max-w-lg rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-5">
        
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0">
              <FeatherIcon name="users" class="w-4 h-4" />
            </div>
            <div>
              <h2 class="text-base font-bold text-slate-900 dark:text-slate-100 leading-tight">Log Village Health Session</h2>
              <p class="text-xs text-slate-400">Community Health Education Record</p>
            </div>
          </div>
          <button
            @click="$emit('close')"
            class="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <FeatherIcon name="x" class="w-4 h-4" />
          </button>
        </div>

        <!-- Form fields -->
        <div class="space-y-4 text-xs">
          
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Session Date *</label>
              <input
                type="date"
                v-model="form.date"
                class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                required
              />
            </div>

            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Session Conducted?</label>
              <select
                v-model="form.session_conducted"
                class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              >
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Village Name</label>
              <input
                type="text"
                v-model="form.village"
                placeholder="Village name..."
                class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>

            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Area / Cluster</label>
              <input
                type="text"
                v-model="form.area"
                placeholder="Area name..."
                class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Total Participants</label>
              <input
                type="number"
                min="0"
                v-model.number="form.total_number_of_participants"
                class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>

            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Health Educator Name</label>
              <input
                type="text"
                v-model="form.health_educator_name"
                placeholder="Presenter name..."
                class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>

          <div>
            <label class="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Driver Name</label>
            <input
              type="text"
              v-model="form.search_driver_name"
              placeholder="SEARCH driver name..."
              class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

          <div v-if="form.session_conducted === 'No'">
            <label class="block text-slate-700 dark:text-slate-300 font-semibold mb-1">Reason for Not Conducting</label>
            <textarea
              v-model="form.reason_for_not_conducting"
              rows="2"
              placeholder="Explain why session was not conducted..."
              class="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            ></textarea>
          </div>

        </div>

        <!-- Footer -->
        <div class="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
          <button
            @click="$emit('close')"
            type="button"
            class="inline-flex items-center justify-center flex-row whitespace-nowrap px-3.5 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 rounded-xl transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            @click="submitSession"
            type="button"
            :disabled="saving"
            class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-4 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 rounded-xl shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            <div v-if="saving" class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin shrink-0"></div>
            <span>Save Session</span>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'VillageHealthModal',
  components: {
    FeatherIcon,
  },
  props: {
    isOpen: Boolean,
  },
  emits: ['close', 'saved'],
  data() {
    return {
      saving: false,
      form: {
        date: new Date().toISOString().split('T')[0],
        session_conducted: 'Yes',
        village: '',
        area: '',
        total_number_of_participants: 0,
        health_educator_name: '',
        search_driver_name: '',
        reason_for_not_conducting: '',
      },
    }
  },
  methods: {
    async submitSession() {
      if (!this.form.date) {
        alert('Please enter a session date.')
        return
      }

      this.saving = true
      try {
        const csrf = window.csrf_token || (document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || ''
        const res = await fetch('/api/resource/Village Health Education', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Frappe-CSRF-Token': csrf,
          },
          body: JSON.stringify(this.form),
        })

        if (res.ok) {
          this.$emit('saved')
          this.$emit('close')
          this.form = {
            date: new Date().toISOString().split('T')[0],
            session_conducted: 'Yes',
            village: '',
            area: '',
            total_number_of_participants: 0,
            health_educator_name: '',
            search_driver_name: '',
            reason_for_not_conducting: '',
          }
        } else {
          const err = await res.json()
          alert('Failed to save session: ' + (err.message || 'Error occurred'))
        }
      } catch (e) {
        alert('Error saving session: ' + e.message)
      } finally {
        this.saving = false
      }
    },
  },
}
</script>

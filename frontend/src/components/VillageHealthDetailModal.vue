<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
      @click="$emit('close')"
    ></div>

    <div class="flex min-h-full items-center justify-center p-4 sm:p-6">
      <div class="relative w-full max-w-3xl rounded-2xl bg-white shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        
        <!-- Header -->
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-sm">
              <FeatherIcon name="users" class="w-5 h-5" />
            </div>
            <div>
              <h2 class="text-base font-bold text-slate-900 leading-tight">Session Details: {{ session?.name }}</h2>
              <p class="text-xs text-slate-500 mt-0.5">Conducted on {{ session?.formatted_date || session?.date || '-' }}</p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <a
              :href="'/app/village-health-education/' + encodeURIComponent(session?.name || '')"
              target="_blank"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-100 rounded-xl transition-colors cursor-pointer"
            >
              <FeatherIcon name="external-link" class="w-3.5 h-3.5" />
              <span>Open in Frappe Desk</span>
            </a>
            <button
              @click="$emit('close')"
              class="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <FeatherIcon name="x" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Scrollable Modal Body -->
        <div class="p-6 overflow-y-auto space-y-6 flex-1 text-sm text-slate-700">
          
          <!-- Basic Info -->
          <div>
            <h3 class="text-sm font-bold text-slate-900 mb-2 flex items-center gap-1.5">
              <FeatherIcon name="calendar" class="w-4 h-4 text-emerald-600" />
              Session Information
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50/70 p-4 rounded-xl border border-slate-200/80 text-xs">
              <div>
                <span class="text-slate-400 block text-[11px]">Session ID</span>
                <span class="font-bold text-slate-900 text-sm">{{ session?.name }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Date</span>
                <span class="font-semibold text-slate-800">{{ session?.formatted_date || session?.date }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Village</span>
                <span class="font-bold text-slate-900">{{ session?.village || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Area</span>
                <span class="font-medium text-slate-800">{{ session?.area || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Execution Details -->
          <div>
            <h3 class="text-sm font-bold text-slate-900 mb-2 flex items-center gap-1.5">
              <FeatherIcon name="check-circle" class="w-4 h-4 text-emerald-600" />
              Execution Details
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50/70 p-4 rounded-xl border border-slate-200/80 text-xs">
              <div>
                <span class="text-slate-400 block text-[11px]">Session Conducted?</span>
                <span
                  class="inline-block mt-0.5 px-2 py-0.5 rounded-full text-xs font-bold"
                  :class="session?.session_conducted === 'Yes' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'"
                >
                  {{ session?.session_conducted || 'Yes' }}
                </span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Health Educator</span>
                <span class="font-semibold text-slate-900">{{ session?.health_educator_name || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Search Driver</span>
                <span class="font-medium text-slate-800">{{ session?.search_driver_name || '-' }}</span>
              </div>
              <div v-if="session?.reason_for_not_conducting" class="col-span-2 sm:col-span-3">
                <span class="text-slate-400 block text-[11px]">Reason for Cancellation</span>
                <span class="font-medium text-rose-700">{{ session?.reason_for_not_conducting }}</span>
              </div>
            </div>
          </div>

          <!-- Topics Covered -->
          <div v-if="session?.topics && session.topics.length > 0">
            <h3 class="text-sm font-bold text-slate-900 mb-2 flex items-center gap-1.5">
              <FeatherIcon name="book-open" class="w-4 h-4 text-emerald-600" />
              Topics Covered
            </h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(t, idx) in session.topics"
                :key="idx"
                class="px-3 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-full text-xs font-semibold"
              >
                {{ t.topic || t }}
              </span>
            </div>
          </div>

          <!-- Places & Attendance -->
          <div>
            <h3 class="text-sm font-bold text-slate-900 mb-2 flex items-center gap-1.5">
              <FeatherIcon name="map-pin" class="w-4 h-4 text-emerald-600" />
              Places & Attendance (Total Participants: {{ session?.total_number_of_participants || 0 }})
            </h3>
            <div v-if="session?.locations && session.locations.length > 0" class="rounded-xl border border-slate-200 overflow-hidden">
              <table class="min-w-full divide-y divide-slate-100 text-xs">
                <thead class="bg-slate-50 text-slate-600 font-semibold text-[11px]">
                  <tr>
                    <th class="px-3 py-2 text-left">Place Name</th>
                    <th class="px-3 py-2 text-left">Participants</th>
                    <th class="px-3 py-2 text-left">Photo</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 text-slate-700">
                  <tr v-for="(loc, idx) in session.locations" :key="idx">
                    <td class="px-3 py-2 font-medium">{{ loc.location_name || 'Location ' + (idx + 1) }}</td>
                    <td class="px-3 py-2 font-bold text-slate-900">{{ loc.number_of_participants || 0 }}</td>
                    <td class="px-3 py-2">
                      <a v-if="loc.photo" :href="loc.photo" target="_blank" class="text-indigo-600 hover:underline font-medium">View Photo</a>
                      <span v-else class="text-slate-400">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600">
              Total participants logged: <strong>{{ session?.total_number_of_participants || 0 }}</strong> across <strong>{{ session?.number_of_places || 1 }}</strong> places.
            </div>
          </div>

          <!-- Village Patil -->
          <div v-if="session?.village_patil_met">
            <h3 class="text-sm font-bold text-slate-900 mb-2 flex items-center gap-1.5">
              <FeatherIcon name="award" class="w-4 h-4 text-emerald-600" />
              Village Patil Meeting
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50/70 p-4 rounded-xl border border-slate-200/80 text-xs">
              <div>
                <span class="text-slate-400 block text-[11px]">Patil Met?</span>
                <span class="font-bold">{{ session?.village_patil_met }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Patil Name</span>
                <span class="font-medium">{{ session?.village_patil_name || '-' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[11px]">Feedback</span>
                <span class="font-medium">{{ session?.village_patil_feedback || session?.reason_for_not_meeting_patil || '-' }}</span>
              </div>
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-end">
          <Button @click="$emit('close')" variant="outline" class="text-xs">
            Close Dialog
          </Button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, Button } from 'frappe-ui'

export default {
  name: 'VillageHealthDetailModal',
  components: {
    FeatherIcon,
    Button,
  },
  props: {
    isOpen: Boolean,
    session: Object,
  },
  emits: ['close'],
}
</script>

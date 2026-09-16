<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
    <div
      class="bg-white dark:bg-slate-900 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in-95 duration-150"
    >
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/40 rounded-t-2xl">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-teal-50 dark:bg-teal-950/50 text-teal-600 dark:text-teal-400 flex items-center justify-center font-bold">
            <FeatherIcon name="home" class="w-5 h-5" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="font-bold text-lg text-slate-900 dark:text-slate-100">
                {{ household?.name || 'Household Dossier' }}
              </h3>
              <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-teal-100 dark:bg-teal-900 text-teal-800 dark:text-teal-200">
                {{ household?.village }}
              </span>
            </div>
            <p class="text-xs text-slate-500">
              House No: <strong>{{ household?.house_number }}</strong> | Family No: <strong>{{ household?.family_number }}</strong> | Village No: <strong>{{ household?.village_number }}</strong>
            </p>
          </div>
        </div>

        <button
          @click="$emit('close')"
          class="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          <FeatherIcon name="x" class="w-5 h-5" />
        </button>
      </div>

      <!-- Modal Body (Scrollable) -->
      <div v-if="loading" class="p-12 flex flex-col items-center justify-center">
        <div class="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-3 text-xs text-slate-500 font-medium">Loading household profile...</p>
      </div>

      <div v-else-if="household" class="p-6 overflow-y-auto space-y-6">
        <!-- 1. Family Head & Basic Info Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Head of Family</span>
            <div class="font-bold text-slate-900 dark:text-slate-100 mt-0.5 text-sm truncate">
              {{ household.head_of_household || '—' }}
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Mobile Number</span>
            <div class="font-bold text-slate-900 dark:text-slate-100 mt-0.5 text-sm">
              {{ household.mobile_number || 'No contact' }}
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Caste / Religion</span>
            <div class="font-bold text-slate-900 dark:text-slate-100 mt-0.5 text-sm truncate">
              {{ household.caste_of_head || '—' }} {{ household.religion_of_head ? `(${household.religion_of_head})` : '' }}
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-800">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Total Members</span>
            <div class="font-bold text-teal-600 dark:text-teal-400 mt-0.5 text-sm">
              {{ household.total_family_members }} Members
            </div>
          </div>
        </div>

        <!-- 2. Family Members Registry Table -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="font-bold text-slate-900 dark:text-slate-100 text-sm flex items-center gap-2">
              <FeatherIcon name="users" class="w-4 h-4 text-teal-500" />
              <span>Family Members Registry</span>
            </h4>
            <span class="text-xs text-slate-500 font-medium">{{ (household.family_members || []).length }} registered</span>
          </div>

          <div class="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-2xs">
            <table class="min-w-full divide-y divide-slate-200 dark:divide-slate-800 text-xs">
              <thead class="bg-slate-50 dark:bg-slate-800/80 font-bold text-slate-600 dark:text-slate-300">
                <tr>
                  <th class="px-3.5 py-2.5 text-left">ID</th>
                  <th class="px-3.5 py-2.5 text-left">Full Name</th>
                  <th class="px-3.5 py-2.5 text-left">Age / Gender</th>
                  <th class="px-3.5 py-2.5 text-left">Education</th>
                  <th class="px-3.5 py-2.5 text-left">Marital Status</th>
                  <th class="px-3.5 py-2.5 text-left">Birth Date</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-800 bg-white dark:bg-slate-900">
                <tr v-for="m in (household.family_members || [])" :key="m.name || m.identification_number" class="hover:bg-slate-50/80 dark:hover:bg-slate-800/40">
                  <td class="px-3.5 py-2 font-mono text-slate-500">{{ m.identification_number }}</td>
                  <td class="px-3.5 py-2 font-semibold text-slate-900 dark:text-slate-100">{{ m.member_name }}</td>
                  <td class="px-3.5 py-2 text-slate-600 dark:text-slate-300">{{ m.age }} yrs / {{ m.gender }}</td>
                  <td class="px-3.5 py-2 text-slate-600 dark:text-slate-300">{{ m.education || '—' }}</td>
                  <td class="px-3.5 py-2 text-slate-600 dark:text-slate-300">{{ m.marital_status || '—' }}</td>
                  <td class="px-3.5 py-2 text-slate-500">{{ m.birth_date || '—' }}</td>
                </tr>
                <tr v-if="!household.family_members?.length">
                  <td colspan="6" class="px-3.5 py-4 text-center text-slate-400">No family member records found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 3. Housing, Sanitation & Facilities Badges -->
        <div class="space-y-3">
          <h4 class="font-bold text-slate-900 dark:text-slate-100 text-sm flex items-center gap-2">
            <FeatherIcon name="check-circle" class="w-4 h-4 text-indigo-500" />
            <span>Housing, Sanitation & Facilities</span>
          </h4>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
            <div class="p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
              <span class="text-slate-500 block">Electricity:</span>
              <strong :class="isPositive(household.electricity_connection) ? 'text-emerald-600' : 'text-slate-700 dark:text-slate-300'">
                {{ household.electricity_connection || 'No' }}
              </strong>
            </div>

            <div class="p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
              <span class="text-slate-500 block">Toilet:</span>
              <strong :class="isPositive(household.toilet_present) ? 'text-emerald-600' : 'text-slate-700 dark:text-slate-300'">
                {{ household.toilet_present || 'No' }} (Usage: {{ household.toilet_usage || 'No' }})
              </strong>
            </div>

            <div class="p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
              <span class="text-slate-500 block">Bathroom:</span>
              <strong :class="isPositive(household.separate_bathroom) ? 'text-emerald-600' : 'text-slate-700 dark:text-slate-300'">
                {{ household.separate_bathroom || 'No' }}
              </strong>
            </div>

            <div class="p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
              <span class="text-slate-500 block">Bednets:</span>
              <strong>{{ household.bednet_available || 'No' }} (Total: {{ household.total_bednets || 0 }})</strong>
            </div>
          </div>
        </div>

        <!-- 4. Land & Government Schemes -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
            <h5 class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <FeatherIcon name="sun" class="w-3.5 h-3.5 text-emerald-500" />
              <span>Land & Agriculture</span>
            </h5>
            <div>Wet Land: <strong>{{ household.wet_land_acre || 0 }} acres, {{ household.wet_land_guntha || 0 }} guntha</strong></div>
            <div>Dry Land: <strong>{{ household.dry_land_acre || 0 }} acres, {{ household.dry_land_guntha || 0 }} guntha</strong></div>
            <div>Well in Farm: <strong>{{ household.well_in_farm || 'No' }}</strong></div>
          </div>

          <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2">
            <h5 class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <FeatherIcon name="award" class="w-3.5 h-3.5 text-purple-500" />
              <span>Government Schemes & Cards</span>
            </h5>
            <div>Ration Card: <strong>{{ household.ration_card || 'None' }}</strong></div>
            <div>Health Scheme Card: <strong>{{ household.health_scheme_card || 'None' }}</strong></div>
            <div>Rooms: <strong>{{ household.total_rooms || '—' }}</strong> | Beds: <strong>{{ household.total_beds || '—' }}</strong></div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-3 border-t border-slate-200 dark:border-slate-800 flex justify-end bg-slate-50/50 dark:bg-slate-800/40 rounded-b-2xl">
        <button
          @click="$emit('close')"
          class="px-4 py-2 rounded-xl bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold hover:bg-slate-300 dark:hover:bg-slate-600 transition"
        >
          Close Dossier
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
  isOpen: { type: Boolean, default: false },
  household: { type: Object, default: () => null },
  loading: { type: Boolean, default: false }
})

defineEmits(['close'])

const isPositive = (val) => {
  if (!val) return false
  const s = String(val).toLowerCase()
  return s.includes('yes') || s === '1'
}
</script>

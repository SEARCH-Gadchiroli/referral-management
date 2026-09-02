<template>
  <div class="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8 space-y-8">
    
    <!-- Hero Header -->
    <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-8 sm:p-10 text-white shadow-xl shadow-slate-900/10 relative overflow-hidden">
      <div class="absolute right-0 top-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
      <div class="relative z-10 max-w-2xl">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-indigo-200 text-xs font-medium backdrop-blur-md mb-4">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>SEARCH Health Operations System</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight">Clinical & Field Operations Portal</h1>
        <p class="mt-3 text-slate-300 text-sm sm:text-base leading-relaxed">
          Welcome to the unified operations hub. Seamlessly manage Mobile Medical Unit (MMU) patient encounters, track secondary care referrals, log village health education sessions, and inspect real-time analytics.
        </p>
      </div>
    </div>

    <!-- Modules Grid -->
    <div>
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-lg font-bold text-slate-900 dark:text-slate-100">Application Modules</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400">Select a workspace to view or input operational data.</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <!-- MMU Card -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md hover:border-rose-200 dark:hover:border-rose-900/50 transition-all duration-200 flex flex-col justify-between group">
          <div>
            <div class="w-12 h-12 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-100 dark:border-rose-900/50 flex items-center justify-center text-rose-600 dark:text-rose-400 mb-4 group-hover:scale-105 transition-transform">
              <FeatherIcon name="truck" class="w-6 h-6 shrink-0" />
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-slate-100 group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors">Mobile Medical Unit</h3>
            <p class="mt-2 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Record daily patient encounters, multi-tier coded diagnoses, and medicine distributions across Dhanora taluka villages.
            </p>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <router-link
              to="/mmu"
              class="inline-flex items-center flex-row gap-1 whitespace-nowrap text-xs font-semibold text-rose-600 dark:text-rose-400 hover:text-rose-700"
            >
              <span>Browse Visits</span>
              <span>→</span>
            </router-link>
            <router-link
              to="/mmu/new"
              class="inline-flex items-center flex-row gap-1 whitespace-nowrap px-2.5 py-1 text-xs font-medium bg-rose-50 dark:bg-rose-950/50 hover:bg-rose-100 dark:hover:bg-rose-900/50 text-rose-700 dark:text-rose-300 rounded-lg transition-colors"
            >
              <span>+ New Visit</span>
            </router-link>
          </div>
        </div>

        <!-- Referrals Card -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md hover:border-blue-200 dark:hover:border-blue-900/50 transition-all duration-200 flex flex-col justify-between group">
          <div>
            <div class="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-950/50 border border-blue-100 dark:border-blue-900/50 flex items-center justify-center text-blue-600 dark:text-blue-400 mb-4 group-hover:scale-105 transition-transform">
              <FeatherIcon name="file-text" class="w-6 h-6 shrink-0" />
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">Patient Referrals</h3>
            <p class="mt-2 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Track clinical referral status, OPD appointment pipelines, doctor recommendations, and follow-up records.
            </p>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <router-link
              to="/referrals"
              class="inline-flex items-center flex-row gap-1 whitespace-nowrap text-xs font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700"
            >
              <span>View Referrals</span>
              <span>→</span>
            </router-link>
          </div>
        </div>

        <!-- Village Health Card -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md hover:border-emerald-200 dark:hover:border-emerald-900/50 transition-all duration-200 flex flex-col justify-between group">
          <div>
            <div class="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-100 dark:border-emerald-900/50 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-4 group-hover:scale-105 transition-transform">
              <FeatherIcon name="users" class="w-6 h-6 shrink-0" />
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">Village Health Education</h3>
            <p class="mt-2 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Monitor village public health sessions, topics covered, community attendance, and field trainer activities.
            </p>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <router-link
              to="/village-health"
              class="inline-flex items-center flex-row gap-1 whitespace-nowrap text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:text-emerald-700"
            >
              <span>View Sessions</span>
              <span>→</span>
            </router-link>
          </div>
        </div>

        <!-- Analytics / Metabase Card -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md hover:border-violet-200 dark:hover:border-violet-900/50 transition-all duration-200 flex flex-col justify-between group">
          <div>
            <div class="w-12 h-12 rounded-xl bg-violet-50 dark:bg-violet-950/50 border border-violet-100 dark:border-violet-900/50 flex items-center justify-center text-violet-600 dark:text-violet-400 mb-4 group-hover:scale-105 transition-transform">
              <FeatherIcon name="bar-chart-2" class="w-6 h-6 shrink-0" />
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-slate-100 group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors">Metabase Dashboards</h3>
            <p class="mt-2 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Interactive analytics dashboards for epidemiological trends, patient visit volumes, and departmental indicators.
            </p>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <router-link
              to="/dashboards"
              class="inline-flex items-center flex-row gap-1 whitespace-nowrap text-xs font-semibold text-violet-600 dark:text-violet-400 hover:text-violet-700"
            >
              <span>Open Dashboards</span>
              <span>→</span>
            </router-link>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'Home',
  components: {
    FeatherIcon,
  },
}
</script>

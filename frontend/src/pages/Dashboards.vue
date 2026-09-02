<template>
  <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
    
    <!-- View 1: Single Embedded Dashboard -->
    <div v-if="currentDashboardName" class="space-y-6">
      
      <!-- Top Control Bar -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
        <div class="flex items-center gap-3">
          <router-link
            to="/dashboards"
            class="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors inline-flex items-center gap-1.5 text-xs font-semibold"
          >
            <FeatherIcon name="arrow-left" class="w-4 h-4" />
            <span>All Dashboards</span>
          </router-link>
          <div class="h-5 w-px bg-slate-200 hidden sm:block"></div>
          <div>
            <h1 class="text-base font-bold text-slate-900 leading-tight">
              {{ embedResource.data?.title || currentDashboardName }}
            </h1>
            <p v-if="embedResource.data?.description" class="text-xs text-slate-500 mt-0.5">
              {{ embedResource.data.description }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <Button
            @click="embedResource.reload()"
            variant="subtle"
            class="text-xs text-slate-600"
            :loading="embedResource.loading"
          >
            <FeatherIcon name="refresh-cw" class="w-3.5 h-3.5 mr-1" />
            Reload
          </Button>
        </div>
      </div>

      <!-- Iframe Container -->
      <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden min-h-[600px] relative">
        <div v-if="embedResource.loading" class="absolute inset-0 bg-white/80 backdrop-blur-xs flex flex-col items-center justify-center gap-3 z-10">
          <div class="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-xs font-medium text-slate-600">Generating secure analytics token...</span>
        </div>

        <div v-else-if="embedResource.error" class="p-12 text-center space-y-3">
          <div class="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
            <FeatherIcon name="alert-circle" class="w-6 h-6" />
          </div>
          <h3 class="text-base font-bold text-slate-900">Unable to Load Dashboard</h3>
          <p class="text-xs text-slate-500 max-w-md mx-auto">
            {{ embedResource.error.message || 'You may not have permissions or Metabase is unreachable.' }}
          </p>
          <Button @click="$router.push('/dashboards')" variant="outline" class="text-xs">
            Return to Dashboard List
          </Button>
        </div>

        <iframe
          v-else-if="embedResource.data?.url"
          :src="embedResource.data.url"
          class="w-full border-0"
          :style="{ height: (embedResource.data.height || 850) + 'px' }"
          allowtransparency
        ></iframe>
      </div>

    </div>

    <!-- View 2: Dashboards Gallery -->
    <div v-else class="space-y-6">
      
      <!-- Header -->
      <div class="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Analytics & Intelligence</h1>
          <p class="mt-1 text-xs text-slate-500">Explore interactive operational and clinical Metabase reports.</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="dashboardList.loading" class="py-16 text-center">
        <div class="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <span class="text-xs text-slate-500">Loading accessible dashboards...</span>
      </div>

      <!-- Empty State -->
      <div v-else-if="!dashboardList.data || dashboardList.data.length === 0" class="bg-white rounded-2xl p-12 text-center border border-slate-200 space-y-3">
        <div class="w-12 h-12 rounded-2xl bg-violet-50 text-violet-600 flex items-center justify-center mx-auto">
          <FeatherIcon name="lock" class="w-6 h-6" />
        </div>
        <h3 class="text-base font-bold text-slate-800">No Dashboards Available</h3>
        <p class="text-xs text-slate-500 max-w-sm mx-auto">
          No active Metabase dashboards are currently configured for your role. Contact your system administrator for access.
        </p>
      </div>

      <!-- Dashboard Cards Grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="dash in dashboardList.data"
          :key="dash.name"
          @click="openDashboard(dash.name)"
          class="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs hover:shadow-md hover:border-violet-300 transition-all duration-200 cursor-pointer flex flex-col justify-between group relative overflow-hidden"
        >
          <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-violet-500 to-indigo-500"></div>
          
          <div>
            <div class="w-10 h-10 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
              <FeatherIcon name="activity" class="w-5 h-5" />
            </div>
            <h3 class="text-base font-bold text-slate-900 group-hover:text-violet-600 transition-colors">
              {{ dash.title }}
            </h3>
            <p class="mt-2 text-xs text-slate-500 line-clamp-2 leading-relaxed">
              {{ dash.description || 'Explore aggregated metrics and operational indicators.' }}
            </p>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-violet-600 group-hover:text-violet-700">
            <span>View Analytics</span>
            <span>→</span>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script>
import { FeatherIcon, Button, createResource } from 'frappe-ui'

export default {
  name: 'Dashboards',
  components: {
    FeatherIcon,
    Button,
  },
  setup() {
    const dashboardList = createResource({
      url: 'frappe_metabase.api.embed.get_dashboard_list',
      auto: true,
    })

    const embedResource = createResource({
      url: 'frappe_metabase.api.embed.get_embed_url',
      auto: false,
    })

    return {
      dashboardList,
      embedResource,
    }
  },
  computed: {
    currentDashboardName() {
      return this.$route.params.name || this.$route.query.name || ''
    },
  },
  watch: {
    currentDashboardName: {
      immediate: true,
      handler(name) {
        if (name) {
          this.embedResource.fetch({
            doctype: 'Metabase Dashboard',
            name: name,
          })
        }
      },
    },
  },
  methods: {
    openDashboard(name) {
      this.$router.push('/dashboards/' + encodeURIComponent(name))
    },
  },
}
</script>

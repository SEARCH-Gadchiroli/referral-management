<template>
  <header class="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30 shadow-xs transition-colors duration-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        
        <!-- Brand & Nav Links -->
        <div class="flex items-center gap-8">
          <router-link to="/" class="flex items-center gap-3 group">
            <div class="w-10 h-10 rounded-xl bg-white p-1 border border-slate-200/80 dark:border-slate-700 shadow-sm flex items-center justify-center overflow-hidden group-hover:scale-105 transition-transform duration-200">
              <img
                :src="'/assets/referral/images/search-logo.jpg'"
                alt="SEARCH Logo"
                class="w-full h-full object-contain rounded-lg"
              />
            </div>
            <div class="flex flex-col">
              <span class="font-bold text-slate-900 dark:text-slate-100 text-base tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">SEARCH Portal</span>
              <span class="text-xs text-slate-500 dark:text-slate-400 font-medium">Gadchiroli Operations</span>
            </div>
          </router-link>

          <!-- Desktop Navigation Tabs -->
          <nav class="hidden md:flex items-center gap-1.5 pl-4 border-l border-slate-200 dark:border-slate-800">
            <router-link
              to="/"
              custom
              v-slot="{ href, navigate, isActive, isExactActive }"
            >
              <a
                :href="href"
                @click="navigate"
                :class="[
                  isExactActive
                    ? 'bg-slate-100 dark:bg-slate-800 text-indigo-700 dark:text-indigo-400 font-bold shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800/60 font-medium',
                  'px-3.5 py-2 rounded-xl text-sm transition-all duration-150 flex items-center gap-2'
                ]"
              >
                <FeatherIcon name="home" class="w-4 h-4" />
                <span>Home</span>
              </a>
            </router-link>

            <router-link
              to="/mmu"
              custom
              v-slot="{ href, navigate, isActive }"
            >
              <a
                :href="href"
                @click="navigate"
                :class="[
                  isActive
                    ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 font-bold shadow-xs border border-rose-100 dark:border-rose-900/50'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800/60 font-medium',
                  'px-3.5 py-2 rounded-xl text-sm transition-all duration-150 flex items-center gap-2'
                ]"
              >
                <FeatherIcon name="truck" class="w-4 h-4" />
                <span>MMU Visits</span>
              </a>
            </router-link>

            <router-link
              to="/referrals"
              custom
              v-slot="{ href, navigate, isActive }"
            >
              <a
                :href="href"
                @click="navigate"
                :class="[
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 font-bold shadow-xs border border-blue-100 dark:border-blue-900/50'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800/60 font-medium',
                  'px-3.5 py-2 rounded-xl text-sm transition-all duration-150 flex items-center gap-2'
                ]"
              >
                <FeatherIcon name="file-text" class="w-4 h-4" />
                <span>Referrals</span>
              </a>
            </router-link>

            <router-link
              to="/village-health"
              custom
              v-slot="{ href, navigate, isActive }"
            >
              <a
                :href="href"
                @click="navigate"
                :class="[
                  isActive
                    ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 font-bold shadow-xs border border-emerald-100 dark:border-emerald-900/50'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800/60 font-medium',
                  'px-3.5 py-2 rounded-xl text-sm transition-all duration-150 flex items-center gap-2'
                ]"
              >
                <FeatherIcon name="users" class="w-4 h-4" />
                <span>Village Health</span>
              </a>
            </router-link>

            <router-link
              to="/dashboards"
              custom
              v-slot="{ href, navigate, isActive }"
            >
              <a
                :href="href"
                @click="navigate"
                :class="[
                  isActive
                    ? 'bg-violet-50 dark:bg-violet-950/40 text-violet-700 dark:text-violet-300 font-bold shadow-xs border border-violet-100 dark:border-violet-900/50'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800/60 font-medium',
                  'px-3.5 py-2 rounded-xl text-sm transition-all duration-150 flex items-center gap-2'
                ]"
              >
                <FeatherIcon name="bar-chart-2" class="w-4 h-4" />
                <span>Dashboards</span>
              </a>
            </router-link>
          </nav>
        </div>

        <!-- User, Actions & Manual Theme Control -->
        <div class="flex items-center gap-3">
          
          <!-- Ultra-Visible Manual Theme Toggle Pill -->
          <button
            @click="toggleTheme"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold border transition-all duration-200 cursor-pointer shadow-2xs"
            :class="isDark
              ? 'bg-slate-800 text-amber-300 border-slate-700 hover:bg-slate-700'
              : 'bg-slate-100 text-slate-700 border-slate-300 hover:bg-slate-200'"
            title="Toggle Light / Dark Theme"
          >
            <!-- Sun icon -->
            <svg v-if="isDark" class="w-4 h-4 text-amber-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <!-- Moon icon -->
            <svg v-else class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            <span>{{ isDark ? 'Light' : 'Dark' }}</span>
          </button>

          <!-- User Badge -->
          <div class="hidden sm:flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <div class="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 font-bold text-xs flex items-center justify-center">
              {{ (user.data?.full_name || 'U').charAt(0).toUpperCase() }}
            </div>
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-300 max-w-[130px] truncate">
              {{ user.data?.full_name || 'Signed In' }}
            </span>
          </div>

          <!-- Sign Out Button -->
          <button
            @click="handleLogout"
            class="inline-flex items-center gap-1.5 px-3 py-2 text-sm font-semibold text-slate-600 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl transition-colors cursor-pointer"
            title="Sign out of portal"
          >
            <FeatherIcon name="log-out" class="w-4 h-4" />
            <span class="hidden sm:inline">Sign Out</span>
          </button>

          <!-- Mobile menu button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <FeatherIcon :name="mobileMenuOpen ? 'x' : 'menu'" class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Mobile dropdown -->
      <div v-if="mobileMenuOpen" class="md:hidden py-3 border-t border-slate-100 dark:border-slate-800 space-y-1 text-sm">
        <router-link
          to="/"
          @click="mobileMenuOpen = false"
          class="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium"
        >
          <FeatherIcon name="home" class="w-4 h-4 text-slate-400" />
          Home
        </router-link>
        <router-link
          to="/mmu"
          @click="mobileMenuOpen = false"
          class="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium"
        >
          <FeatherIcon name="truck" class="w-4 h-4 text-rose-500" />
          MMU Visits
        </router-link>
        <router-link
          to="/referrals"
          @click="mobileMenuOpen = false"
          class="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium"
        >
          <FeatherIcon name="file-text" class="w-4 h-4 text-blue-500" />
          Referrals
        </router-link>
        <router-link
          to="/village-health"
          @click="mobileMenuOpen = false"
          class="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium"
        >
          <FeatherIcon name="users" class="w-4 h-4 text-emerald-500" />
          Village Health Education
        </router-link>
        <router-link
          to="/dashboards"
          @click="mobileMenuOpen = false"
          class="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium"
        >
          <FeatherIcon name="bar-chart-2" class="w-4 h-4 text-violet-500" />
          Dashboards
        </router-link>
      </div>
    </div>
  </header>
</template>

<script>
import { FeatherIcon, createResource } from 'frappe-ui'

export default {
  name: 'Navbar',
  components: {
    FeatherIcon,
  },
  data() {
    return {
      mobileMenuOpen: false,
      isDark: false,
    }
  },
  setup() {
    const user = createResource({
      url: 'frappe.auth.get_logged_user',
      auto: true,
      transform: (data) => {
        return {
          full_name: data,
        }
      },
    })
    return {
      user,
    }
  },
  created() {
    this.initTheme()
  },
  methods: {
    initTheme() {
      const saved = localStorage.getItem('portal_theme')
      if (saved === 'dark') {
        this.isDark = true
        document.documentElement.classList.add('dark')
      } else {
        this.isDark = false
        document.documentElement.classList.remove('dark')
      }
    },
    toggleTheme() {
      this.isDark = !this.isDark
      if (this.isDark) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('portal_theme', 'dark')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('portal_theme', 'light')
      }
    },
    async handleLogout() {
      try {
        const csrf = window.csrf_token || (document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || ''
        await fetch('/api/method/logout', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': csrf,
          },
        })
      } catch (e) {
        console.warn('Logout post error', e)
      } finally {
        window.location.href = '/login?redirect-to=/portal'
      }
    },
  },
}
</script>

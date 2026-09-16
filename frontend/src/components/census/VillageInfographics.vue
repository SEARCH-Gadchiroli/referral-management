<template>
  <div class="space-y-6">
    <!-- Top Filter & Selected Village Header -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <span class="p-2.5 rounded-xl bg-teal-50 dark:bg-teal-950/50 text-teal-600 dark:text-teal-400">
              <FeatherIcon name="map-pin" class="w-5 h-5" />
            </span>
            <div>
              <h2 class="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <span>{{ selectedVillage === 'ALL' ? 'Dhanora Taluka (232 Tribal Villages)' : selectedVillage }}</span>
                <span v-if="selectedVillageMarathi" class="text-slate-500 dark:text-slate-400 font-normal text-base">({{ selectedVillageMarathi }})</span>
              </h2>
              <p class="text-xs text-slate-500 dark:text-slate-400">
                Socio-demographic, housing, and health infographics registry
              </p>
            </div>
          </div>
        </div>

        <!-- Village Selector -->
        <div class="flex items-center gap-3">
          <div class="relative min-w-[280px]">
            <select
              :value="selectedVillage"
              @change="$emit('update:selectedVillage', $event.target.value)"
              class="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="ALL">🌐 All Tribal Villages (Taluka Overview)</option>
              <option v-for="v in villages" :key="v.village_name" :value="v.village_name">
                {{ v.village_name }} {{ v.village_name_marathi ? `(${v.village_name_marathi})` : '' }} — {{ v.total_households }} HH
              </option>
            </select>
          </div>

          <button
            @click="$emit('refresh')"
            :disabled="loading"
            class="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition"
            title="Refresh Data"
          >
            <FeatherIcon name="refresh-cw" :class="['w-4 h-4', { 'animate-spin': loading }]" />
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-16 flex flex-col items-center justify-center">
      <div class="w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-4 text-sm font-medium text-slate-600 dark:text-slate-400">Computing village infographics & charts...</p>
    </div>

    <!-- Analytics Dashboard Content -->
    <div v-else-if="analytics && analytics.kpis" class="space-y-6">
      
      <!-- 1. Executive KPI Summary Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Households</span>
            <FeatherIcon name="home" class="w-4 h-4 text-teal-600 dark:text-teal-400" />
          </div>
          <div class="text-2xl font-black text-slate-900 dark:text-slate-100">{{ analytics.kpis.total_households }}</div>
          <div class="text-[11px] text-slate-500 mt-1">Avg size: {{ analytics.kpis.avg_family_size }} / family</div>
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Population</span>
            <FeatherIcon name="users" class="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div class="text-2xl font-black text-slate-900 dark:text-slate-100">{{ analytics.kpis.total_population }}</div>
          <div class="text-[11px] text-slate-500 mt-1">M: {{ analytics.kpis.male_population }} | F: {{ analytics.kpis.female_population }}</div>
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Sex Ratio</span>
            <FeatherIcon name="heart" class="w-4 h-4 text-rose-600 dark:text-rose-400" />
          </div>
          <div class="text-2xl font-black text-slate-900 dark:text-slate-100">{{ analytics.kpis.sex_ratio }}</div>
          <div class="text-[11px] text-slate-500 mt-1">Females / 1,000 Males</div>
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Children &le;5</span>
            <FeatherIcon name="smile" class="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div class="text-2xl font-black text-slate-900 dark:text-slate-100">{{ analytics.kpis.children_u5 }}</div>
          <div class="text-[11px] text-slate-500 mt-1">{{ ((analytics.kpis.children_u5 / (analytics.kpis.total_population || 1)) * 100).toFixed(1) }}% of population</div>
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Electricity</span>
            <FeatherIcon name="zap" class="w-4 h-4 text-amber-500" />
          </div>
          <div class="text-2xl font-black text-slate-900 dark:text-slate-100">{{ analytics.kpis.electricity_pct }}%</div>
          <div class="text-[11px] text-slate-500 mt-1">Electrified houses</div>
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 shadow-xs">
          <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Farm Land</span>
            <FeatherIcon name="sun" class="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div class="text-2xl font-black text-slate-900 dark:text-slate-100">{{ (analytics.kpis.total_wet_land_acres + analytics.kpis.total_dry_land_acres).toFixed(1) }}</div>
          <div class="text-[11px] text-slate-500 mt-1">Total acres recorded</div>
        </div>
      </div>

      <!-- 2. Demographics Charts: Age Pyramid Bar Chart + Gender Donut Chart -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Interactive Chart: Age Cohorts Bar Chart (2 Cols) -->
        <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-5">
              <div>
                <h3 class="font-bold text-slate-900 dark:text-slate-100 text-base flex items-center gap-2">
                  <FeatherIcon name="bar-chart-2" class="w-4 h-4 text-indigo-500" />
                  <span>Age Cohort & Demographic Pyramid</span>
                </h3>
                <p class="text-xs text-slate-500 mt-0.5">Distribution across age groups for {{ analytics.kpis.total_population }} individuals</p>
              </div>
              <span class="text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 px-3 py-1 rounded-full border border-indigo-100 dark:border-indigo-900">
                5 Age Tiers
              </span>
            </div>

            <!-- SVG Bar Chart -->
            <div class="space-y-4 pt-2">
              <div v-for="cohort in ageCohortList" :key="cohort.key" class="group">
                <div class="flex items-center justify-between text-xs mb-1.5 font-medium">
                  <div class="flex items-center gap-2">
                    <span :class="['w-2.5 h-2.5 rounded-full', cohort.dotClass]"></span>
                    <span class="text-slate-800 dark:text-slate-200 font-semibold">{{ cohort.label }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-slate-900 dark:text-slate-100 font-bold text-sm">{{ cohort.count.toLocaleString() }}</span>
                    <span class="text-slate-500 text-xs">({{ cohort.pct }}%)</span>
                  </div>
                </div>
                
                <!-- Bar Container -->
                <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-xl h-4 p-0.5 overflow-hidden shadow-inner">
                  <div
                    :class="['h-full rounded-lg transition-all duration-700 ease-out shadow-xs group-hover:opacity-90', cohort.barGradient]"
                    :style="{ width: `${Math.max(Number(cohort.pct), 2)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Demographic Badges -->
          <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 grid grid-cols-3 gap-2 text-center text-xs">
            <div class="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <div class="text-slate-400 text-[10px] uppercase font-bold">Child Population</div>
              <div class="font-black text-amber-600 dark:text-amber-400 mt-0.5">{{ (((analytics.kpis.children_u5 || 0) / (analytics.kpis.total_population || 1)) * 100).toFixed(1) }}%</div>
            </div>
            <div class="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <div class="text-slate-400 text-[10px] uppercase font-bold">Working Age (19-60)</div>
              <div class="font-black text-indigo-600 dark:text-indigo-400 mt-0.5">
                {{ ((((analytics.demographics.age_cohorts.youth || 0) + (analytics.demographics.age_cohorts.middle || 0)) / (analytics.kpis.total_population || 1)) * 100).toFixed(1) }}%
              </div>
            </div>
            <div class="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <div class="text-slate-400 text-[10px] uppercase font-bold">Elderly (60+)</div>
              <div class="font-black text-purple-600 dark:text-purple-400 mt-0.5">{{ (((analytics.kpis.senior_citizens || 0) / (analytics.kpis.total_population || 1)) * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </div>

        <!-- Interactive Chart: Gender Composition Donut (1 Col) -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-slate-900 dark:text-slate-100 text-base flex items-center gap-2">
                <FeatherIcon name="pie-chart" class="w-4 h-4 text-rose-500" />
                <span>Gender Breakdown</span>
              </h3>
              <span class="text-xs text-slate-500">Sex Ratio</span>
            </div>

            <!-- SVG Donut Chart -->
            <div class="relative flex items-center justify-center my-3">
              <svg class="w-44 h-44 -rotate-90 transform" viewBox="0 0 100 100">
                <!-- Background track -->
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  stroke-width="12"
                  fill="transparent"
                  class="stroke-slate-100 dark:stroke-slate-800"
                />
                <!-- Male Segment -->
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  stroke-width="12"
                  fill="transparent"
                  stroke="currentColor"
                  class="text-indigo-500 transition-all duration-1000 ease-out"
                  :stroke-dasharray="`${maleCircleLength} 240`"
                  stroke-dashoffset="0"
                  stroke-linecap="round"
                />
                <!-- Female Segment -->
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  stroke-width="12"
                  fill="transparent"
                  stroke="currentColor"
                  class="text-rose-500 transition-all duration-1000 ease-out"
                  :stroke-dasharray="`${femaleCircleLength} 240`"
                  :stroke-dashoffset="`-${maleCircleLength}`"
                  stroke-linecap="round"
                />
              </svg>

              <!-- Central Donut Text -->
              <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center">
                <span class="text-xs uppercase tracking-wider font-bold text-slate-400">Sex Ratio</span>
                <span class="text-xl font-black text-slate-900 dark:text-slate-100">{{ analytics.kpis.sex_ratio }}</span>
                <span class="text-[10px] text-slate-500">F / 1k M</span>
              </div>
            </div>
          </div>

          <!-- Legend -->
          <div class="space-y-2 pt-3 border-t border-slate-100 dark:border-slate-800">
            <div class="flex items-center justify-between text-xs p-2 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/30">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-indigo-500"></span>
                <span class="text-slate-700 dark:text-slate-300 font-medium">Male</span>
              </div>
              <span class="font-bold text-indigo-700 dark:text-indigo-300">
                {{ analytics.demographics.gender.male.toLocaleString() }} ({{ malePct }}%)
              </span>
            </div>

            <div class="flex items-center justify-between text-xs p-2 rounded-xl bg-rose-50/60 dark:bg-rose-950/30">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-rose-500"></span>
                <span class="text-slate-700 dark:text-slate-300 font-medium">Female</span>
              </div>
              <span class="font-bold text-rose-700 dark:text-rose-300">
                {{ analytics.demographics.gender.female.toLocaleString() }} ({{ femalePct }}%)
              </span>
            </div>
          </div>
        </div>

      </div>

      <!-- 3. Education & Schooling Tiers Breakdown -->
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div>
            <h3 class="font-bold text-slate-900 dark:text-slate-100 text-base flex items-center gap-2">
              <FeatherIcon name="book-open" class="w-4 h-4 text-teal-500" />
              <span>Educational Attainment & Schooling Stages</span>
            </h3>
            <p class="text-xs text-slate-500 mt-0.5">Enrolled student stages and literacy distribution</p>
          </div>
          
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 text-xs font-bold border border-teal-200/60 dark:border-teal-800">
              <FeatherIcon name="user-check" class="w-3.5 h-3.5" />
              <span>{{ analytics.demographics.studying_count.toLocaleString() }} Currently Studying</span>
            </span>
          </div>
        </div>

        <!-- Education Bracket Bars Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="b in (analytics.demographics.education_brackets || [])"
            :key="b.label"
            class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 flex flex-col justify-between space-y-3"
          >
            <div class="flex items-start justify-between gap-2">
              <span class="text-xs font-bold text-slate-800 dark:text-slate-200 leading-tight">{{ b.label }}</span>
              <span class="text-xs font-extrabold text-teal-600 dark:text-teal-400 whitespace-nowrap">
                {{ ((b.count / (analytics.kpis.total_population || 1)) * 100).toFixed(1) }}%
              </span>
            </div>
            
            <div>
              <div class="text-xl font-black text-slate-900 dark:text-slate-100">{{ b.count.toLocaleString() }}</div>
              <div class="text-[11px] text-slate-400 mt-0.5">individuals</div>
            </div>

            <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
              <div
                class="bg-teal-500 h-full rounded-full transition-all duration-700"
                :style="{ width: `${Math.max(((b.count / (analytics.kpis.total_population || 1)) * 100), 2)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. Housing, Living Conditions & Sanitation Indicators (Rich Actual Metrics) -->
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs">
        <div class="flex items-center justify-between mb-5">
          <div>
            <h3 class="font-bold text-slate-900 dark:text-slate-100 text-base flex items-center gap-2">
              <FeatherIcon name="home" class="w-4 h-4 text-emerald-500" />
              <span>Housing, Living Conditions & Sanitation</span>
            </h3>
            <p class="text-xs text-slate-500 mt-0.5">Household infrastructure, clean sanitation, and safety meters</p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Electricity -->
          <div class="p-4 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/40">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-amber-900 dark:text-amber-300 flex items-center gap-1.5">
                <FeatherIcon name="zap" class="w-4 h-4 text-amber-500" />
                <span>Electricity</span>
              </span>
              <span class="text-sm font-black text-amber-600 dark:text-amber-400">{{ analytics.kpis.electricity_pct }}%</span>
            </div>
            <div class="w-full bg-amber-200/60 dark:bg-amber-900/50 rounded-full h-2 overflow-hidden">
              <div class="bg-amber-500 h-full rounded-full" :style="{ width: `${analytics.kpis.electricity_pct}%` }"></div>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">Grid power connected households</p>
          </div>

          <!-- House Ownership -->
          <div class="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/40">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-blue-900 dark:text-blue-300 flex items-center gap-1.5">
                <FeatherIcon name="check-circle" class="w-4 h-4 text-blue-500" />
                <span>Own House</span>
              </span>
              <span class="text-sm font-black text-blue-600 dark:text-blue-400">{{ analytics.kpis.own_house_pct }}%</span>
            </div>
            <div class="w-full bg-blue-200/60 dark:bg-blue-900/50 rounded-full h-2 overflow-hidden">
              <div class="bg-blue-500 h-full rounded-full" :style="{ width: `${analytics.kpis.own_house_pct}%` }"></div>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">Self-owned premises</p>
          </div>

          <!-- Toilet Presence & Active Usage -->
          <div class="p-4 rounded-xl bg-teal-50/50 dark:bg-teal-950/20 border border-teal-100 dark:border-teal-900/40">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-teal-900 dark:text-teal-300 flex items-center gap-1.5">
                <FeatherIcon name="droplet" class="w-4 h-4 text-teal-500" />
                <span>Toilet Presence</span>
              </span>
              <span class="text-sm font-black text-teal-600 dark:text-teal-400">{{ analytics.kpis.toilet_present_pct }}%</span>
            </div>
            <div class="w-full bg-teal-200/60 dark:bg-teal-900/50 rounded-full h-2 overflow-hidden">
              <div class="bg-teal-500 h-full rounded-full" :style="{ width: `${analytics.kpis.toilet_present_pct}%` }"></div>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">Active usage: <strong>{{ analytics.kpis.toilet_usage_pct }}%</strong></p>
          </div>

          <!-- Separate Bathroom -->
          <div class="p-4 rounded-xl bg-cyan-50/50 dark:bg-cyan-950/20 border border-cyan-100 dark:border-cyan-900/40">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-cyan-900 dark:text-cyan-300 flex items-center gap-1.5">
                <FeatherIcon name="shield" class="w-4 h-4 text-cyan-500" />
                <span>Separate Bath</span>
              </span>
              <span class="text-sm font-black text-cyan-600 dark:text-cyan-400">{{ analytics.kpis.separate_bathroom_pct }}%</span>
            </div>
            <div class="w-full bg-cyan-200/60 dark:bg-cyan-900/50 rounded-full h-2 overflow-hidden">
              <div class="bg-cyan-500 h-full rounded-full" :style="{ width: `${analytics.kpis.separate_bathroom_pct}%` }"></div>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">Dedicated bathing facility</p>
          </div>

          <!-- Bednet Coverage -->
          <div class="p-4 rounded-xl bg-purple-50/50 dark:bg-purple-950/20 border border-purple-100 dark:border-purple-900/40">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-purple-900 dark:text-purple-300 flex items-center gap-1.5">
                <FeatherIcon name="sun" class="w-4 h-4 text-purple-500" />
                <span>Mosquito Bednet</span>
              </span>
              <span class="text-sm font-black text-purple-600 dark:text-purple-400">{{ analytics.kpis.bednet_available_pct }}%</span>
            </div>
            <div class="w-full bg-purple-200/60 dark:bg-purple-900/50 rounded-full h-2 overflow-hidden">
              <div class="bg-purple-500 h-full rounded-full" :style="{ width: `${analytics.kpis.bednet_available_pct}%` }"></div>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">Daily usage: <strong>{{ analytics.kpis.bednet_usage_pct }}%</strong></p>
          </div>

          <!-- Farm Well / Irrigation -->
          <div class="p-4 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-emerald-900 dark:text-emerald-300 flex items-center gap-1.5">
                <FeatherIcon name="filter" class="w-4 h-4 text-emerald-500" />
                <span>Farm Wells</span>
              </span>
              <span class="text-sm font-black text-emerald-600 dark:text-emerald-400">{{ analytics.kpis.well_in_farm_pct }}%</span>
            </div>
            <div class="w-full bg-emerald-200/60 dark:bg-emerald-900/50 rounded-full h-2 overflow-hidden">
              <div class="bg-emerald-500 h-full rounded-full" :style="{ width: `${analytics.kpis.well_in_farm_pct}%` }"></div>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">Irrigation well inside farm</p>
          </div>

          <!-- Attached Cowshed -->
          <div class="p-4 rounded-xl bg-orange-50/50 dark:bg-orange-950/20 border border-orange-100 dark:border-orange-900/40">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-orange-900 dark:text-orange-300 flex items-center gap-1.5">
                <FeatherIcon name="grid" class="w-4 h-4 text-orange-500" />
                <span>Cowshed Present</span>
              </span>
              <span class="text-sm font-black text-orange-600 dark:text-orange-400">{{ analytics.kpis.cowshed_pct }}%</span>
            </div>
            <div class="w-full bg-orange-200/60 dark:bg-orange-900/50 rounded-full h-2 overflow-hidden">
              <div class="bg-orange-500 h-full rounded-full" :style="{ width: `${analytics.kpis.cowshed_pct}%` }"></div>
            </div>
            <p class="text-[11px] text-slate-500 mt-2">Cattle shed present on property</p>
          </div>

          <!-- Total Farm Land -->
          <div class="p-4 rounded-xl bg-slate-100/70 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                <FeatherIcon name="map" class="w-4 h-4 text-slate-500" />
                <span>Cultivated Land</span>
              </span>
              <span class="text-sm font-black text-slate-800 dark:text-slate-100">
                {{ (analytics.kpis.total_wet_land_acres + analytics.kpis.total_dry_land_acres).toFixed(0) }} Ac
              </span>
            </div>
            <p class="text-[11px] text-slate-500 mt-3">
              Wet: <strong>{{ analytics.kpis.total_wet_land_acres }} Ac</strong> | Dry: <strong>{{ analytics.kpis.total_dry_land_acres }} Ac</strong>
            </p>
          </div>
        </div>
      </div>

      <!-- 5. Dedicated Cards: Livestock Assets + Health & Social Security + Community Profile -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Card A: Livestock & Cattle Assets (Simpler Direct Display) -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-slate-900 dark:text-slate-100 text-base flex items-center gap-2">
                <span class="text-lg">🐂</span>
                <span>Livestock & Cattle Assets</span>
              </h3>
              <span class="text-xs bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 px-2.5 py-0.5 rounded-full font-semibold">
                {{ totalLivestockCount.toLocaleString() }} Animals
              </span>
            </div>

            <!-- Livestock Simple Cards Grid -->
            <div class="grid grid-cols-2 gap-3">
              <div
                v-for="ls in formattedLivestockList"
                :key="ls.code"
                class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 flex items-center justify-between"
              >
                <div class="flex items-center gap-2">
                  <span class="text-lg">{{ ls.emoji }}</span>
                  <span class="text-xs font-semibold text-slate-700 dark:text-slate-300">{{ ls.cleanLabel }}</span>
                </div>
                <span class="text-sm font-black text-slate-900 dark:text-slate-100">{{ ls.count.toLocaleString() }}</span>
              </div>
            </div>

            <div v-if="!analytics.welfare_and_social.livestock?.length" class="text-xs text-slate-400 py-6 text-center">
              No livestock records
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500">
            Vital economic & agricultural assets across tribal farming families.
          </div>
        </div>

        <!-- Card B: Health & Social Security Schemes (Simple Coverage Cards) -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-slate-900 dark:text-slate-100 text-base flex items-center gap-2">
                <FeatherIcon name="shield" class="w-4 h-4 text-emerald-500" />
                <span>Health & Welfare Schemes</span>
              </h3>
              <span class="text-xs text-slate-500">Coverage</span>
            </div>

            <div class="space-y-3.5">
              <!-- Ayushman Bharat -->
              <div class="p-3.5 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-100 dark:border-emerald-900/40">
                <div class="flex items-center justify-between text-xs font-bold text-emerald-900 dark:text-emerald-300 mb-1.5">
                  <span>Ayushman Bharat / PM-JAY</span>
                  <span class="text-sm font-black">{{ ayushmanPct }}%</span>
                </div>
                <div class="w-full bg-emerald-200/60 dark:bg-emerald-900/50 rounded-full h-2 overflow-hidden mb-1.5">
                  <div class="bg-emerald-500 h-full rounded-full" :style="{ width: `${ayushmanPct}%` }"></div>
                </div>
                <div class="text-[11px] text-emerald-700 dark:text-emerald-400">
                  <strong>{{ ayushmanCount.toLocaleString() }}</strong> households enrolled
                </div>
              </div>

              <!-- Ration Cards Distribution -->
              <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 space-y-2">
                <div class="text-xs font-bold text-slate-700 dark:text-slate-300">PDS Ration Card Entitlement</div>
                <div class="space-y-1.5">
                  <div v-for="rc in (analytics.welfare_and_social.ration_cards || [])" :key="rc.code" class="flex items-center justify-between text-xs">
                    <span class="text-slate-600 dark:text-slate-400">{{ rc.label }} Card</span>
                    <span class="font-bold text-slate-800 dark:text-slate-200">{{ rc.count }} HH ({{ rc.pct }}%)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500">
            Universal health coverage & subsidized food safety net enrollment.
          </div>
        </div>

        <!-- Card C: Caste & Tribal Communities Profile -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-slate-900 dark:text-slate-100 text-base flex items-center gap-2">
                <FeatherIcon name="users" class="w-4 h-4 text-amber-500" />
                <span>Community & Tribal Profile</span>
              </h3>
              <span class="text-xs text-slate-500">Family Heads</span>
            </div>

            <!-- Top Castes / Tribes List -->
            <div class="space-y-2.5 max-h-[220px] overflow-y-auto pr-1">
              <div
                v-for="c in (analytics.welfare_and_social.caste || []).slice(0, 6)"
                :key="c.label"
                class="space-y-1"
              >
                <div class="flex justify-between text-xs font-medium">
                  <span class="text-slate-800 dark:text-slate-200 font-semibold truncate">{{ c.label }}</span>
                  <span class="text-slate-900 dark:text-slate-100 font-bold">
                    {{ c.count }} ({{ ((c.count / (analytics.kpis.total_households || 1)) * 100).toFixed(0) }}%)
                  </span>
                </div>
                <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    class="bg-amber-500 h-full rounded-full transition-all duration-500"
                    :style="{ width: `${((c.count / (analytics.kpis.total_households || 1)) * 100)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500">
            Dhanora taluka is predominantly home to Gond, Madiya, and related tribal lineages.
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  selectedVillage: { type: String, default: 'ALL' },
  villages: { type: Array, default: () => [] },
  analytics: { type: Object, default: () => null },
  loading: { type: Boolean, default: false }
})

defineEmits(['update:selectedVillage', 'refresh'])

const selectedVillageMarathi = computed(() => {
  if (!props.selectedVillage || props.selectedVillage === 'ALL') return ''
  const v = props.villages.find(x => x.village_name === props.selectedVillage)
  return v ? v.village_name_marathi : ''
})

// Age Cohort List with Bar Gradients & Styling
const ageCohortList = computed(() => {
  if (!props.analytics?.demographics?.age_cohorts) return []
  const total = props.analytics.kpis.total_population || 1
  const c = props.analytics.demographics.age_cohorts

  return [
    { 
      key: 'u5', 
      label: '0 – 5 Years (Infants & Early Childhood)', 
      count: c.u5 || 0, 
      pct: (((c.u5 || 0) / total) * 100).toFixed(1), 
      dotClass: 'bg-amber-500',
      barGradient: 'bg-gradient-to-r from-amber-400 to-amber-500'
    },
    { 
      key: 'school', 
      label: '6 – 18 Years (School-Age Children & Teens)', 
      count: c.school || 0, 
      pct: (((c.school || 0) / total) * 100).toFixed(1), 
      dotClass: 'bg-teal-500',
      barGradient: 'bg-gradient-to-r from-teal-400 to-teal-500'
    },
    { 
      key: 'youth', 
      label: '19 – 35 Years (Youth & Young Adults)', 
      count: c.youth || 0, 
      pct: (((c.youth || 0) / total) * 100).toFixed(1), 
      dotClass: 'bg-indigo-500',
      barGradient: 'bg-gradient-to-r from-indigo-400 to-indigo-500'
    },
    { 
      key: 'middle', 
      label: '36 – 60 Years (Middle-Age Working Adults)', 
      count: c.middle || 0, 
      pct: (((c.middle || 0) / total) * 100).toFixed(1), 
      dotClass: 'bg-blue-500',
      barGradient: 'bg-gradient-to-r from-blue-400 to-blue-500'
    },
    { 
      key: 'senior', 
      label: '60+ Years (Elderly / Senior Citizens)', 
      count: c.senior || 0, 
      pct: (((c.senior || 0) / total) * 100).toFixed(1), 
      dotClass: 'bg-purple-500',
      barGradient: 'bg-gradient-to-r from-purple-400 to-purple-500'
    }
  ]
})

// Gender Donut Chart Calculations (Circumference ~ 238.76 for r=38)
const totalPop = computed(() => props.analytics?.kpis?.total_population || 1)
const maleCount = computed(() => props.analytics?.demographics?.gender?.male || 0)
const femaleCount = computed(() => props.analytics?.demographics?.gender?.female || 0)

const malePct = computed(() => ((maleCount.value / totalPop.value) * 100).toFixed(1))
const femalePct = computed(() => ((femaleCount.value / totalPop.value) * 100).toFixed(1))

const maleCircleLength = computed(() => {
  const circ = 2 * Math.PI * 38
  return ((maleCount.value / totalPop.value) * circ).toFixed(1)
})

const femaleCircleLength = computed(() => {
  const circ = 2 * Math.PI * 38
  return ((femaleCount.value / totalPop.value) * circ).toFixed(1)
})

// Livestock Formatter & Emojis
const emojiMap = {
  '1': '🐄', // Cow
  '2': '🐂', // Bullock
  '3': '🐃', // Buffalo
  '4': '🐂', // Bull
  '5': '🐐', // Goat
  '6': '🐔', // Chicken
  '7': '🐕', // Dog
  '8': '🐖'  // Pig
}

const formattedLivestockList = computed(() => {
  const list = props.analytics?.welfare_and_social?.livestock || []
  return list.map(item => {
    let clean = item.label || `Animal #${item.code}`
    clean = clean.split('(')[0].trim()
    return {
      ...item,
      cleanLabel: clean,
      emoji: emojiMap[item.code] || '🐾'
    }
  })
})

const totalLivestockCount = computed(() => {
  const list = props.analytics?.welfare_and_social?.livestock || []
  return list.reduce((acc, curr) => acc + (Number(curr.count) || 0), 0)
})

// Health Schemes
const ayushmanScheme = computed(() => {
  const list = props.analytics?.welfare_and_social?.health_schemes || []
  return list.find(s => s.code === '1' || (s.label || '').toLowerCase().includes('ayush')) || {}
})

const ayushmanCount = computed(() => ayushmanScheme.value.count || 0)
const ayushmanPct = computed(() => ayushmanScheme.value.pct || 0)
</script>

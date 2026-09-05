<template>
  <div class="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
    
    <!-- Top Action Bar -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white dark:bg-slate-900 p-5 sm:px-6 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs">
      <div class="flex items-center gap-3">
        <router-link
          to="/mmu"
          class="inline-flex items-center flex-row gap-1.5 whitespace-nowrap px-3 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors text-sm font-semibold cursor-pointer"
        >
          <FeatherIcon name="arrow-left" class="w-4 h-4 shrink-0" />
          <span>Visits List</span>
        </router-link>
        <div class="h-5 w-px bg-slate-200 dark:bg-slate-700 hidden sm:block"></div>
        <div>
          <h1 class="text-lg font-bold text-slate-900 dark:text-slate-100 leading-tight">
            {{ isEditMode ? 'Edit MMU Visit: ' + editId : 'New MMU Patient Encounter' }}
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400">Dhanora Taluka Mobile Medical Unit Form</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2.5">
        <button
          v-if="isEditMode && canDelete"
          @click="deleteRecord"
          type="button"
          :disabled="saving"
          class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-3.5 py-2 text-sm font-semibold text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-xl transition-colors cursor-pointer"
        >
          <FeatherIcon name="trash-2" class="w-4 h-4 shrink-0" />
          <span>Delete</span>
        </button>

        <button
          @click="resetForm"
          type="button"
          :disabled="saving"
          class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-3.5 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 rounded-xl transition-colors cursor-pointer"
        >
          <span>Reset</span>
        </button>

        <button
          @click="saveRecord"
          type="button"
          :disabled="saving"
          class="inline-flex items-center justify-center flex-row gap-1.5 whitespace-nowrap px-4 py-2 text-sm font-semibold text-white bg-rose-600 hover:bg-rose-700 active:bg-rose-800 rounded-xl shadow-xs transition-colors cursor-pointer disabled:opacity-50"
        >
          <div v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin shrink-0"></div>
          <FeatherIcon v-else name="check" class="w-4 h-4 shrink-0" />
          <span>{{ isEditMode ? 'Update Record' : 'Save Record' }}</span>
        </button>
      </div>
    </div>

    <!-- Alert Banner if notification -->
    <div v-if="feedbackMsg" :class="feedbackError ? 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300' : 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300'" class="p-4 rounded-xl border text-sm flex items-center justify-between font-medium">
      <span>{{ feedbackMsg }}</span>
      <button @click="feedbackMsg = ''" class="font-bold text-base cursor-pointer">×</button>
    </div>

    <!-- Main Form -->
    <div class="space-y-6">
      
      <!-- Section 1: Encounter & Patient Demographics -->
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-7 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-6">
        <div class="flex items-center gap-2.5 pb-3.5 border-b border-slate-100 dark:border-slate-800">
          <div class="w-8 h-8 rounded-xl bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0">
            <FeatherIcon name="user" class="w-4 h-4" />
          </div>
          <h2 class="text-base font-bold text-slate-900 dark:text-slate-100">1. Encounter & Patient Identification</h2>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
          
          <!-- Date of Visit -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Date of Visit *</label>
            <input
              type="date"
              v-model="form.date_of_visit"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              required
            />
          </div>

          <!-- Patient Unique ID -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Patient Unique ID *</label>
            <div class="flex items-center gap-2">
              <input
                type="text"
                v-model="form.patient_unique_id"
                @blur="onPatientIdBlur"
                placeholder="e.g. KEH/01, DUR/03"
                class="flex-1 px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                required
              />
              <button
                type="button"
                @click="generatePatientId(true)"
                class="px-3 py-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 rounded-xl transition-colors shrink-0"
                title="Auto-generate next ID based on Village"
              >
                <FeatherIcon name="zap" class="w-3.5 h-3.5 inline mr-1" />
                Auto ID
              </button>
            </div>
          </div>

          <!-- Patient Name -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Patient Full Name *</label>
            <input
              type="text"
              v-model="form.patient_name"
              placeholder="Patient Name"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              required
            />
          </div>

          <!-- Patient Sex -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Patient Sex</label>
            <select
              v-model="form.patient_sex"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select Sex</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <!-- Area Name -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Area Name</label>
            <select
              v-model="form.area_name"
              @change="onAreaChange"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select Area</option>
              <option v-for="a in masterData.areas || []" :key="a.code" :value="a.name">
                {{ a.name }}
              </option>
            </select>
          </div>

          <!-- Village Name -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Village Name (Village Profile)</label>
            <select
              v-model="form.village_name"
              @change="onVillageChange"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select Village (Village Profile)</option>
              <option v-for="v in availableVillages" :key="v.name" :value="v.name">
                {{ v.displayName || v.name }}
              </option>
            </select>
          </div>

        </div>

        <!-- Age Breakdown -->
        <div class="p-4 sm:p-5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700">
          <div class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-3.5 flex items-center justify-between">
            <span>Age Breakdown & Automatic Calculation</span>
            <span class="text-rose-600 dark:text-rose-400 font-extrabold text-sm">Total Age: {{ form.total_age }} yrs</span>
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Age (Years)</label>
              <input
                type="number"
                min="0"
                v-model.number="form.age_years"
                @input="calculateTotalAge"
                class="w-full px-3 py-2 text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Age (Months)</label>
              <input
                type="number"
                min="0"
                max="11"
                v-model.number="form.age_months"
                @input="calculateTotalAge"
                class="w-full px-3 py-2 text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Age (Days)</label>
              <input
                type="number"
                min="0"
                max="30"
                v-model.number="form.age_days"
                @input="calculateTotalAge"
                class="w-full px-3 py-2 text-sm rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Section: Census Matching (Citizen Linkage) -->
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-7 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-5">
        <div class="flex items-center justify-between pb-3.5 border-b border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400 flex items-center justify-center shrink-0">
              <FeatherIcon name="users" class="w-4 h-4" />
            </div>
            <div>
              <h2 class="text-base font-bold text-slate-900 dark:text-slate-100">Census Citizen Linkage</h2>
              <p class="text-xs text-slate-500">Cross-reference patient with Household Census database</p>
            </div>
          </div>

          <!-- Match Status Badge -->
          <div class="flex items-center gap-2">
            <span
              :class="{
                'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800': form.match_status === 'Auto-Matched' || form.match_status === 'Manually Verified',
                'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800': form.match_status === 'Multiple Matches',
                'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700': !form.match_status || form.match_status === 'Unmatched'
              }"
              class="px-3 py-1 text-xs font-semibold rounded-full border"
            >
              {{ form.match_status || 'Unmatched' }}
            </span>
          </div>
        </div>

        <!-- Matched details display or search prompt -->
        <div v-if="form.census_match" class="p-4 rounded-xl bg-violet-50/50 dark:bg-violet-950/30 border border-violet-200 dark:border-violet-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="space-y-1 text-sm">
            <div class="font-bold text-violet-900 dark:text-violet-200">
              Citizen: {{ form.matched_member_name }} ({{ form.matched_member_age }} yrs)
            </div>
            <div class="text-xs text-violet-700 dark:text-violet-400">
              Household ID: <span class="font-semibold">{{ form.census_match }}</span> | Confidence: <span class="font-bold">{{ form.match_confidence }}%</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              @click="searchCensusMatches"
              class="px-3 py-1.5 text-xs font-semibold text-violet-700 dark:text-violet-300 bg-white dark:bg-slate-800 border border-violet-300 dark:border-violet-700 rounded-lg hover:bg-violet-50 transition-colors"
            >
              Change Match
            </button>
            <button
              type="button"
              @click="clearCensusMatch"
              class="px-3 py-1.5 text-xs font-semibold text-rose-600 hover:text-rose-700 bg-white dark:bg-slate-800 border border-rose-200 rounded-lg transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        <div v-else class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700">
          <div class="text-sm text-slate-600 dark:text-slate-400">
            No census household linked yet. Auto-match runs on save, or search candidate citizens manually.
          </div>
          <button
            type="button"
            @click="searchCensusMatches"
            :disabled="!form.patient_name"
            class="inline-flex items-center justify-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-violet-700 dark:text-violet-300 bg-violet-50 dark:bg-violet-950/60 hover:bg-violet-100 border border-violet-200 dark:border-violet-800 rounded-xl transition-colors shrink-0 disabled:opacity-50"
          >
            <FeatherIcon name="search" class="w-3.5 h-3.5" />
            <span>Find Census Matches</span>
          </button>
        </div>

      </div>

      <!-- Section 2: Clinical Diagnoses -->
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-7 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-6">
        <div class="flex items-center gap-2.5 pb-3.5 border-b border-slate-100 dark:border-slate-800">
          <div class="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
            <FeatherIcon name="activity" class="w-4 h-4" />
          </div>
          <h2 class="text-base font-bold text-slate-900 dark:text-slate-100">2. Clinical Diagnoses (Codes 1 - 225)</h2>
        </div>

        <!-- Clinical Diagnoses (1 to 6) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
          
          <!-- Diagnosis 1 -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Diagnosis 1</label>
            <input
              type="text"
              list="diag-list"
              v-model="form.diagnosis_1"
              placeholder="Search or select diagnosis..."
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

          <!-- Diagnosis 2 -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Diagnosis 2</label>
            <input
              type="text"
              list="diag-list"
              v-model="form.diagnosis_2"
              placeholder="Search or select diagnosis..."
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

          <!-- Diagnosis 3 -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Diagnosis 3</label>
            <input
              type="text"
              list="diag-list"
              v-model="form.diagnosis_3"
              placeholder="Search or select diagnosis..."
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

          <!-- Diagnosis 4 -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Diagnosis 4</label>
            <input
              type="text"
              list="diag-list"
              v-model="form.diagnosis_4"
              placeholder="Search or select diagnosis..."
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

          <!-- Diagnosis 5 -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Diagnosis 5</label>
            <input
              type="text"
              list="diag-list"
              v-model="form.diagnosis_5"
              placeholder="Search or select diagnosis..."
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

          <!-- Diagnosis 6 -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Diagnosis 6</label>
            <input
              type="text"
              list="diag-list"
              v-model="form.diagnosis_6"
              placeholder="Search or select diagnosis..."
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

        </div>

        <!-- Dental Diagnoses (1 & 2) -->
        <div class="pt-4 border-t border-slate-100 dark:border-slate-800">
          <h3 class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">Dental Diagnoses (Codes &ge; 226)</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <!-- Dental Diagnosis 1 -->
            <div>
              <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Dental Diagnosis 1</label>
              <input
                type="text"
                list="dental-list"
                v-model="form.dental_diagnosis"
                placeholder="Search dental diagnosis 1..."
                class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>

            <!-- Dental Diagnosis 2 -->
            <div>
              <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Dental Diagnosis 2</label>
              <input
                type="text"
                list="dental-list"
                v-model="form.dental_diagnosis_2"
                placeholder="Search dental diagnosis 2..."
                class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              />
            </div>
          </div>
        </div>

        <!-- Datalists for instant native searchable dropdowns -->
        <datalist id="diag-list">
          <option v-for="d in masterData.diagnoses || []" :key="d.code" :value="d.name" />
        </datalist>

        <datalist id="dental-list">
          <option v-for="d in dentalDiagnoses" :key="d.code" :value="d.name" />
        </datalist>

      </div>

      <!-- Section 3: Follow-Up & Referral -->
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-7 border border-slate-200/80 dark:border-slate-800 shadow-xs space-y-6">
        <div class="flex items-center gap-2.5 pb-3.5 border-b border-slate-100 dark:border-slate-800">
          <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
            <FeatherIcon name="check-circle" class="w-4 h-4" />
          </div>
          <h2 class="text-base font-bold text-slate-900 dark:text-slate-100">3. Follow-up Status & Secondary Care Referral</h2>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
          
          <!-- Newly Diagnosed -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Patient Newly Diagnosed?</label>
            <select
              v-model="form.patient_newly_diag"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
            </select>
          </div>

          <!-- Follow-up: Hypertension -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Follow-up: Hypertension</label>
            <select
              v-model="form.followup_hypertension"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="NO">NO</option>
            </select>
          </div>

          <!-- Follow-up: Diabetes -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Follow-up: Diabetes</label>
            <select
              v-model="form.followup_diabetes"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="NO">NO</option>
            </select>
          </div>

          <!-- Follow-up: Chronic Disease -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Follow-up: Chronic Disease</label>
            <select
              v-model="form.followup_chronic_disease"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="NO">NO</option>
            </select>
          </div>

        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-5 pt-2">
          
          <!-- Patient Referred -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Patient Referred To</label>
            <select
              v-model="form.patient_referred"
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select Facility</option>
              <option v-for="opt in masterData.referral_options || defaultReferrals" :key="opt" :value="opt">
                {{ opt }}
              </option>
            </select>
          </div>

          <!-- Patient Referred by Doctor -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Patient Referred by Doctor</label>
            <input
              type="text"
              v-model="form.patient_referred_by_doctor"
              placeholder="Enter Doctor name..."
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

          <!-- Patient Referred Where -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Referred Facility Details / Notes</label>
            <input
              type="text"
              v-model="form.patient_referred_where"
              placeholder="e.g. SEARCH Hospital OPD, Wardha Civil..."
              class="w-full px-3.5 py-2.5 text-sm rounded-xl border border-slate-300 dark:border-slate-700 focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 outline-hidden bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            />
          </div>

        </div>

      </div>

    </div>

    <!-- Census Candidates Modal Dialog -->
    <div v-if="showCensusModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div class="bg-white dark:bg-slate-900 w-full max-w-2xl rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[85vh]">
        <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div>
            <h3 class="text-base font-bold text-slate-900 dark:text-slate-100">Census Household Candidates</h3>
            <p class="text-xs text-slate-500">Matching patient details against village census</p>
          </div>
          <button @click="showCensusModal = false" class="text-slate-400 hover:text-slate-600 text-lg font-bold">×</button>
        </div>

        <div class="p-6 overflow-y-auto space-y-3">
          <div v-if="censusSearching" class="py-8 text-center text-sm text-slate-500">
            <div class="w-6 h-6 border-2 border-rose-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            Searching census records...
          </div>

          <div v-else-if="censusCandidates.length === 0" class="py-8 text-center text-sm text-slate-500">
            No matching citizens found in census for this name and village.
          </div>

          <div
            v-else
            v-for="c in censusCandidates"
            :key="c.household + c.member_name"
            class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-violet-300 dark:hover:border-violet-700 bg-white dark:bg-slate-850 flex items-center justify-between gap-4 transition-colors"
          >
            <div class="space-y-1">
              <div class="font-bold text-slate-900 dark:text-slate-100 text-sm">
                {{ c.member_name }} <span v-if="c.member_name_marathi" class="text-slate-500 font-normal">({{ c.member_name_marathi }})</span>
              </div>
              <div class="text-xs text-slate-500 space-x-2">
                <span>Age: <b>{{ c.age }}</b></span>
                <span>•</span>
                <span>Gender: <b>{{ c.gender }}</b></span>
                <span>•</span>
                <span>Rel: <b>{{ c.relation }}</b></span>
                <span>•</span>
                <span>Household: <b>{{ c.household }}</b></span>
              </div>
            </div>

            <div class="flex items-center gap-3 shrink-0">
              <div class="text-right">
                <span class="px-2 py-1 text-xs font-bold rounded-lg bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200">
                  {{ c.confidence }}% match
                </span>
              </div>
              <button
                type="button"
                @click="confirmCensusMatch(c)"
                class="px-3 py-1.5 text-xs font-semibold text-white bg-violet-600 hover:bg-violet-700 rounded-xl transition-colors"
              >
                Select
              </button>
            </div>
          </div>
        </div>

        <div class="px-6 py-3 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-800 flex justify-end">
          <button
            type="button"
            @click="showCensusModal = false"
            class="px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'MMUForm',
  components: {
    FeatherIcon,
  },
  data() {
    return {
      saving: false,
      feedbackMsg: '',
      feedbackError: false,
      showCensusModal: false,
      censusSearching: false,
      censusCandidates: [],
      masterData: {
        areas: [],
        villages: {},
        village_prefixes: {},
        diagnoses: [],
        medicines: [],
        referral_options: [],
      },
      defaultReferrals: [
        'No', 'Not Applicable', 'SEARCH', 'Govt. Hospital Gadchiroli',
        'Other Govt. Hospital', 'Private Gadchiroli hospital',
        'Other Private Hospital', 'SEARCH Surgery'
      ],
      form: {
        date_of_visit: new Date().toISOString().split('T')[0],
        patient_unique_id: '',
        patient_name: '',
        patient_sex: '',
        area_name: '',
        area_code: 0,
        village_name: '',
        village_code: 0,
        age_years: 0,
        age_months: 0,
        age_days: 0,
        total_age: 0.0,
        diagnosis_1: '',
        diag_code_1: 0,
        diagnosis_2: '',
        diag_code_2: 0,
        diagnosis_3: '',
        diag_code_3: 0,
        diagnosis_4: '',
        diag_code_4: 0,
        diagnosis_5: '',
        diag_code_5: 0,
        diagnosis_6: '',
        diag_code_6: 0,
        dental_diagnosis: '',
        diag_code_dental_1: 0,
        dental_diagnosis_2: '',
        diag_code_dental_2: 0,
        patient_newly_diag: '',
        followup_hypertension: '',
        followup_diabetes: '',
        followup_chronic_disease: '',
        patient_referred: 'No',
        patient_referred_where: '',
        patient_referred_by_doctor: '',
        census_match: null,
        matched_member_name: '',
        matched_member_age: 0,
        match_confidence: 0.0,
        match_status: 'Unmatched',
      },
    }
  },
  computed: {
    isEditMode() {
      return Boolean(this.$route.params.id)
    },
    editId() {
      return this.$route.params.id || ''
    },
    availableVillages() {
      const profiles = this.masterData.village_profiles || []
      if (profiles.length > 0) {
        let list = profiles
        if (this.form.area_name) {
          const areaNorm = this.form.area_name.toLowerCase().replace('_', ' ')
          const filtered = profiles.filter(p => {
            const taluka = (p.taluka || '').toLowerCase()
            return taluka && (areaNorm.includes(taluka) || taluka.includes(areaNorm))
          })
          if (filtered.length > 0) {
            list = filtered
          }
        }
        return list.map(p => ({
          name: p.name,
          code: p.village_number || 0,
          displayName: p.village_name_marathi ? `${p.name} (${p.village_name_marathi})` : p.name,
          marathi: p.village_name_marathi,
          taluka: p.taluka
        }))
      }

      if (!this.form.area_name || !this.masterData.villages) return []
      const area = (this.masterData.areas || []).find(a => a.name === this.form.area_name)
      if (!area) return []
      return (this.masterData.villages[String(area.code)] || []).map(v => ({
        name: v.name,
        code: v.code,
        displayName: v.name
      }))
    },
    dentalDiagnoses() {
      return (this.masterData.diagnoses || []).filter(d => d.code >= 226)
    },
    canDelete() {
      return Boolean(this.masterData?.can_delete)
    },
  },
  created() {
    this.fetchMasterData()
    if (this.isEditMode) {
      this.fetchRecord(this.editId)
    }
  },
  methods: {
    async fetchMasterData() {
      try {
        const res = await fetch('/api/method/mmu.mmu.doctype.mmu_patient_record.mmu_patient_record.get_master_data')
        const data = await res.json()
        if (data.message) {
          this.masterData = data.message
        }
      } catch (e) {
        console.error('Failed to load MMU master data', e)
      }
    },
    async fetchRecord(id) {
      try {
        const res = await fetch(`/api/method/mmu.mmu.doctype.mmu_patient_record.mmu_patient_record.get_record_details?record_name=${encodeURIComponent(id)}`)
        const data = await res.json()
        if (data.message && !data.message.error) {
          Object.assign(this.form, data.message)
        }
      } catch (e) {
        this.feedbackMsg = 'Failed to load record: ' + e.message
        this.feedbackError = true
      }
    },
    onAreaChange() {
      const area = (this.masterData.areas || []).find(a => a.name === this.form.area_name)
      this.form.area_code = area ? area.code : 0
    },
    onVillageChange() {
      if (this.form.village_name) {
        const matched = this.availableVillages.find(v => v.name === this.form.village_name)
        if (matched && matched.code) {
          this.form.village_code = matched.code
        }
      }
      if (!this.isEditMode) {
        const currentId = (this.form.patient_unique_id || '').trim()
        if (!currentId || currentId.includes('/')) {
          this.generatePatientId(false)
        }
      }
    },
    async generatePatientId(force = false) {
      const villageCode = Number(this.form.village_code) || 0
      const villageName = this.form.village_name || ''
      if (!villageCode && !villageName) {
        if (force) alert('Please select a Village first.')
        return
      }

      try {
        const url = `/api/method/mmu.mmu.doctype.mmu_patient_record.mmu_patient_record.get_next_patient_id?village_code=${villageCode}&village_name=${encodeURIComponent(villageName)}`
        const res = await fetch(url)
        const data = await res.json()
        if (data.message && data.message.next_id) {
          this.form.patient_unique_id = data.message.next_id
        }
      } catch (e) {
        console.error('Failed to generate patient ID', e)
      }
    },
    calculateTotalAge() {
      const y = Number(this.form.age_years) || 0
      const m = Number(this.form.age_months) || 0
      const d = Number(this.form.age_days) || 0
      const total = y + (m / 12.0) + (d / 365.25)
      this.form.total_age = Number(total.toFixed(2))
    },
    async searchCensusMatches() {
      if (!this.form.patient_name) {
        alert('Please enter Patient Name first.')
        return
      }
      this.showCensusModal = true
      this.censusSearching = true
      this.censusCandidates = []
      try {
        const params = new URLSearchParams({
          patient_name: this.form.patient_name,
          village_code: String(this.form.village_code || 0),
          village_name: this.form.village_name || '',
          patient_sex: this.form.patient_sex || '',
          age_years: String(this.form.age_years || 0),
          total_age: String(this.form.total_age || 0),
        })
        const res = await fetch(`/api/method/mmu.mmu.doctype.mmu_patient_record.mmu_patient_record.search_census_matches?${params.toString()}`)
        const data = await res.json()
        this.censusCandidates = data.message || []
      } catch (e) {
        console.error('Census search failed', e)
      } finally {
        this.censusSearching = false
      }
    },
    confirmCensusMatch(c) {
      this.form.census_match = c.household
      this.form.matched_member_name = c.member_name
      this.form.matched_member_age = c.age
      this.form.match_confidence = c.confidence
      this.form.match_status = 'Manually Verified'
      this.showCensusModal = false
      this.feedbackMsg = `Census match linked: ${c.member_name} (${c.household})`
      this.feedbackError = false
    },
    clearCensusMatch() {
      this.form.census_match = null
      this.form.matched_member_name = ''
      this.form.matched_member_age = 0
      this.form.match_confidence = 0.0
      this.form.match_status = 'Unmatched'
    },
    async lookupPatient() {
      if (!this.form.patient_unique_id) return
      try {
        const url = `/api/method/mmu.mmu.doctype.mmu_patient_record.mmu_patient_record.get_patient_details?patient_id=${encodeURIComponent(this.form.patient_unique_id)}&date_of_visit=${encodeURIComponent(this.form.date_of_visit)}`
        const res = await fetch(url)
        const data = await res.json()
        if (data.message && !data.message.error) {
          const p = data.message
          if (p.patient_name) this.form.patient_name = p.patient_name
          if (p.patient_sex) this.form.patient_sex = p.patient_sex
          if (p.village_name) this.form.village_name = p.village_name
          if (p.area_name) this.form.area_name = p.area_name
          if (p.age_years !== undefined) this.form.age_years = p.age_years
          if (p.age_months !== undefined) this.form.age_months = p.age_months
          if (p.age_days !== undefined) this.form.age_days = p.age_days
          if (p.total_age !== undefined) this.form.total_age = p.total_age
          this.feedbackMsg = 'Patient record linked successfully.'
          this.feedbackError = false
        }
      } catch (e) {
        console.warn('Patient lookup fallback active', e)
      }
    },
    onPatientIdBlur() {
      if (this.form.patient_unique_id && !this.form.patient_name) {
        this.lookupPatient()
      }
    },
    resolveDiagnosisCodes() {
      const diagMap = {}
      ;(this.masterData.diagnoses || []).forEach(d => {
        diagMap[d.name.toLowerCase()] = d.code
      })

      if (this.form.diagnosis_1) {
        this.form.diag_code_1 = diagMap[this.form.diagnosis_1.toLowerCase()] || 0
      }
      if (this.form.diagnosis_2) {
        this.form.diag_code_2 = diagMap[this.form.diagnosis_2.toLowerCase()] || 0
      }
      if (this.form.diagnosis_3) {
        this.form.diag_code_3 = diagMap[this.form.diagnosis_3.toLowerCase()] || 0
      }
      if (this.form.diagnosis_4) {
        this.form.diag_code_4 = diagMap[this.form.diagnosis_4.toLowerCase()] || 0
      }
      if (this.form.diagnosis_5) {
        this.form.diag_code_5 = diagMap[this.form.diagnosis_5.toLowerCase()] || 0
      }
      if (this.form.diagnosis_6) {
        this.form.diag_code_6 = diagMap[this.form.diagnosis_6.toLowerCase()] || 0
      }
      if (this.form.dental_diagnosis) {
        this.form.diag_code_dental_1 = diagMap[this.form.dental_diagnosis.toLowerCase()] || 0
      }
      if (this.form.dental_diagnosis_2) {
        this.form.diag_code_dental_2 = diagMap[this.form.dental_diagnosis_2.toLowerCase()] || 0
      }

      if (this.form.village_name && this.form.area_name) {
        const area = (this.masterData.areas || []).find(a => a.name === this.form.area_name)
        if (area) {
          const vList = this.masterData.villages[String(area.code)] || []
          const vObj = vList.find(v => v.name === this.form.village_name)
          if (vObj) this.form.village_code = vObj.code
        }
      }
    },
    async saveRecord() {
      if (!this.form.patient_unique_id || !this.form.patient_name || !this.form.date_of_visit) {
        this.feedbackMsg = 'Please complete required fields: Date of Visit, Patient ID, and Patient Name.'
        this.feedbackError = true
        return
      }

      this.saving = true
      this.feedbackMsg = ''
      this.feedbackError = false
      this.resolveDiagnosisCodes()

      try {
        const csrf = window.csrf_token || (document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || ''
        const payload = {
          ...this.form,
          name: this.isEditMode ? this.editId : undefined,
        }

        const res = await fetch('/api/method/mmu.mmu.doctype.mmu_patient_record.mmu_patient_record.save_patient_record', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Frappe-CSRF-Token': csrf,
          },
          body: JSON.stringify({ data: JSON.stringify(payload) }),
        })

        const data = await res.json()
        if (res.ok && !data.exc) {
          this.feedbackMsg = 'Record saved successfully!'
          this.feedbackError = false
          setTimeout(() => {
            this.$router.push('/mmu')
          }, 600)
        } else {
          this.feedbackMsg = data._server_messages ? JSON.parse(data._server_messages).join(' ') : (data.exception || data.message || 'Failed to save record.')
          this.feedbackError = true
        }
      } catch (err) {
        this.feedbackMsg = 'Error saving record: ' + err.message
        this.feedbackError = true
      } finally {
        this.saving = false
      }
    },
    async deleteRecord() {
      if (!confirm('Are you sure you want to delete this MMU Patient Record?')) return
      this.saving = true
      try {
        const csrf = window.csrf_token || (document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || ''
        const res = await fetch('/api/method/mmu.mmu.doctype.mmu_patient_record.mmu_patient_record.delete_patient_record', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Frappe-CSRF-Token': csrf,
          },
          body: JSON.stringify({ record_name: this.editId }),
        })
        if (res.ok) {
          this.$router.push('/mmu')
        } else {
          alert('Failed to delete record.')
        }
      } finally {
        this.saving = false
      }
    },
    resetForm() {
      this.form = {
        date_of_visit: new Date().toISOString().split('T')[0],
        patient_unique_id: '',
        patient_name: '',
        patient_sex: '',
        area_name: '',
        area_code: 0,
        village_name: '',
        village_code: 0,
        age_years: 0,
        age_months: 0,
        age_days: 0,
        total_age: 0.0,
        diagnosis_1: '',
        diag_code_1: 0,
        diagnosis_2: '',
        diag_code_2: 0,
        diagnosis_3: '',
        diag_code_3: 0,
        diagnosis_4: '',
        diag_code_4: 0,
        diagnosis_5: '',
        diag_code_5: 0,
        diagnosis_6: '',
        diag_code_6: 0,
        dental_diagnosis: '',
        diag_code_dental_1: 0,
        dental_diagnosis_2: '',
        diag_code_dental_2: 0,
        patient_newly_diag: '',
        followup_hypertension: '',
        followup_diabetes: '',
        followup_chronic_disease: '',
        patient_referred: 'No',
        patient_referred_where: '',
        patient_referred_by_doctor: '',
        census_match: null,
        matched_member_name: '',
        matched_member_age: 0,
        match_confidence: 0.0,
        match_status: 'Unmatched',
      }
      this.feedbackMsg = ''
    },
  },
}
</script>

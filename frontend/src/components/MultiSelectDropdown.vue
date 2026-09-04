<template>
  <div class="relative w-full" ref="containerRef">
    <label v-if="label" class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
      {{ label }}
    </label>

    <!-- Trigger Button -->
    <button
      type="button"
      @click="toggleDropdown"
      class="w-full flex items-center justify-between px-3 py-2 rounded-xl border text-xs transition-all text-left bg-slate-50/50 dark:bg-slate-800"
      :class="[
        isOpen 
          ? 'border-blue-500 ring-2 ring-blue-500/20 dark:border-blue-400' 
          : selectedCount > 0 
            ? 'border-blue-300 dark:border-blue-700 bg-blue-50/30 dark:bg-blue-950/20' 
            : 'border-slate-300 dark:border-slate-700 hover:border-slate-400'
      ]"
    >
      <div class="flex items-center gap-1.5 flex-1 min-w-0 pr-2">
        <template v-if="selectedCount === 0">
          <span class="text-slate-400 truncate">{{ placeholder || 'All' }}</span>
        </template>
        <template v-else-if="selectedCount === 1">
          <span class="font-medium text-slate-800 dark:text-slate-200 truncate">{{ selectedValues[0] }}</span>
        </template>
        <template v-else>
          <span class="font-medium text-slate-800 dark:text-slate-200 truncate">{{ selectedValues[0] }}</span>
          <span class="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-900/60 dark:text-blue-300 shrink-0">
            +{{ selectedCount - 1 }}
          </span>
        </template>
      </div>

      <div class="flex items-center gap-1 shrink-0">
        <span
          v-if="selectedCount > 0"
          @click.stop="clearAll"
          class="p-0.5 rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
          title="Clear selection"
        >
          <FeatherIcon name="x" class="w-3 h-3" />
        </span>
        <FeatherIcon
          name="chevron-down"
          class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200"
          :class="{ 'rotate-180 text-blue-600 dark:text-blue-400': isOpen }"
        />
      </div>
    </button>

    <!-- Dropdown Menu -->
    <div
      v-if="isOpen"
      class="absolute z-50 left-0 right-0 mt-1.5 bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-800 py-2 overflow-hidden flex flex-col text-xs max-h-64"
    >
      <!-- Search Input (if > 5 options) -->
      <div v-if="options && options.length > 5" class="px-2.5 pb-2 border-b border-slate-100 dark:border-slate-800">
        <div class="relative">
          <input
            ref="searchInputRef"
            type="text"
            v-model="searchQuery"
            placeholder="Search options..."
            class="w-full pl-7 pr-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-800 dark:text-slate-200 focus:outline-hidden focus:border-blue-500"
            @click.stop
          />
          <FeatherIcon name="search" class="w-3.5 h-3.5 text-slate-400 absolute left-2 top-1/2 -translate-y-1/2" />
        </div>
      </div>

      <!-- Quick Action Controls -->
      <div class="px-3 py-1.5 flex items-center justify-between border-b border-slate-100 dark:border-slate-800 text-[11px] text-slate-500 dark:text-slate-400 bg-slate-50/50 dark:bg-slate-800/40">
        <button
          type="button"
          @click.stop="selectAll"
          class="hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors cursor-pointer"
        >
          Select All ({{ filteredOptions.length }})
        </button>
        <button
          type="button"
          @click.stop="clearAll"
          class="hover:text-rose-600 dark:hover:text-rose-400 font-medium transition-colors cursor-pointer"
        >
          Clear
        </button>
      </div>

      <!-- Option List -->
      <div class="overflow-y-auto flex-1 divide-y divide-slate-50 dark:divide-slate-800/50 py-1">
        <div
          v-if="filteredOptions.length === 0"
          class="px-3 py-4 text-center text-slate-400 text-xs italic"
        >
          No matching options
        </div>
        <label
          v-for="opt in filteredOptions"
          :key="opt"
          class="flex items-center gap-2.5 px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-800/70 cursor-pointer select-none transition-colors"
          @click.stop
        >
          <input
            type="checkbox"
            :value="opt"
            :checked="isSelected(opt)"
            @change="toggleOption(opt)"
            class="rounded-sm border-slate-300 text-blue-600 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-800 h-3.5 w-3.5 cursor-pointer"
          />
          <span
            class="flex-1 truncate text-xs"
            :class="[isSelected(opt) ? 'font-semibold text-blue-600 dark:text-blue-400' : 'text-slate-700 dark:text-slate-300']"
          >
            {{ opt }}
          </span>
          <FeatherIcon
            v-if="isSelected(opt)"
            name="check"
            class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 shrink-0"
          />
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import FeatherIcon from 'frappe-ui/src/components/FeatherIcon.vue'

export default {
  name: 'MultiSelectDropdown',
  components: {
    FeatherIcon
  },
  props: {
    modelValue: {
      type: [Array, String],
      default: () => []
    },
    options: {
      type: Array,
      default: () => []
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'All'
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      isOpen: false,
      searchQuery: ''
    }
  },
  computed: {
    selectedValues() {
      if (Array.isArray(this.modelValue)) {
        return this.modelValue
      }
      if (typeof this.modelValue === 'string' && this.modelValue.trim()) {
        return this.modelValue.split(',').map(s => s.trim()).filter(Boolean)
      }
      return []
    },
    selectedCount() {
      return this.selectedValues.length
    },
    filteredOptions() {
      if (!this.options) return []
      if (!this.searchQuery.trim()) return this.options
      const q = this.searchQuery.toLowerCase().trim()
      return this.options.filter(opt => String(opt).toLowerCase().includes(q))
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    toggleDropdown() {
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.searchQuery = ''
        this.$nextTick(() => {
          if (this.$refs.searchInputRef) {
            this.$refs.searchInputRef.focus()
          }
        })
      }
    },
    handleClickOutside(e) {
      if (this.$refs.containerRef && !this.$refs.containerRef.contains(e.target)) {
        this.isOpen = false
      }
    },
    isSelected(opt) {
      return this.selectedValues.includes(opt)
    },
    toggleOption(opt) {
      const current = [...this.selectedValues]
      const idx = current.indexOf(opt)
      if (idx > -1) {
        current.splice(idx, 1)
      } else {
        current.push(opt)
      }
      this.$emit('update:modelValue', current)
    },
    selectAll() {
      const current = new Set(this.selectedValues)
      this.filteredOptions.forEach(opt => current.add(opt))
      this.$emit('update:modelValue', Array.from(current))
    },
    clearAll() {
      this.$emit('update:modelValue', [])
    }
  }
}
</script>

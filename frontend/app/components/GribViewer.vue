<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-2xl font-bold">GRIB Data Viewer</h2>
      <button
        v-if="fileId"
        @click="$emit('close')"
        class="text-gray-500 hover:text-gray-700"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      <p class="mt-4 text-gray-600">Loading GRIB data...</p>
    </div>

    <div v-else-if="error" class="text-center py-12 text-red-600">
      <p>Error loading data: {{ error }}</p>
    </div>

    <div v-else-if="!fileId" class="text-center py-12 text-gray-600">
      <p>Select a GRIB file to view its data</p>
    </div>

    <div v-else-if="gribData" class="space-y-6">
      <!-- File Info -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3 class="font-semibold mb-2">File Information</h3>
        <p class="text-sm text-gray-600">{{ gribData.filename }}</p>
      </div>

      <!-- Variable Selection -->
      <div v-if="gribData.variables.length > 0">
        <label class="block text-sm font-medium text-gray-700 mb-2">Select Variable</label>
        <select
          v-model="selectedVariable"
          @change="loadData"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option v-for="variable in gribData.variables" :key="variable" :value="variable">
            {{ variable }}
          </option>
        </select>
      </div>

      <!-- Dimensions -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h3 class="font-semibold mb-2">Dimensions</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div v-for="(value, key) in gribData.dimensions" :key="key">
            <span class="text-gray-600">{{ key }}:</span>
            <span class="ml-2 font-medium">{{ value }}</span>
          </div>
        </div>
      </div>

      <!-- Coordinates -->
      <div v-if="gribData.metadata?.coordinates" class="bg-gray-50 rounded-lg p-4">
        <h3 class="font-semibold mb-2">Coordinates</h3>
        <div class="space-y-2 text-sm">
          <div v-for="(values, key) in gribData.metadata.coordinates" :key="key">
            <span class="text-gray-600 font-medium">{{ key }}:</span>
            <p class="text-xs text-gray-500 mt-1">
              Range: {{ formatCoordinateRange(values) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Map Visualization -->
      <MapViewer :gribData="gribData" />

      <!-- Metadata -->
      <div v-if="gribData.metadata?.attributes" class="bg-gray-50 rounded-lg p-4">
        <h3 class="font-semibold mb-2">Attributes</h3>
        <div class="space-y-1 text-sm max-h-48 overflow-y-auto">
          <div v-for="(value, key) in gribData.metadata.attributes" :key="key" class="flex">
            <span class="text-gray-600 min-w-[120px]">{{ key }}:</span>
            <span class="ml-2 text-gray-900 break-all">{{ value }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  fileId: string | null
}>()

const emit = defineEmits(['close'])
const { getGribData } = useGribApi()

interface GRIBData {
  file_id: string
  filename: string
  variables: string[]
  dimensions: Record<string, number>
  metadata: {
    coordinates?: Record<string, number[]>
    attributes?: Record<string, any>
  }
  data: Record<string, any>
}

const gribData = ref<GRIBData | null>(null)
const loading = ref(false)
const error = ref('')
const selectedVariable = ref<string | null>(null)

const loadData = async () => {
  if (!props.fileId) return

  loading.value = true
  error.value = ''

  try {
    const data = await getGribData(
      props.fileId, 
      selectedVariable.value ? selectedVariable.value : undefined
    )
    gribData.value = data as GRIBData
    
    // Set default variable if not selected
    if (!selectedVariable.value && data.variables.length > 0) {
      selectedVariable.value = data.variables[0]
    }
  } catch (e: any) {
    error.value = e.message || 'Failed to load GRIB data'
    gribData.value = null
  } finally {
    loading.value = false
  }
}

const formatCoordinateRange = (values: number[]): string => {
  if (!values || values.length === 0) return 'N/A'
  const min = Math.min(...values)
  const max = Math.max(...values)
  return `${min.toFixed(2)} to ${max.toFixed(2)}`
}

// Watch for file ID changes
watch(() => props.fileId, () => {
  if (props.fileId) {
    loadData()
  } else {
    gribData.value = null
    selectedVariable.value = null
  }
}, { immediate: true })
</script>

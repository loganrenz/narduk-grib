<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold mb-4">GRIB Data Downloader</h2>
    
    <form @submit.prevent="downloadGrib" class="space-y-4">
      <!-- Model Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Model</label>
        <select
          v-model="form.model"
          @change="onModelChange"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="gfs">GFS (Global Forecast System)</option>
          <option value="gfs-wave">GFS Wave</option>
          <option value="nam">NAM (North American Mesoscale)</option>
          <option value="hrrr">HRRR (High Resolution Rapid Refresh)</option>
          <option value="rtofs">RTOFS (Real-Time Ocean Forecast)</option>
        </select>
      </div>

      <!-- Resolution -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Resolution</label>
        <select
          v-model="form.resolution"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="0p25">0.25° (~25 km)</option>
          <option value="0p50">0.50° (~50 km)</option>
          <option value="1p00">1.00° (~100 km)</option>
        </select>
      </div>

      <!-- Region Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Region</label>
        <select
          v-model="form.region"
          @change="onRegionChange"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="custom">Custom Region</option>
          <option value="gulf-of-mexico">Gulf of Mexico</option>
          <option value="caribbean">Caribbean</option>
          <option value="atlantic">North Atlantic</option>
          <option value="pacific">North Pacific</option>
          <option value="global">Global</option>
        </select>
      </div>

      <!-- Custom Bounding Box -->
      <div v-if="form.region === 'custom'" class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">West Longitude</label>
          <input
            v-model.number="form.westLon"
            type="number"
            step="0.1"
            min="-180"
            max="180"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">East Longitude</label>
          <input
            v-model.number="form.eastLon"
            type="number"
            step="0.1"
            min="-180"
            max="180"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">North Latitude</label>
          <input
            v-model.number="form.northLat"
            type="number"
            step="0.1"
            min="-90"
            max="90"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">South Latitude</label>
          <input
            v-model.number="form.southLat"
            type="number"
            step="0.1"
            min="-90"
            max="90"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <!-- Variables Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Variables</label>
        <div class="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-3">
          <label v-for="variable in availableVariables" :key="variable.value" class="flex items-center space-x-2">
            <input
              v-model="form.variables"
              type="checkbox"
              :value="variable.value"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm">{{ variable.label }}</span>
          </label>
        </div>
      </div>

      <!-- Forecast Hours -->
      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Start Hour</label>
          <input
            v-model.number="form.startHour"
            type="number"
            min="0"
            :max="form.endHour"
            step="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">End Hour</label>
          <input
            v-model.number="form.endHour"
            type="number"
            :min="form.startHour"
            max="384"
            step="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Interval (hrs)</label>
          <select
            v-model.number="form.interval"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option :value="3">3 hours</option>
            <option :value="6">6 hours</option>
            <option :value="12">12 hours</option>
            <option :value="24">24 hours</option>
          </select>
        </div>
      </div>

      <!-- Model Run Time -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Model Run Cycle</label>
          <select
            v-model="form.cycle"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="00">00Z (Midnight UTC)</option>
            <option value="06">06Z (6 AM UTC)</option>
            <option value="12">12Z (Noon UTC)</option>
            <option value="18">18Z (6 PM UTC)</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
          <input
            v-model="form.date"
            type="date"
            :max="maxDate"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <!-- Pressure Levels -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Pressure Levels (mb)</label>
        <div class="grid grid-cols-4 gap-2 border border-gray-200 rounded-lg p-3">
          <label v-for="level in pressureLevels" :key="level" class="flex items-center space-x-2">
            <input
              v-model="form.levels"
              type="checkbox"
              :value="level"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm">{{ level }}</span>
          </label>
        </div>
      </div>

      <div v-if="downloadError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
        {{ downloadError }}
      </div>

      <div v-if="downloadStatus" class="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-sm">
        {{ downloadStatus }}
      </div>

      <button
        type="submit"
        :disabled="isDownloading || !isFormValid"
        class="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-4 rounded-lg disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        {{ isDownloading ? 'Downloading...' : 'Download GRIB Data' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits(['downloaded'])
const { downloadFile } = useGribApi()

const form = ref({
  model: 'gfs',
  resolution: '0p25',
  region: 'gulf-of-mexico',
  westLon: 260,
  eastLon: 280,
  northLat: 32,
  southLat: 22,
  variables: ['TMP', 'UGRD', 'VGRD'],
  startHour: 0,
  endHour: 24,
  interval: 6,
  cycle: '00',
  date: new Date().toISOString().split('T')[0],
  levels: ['surface']
})

const isDownloading = ref(false)
const downloadError = ref('')
const downloadStatus = ref('')

const availableVariables = [
  { value: 'TMP', label: 'Temperature' },
  { value: 'UGRD', label: 'U Wind' },
  { value: 'VGRD', label: 'V Wind' },
  { value: 'PRMSL', label: 'Pressure (MSL)' },
  { value: 'RH', label: 'Relative Humidity' },
  { value: 'APCP', label: 'Precipitation' },
  { value: 'TCDC', label: 'Cloud Cover' },
  { value: 'HGT', label: 'Geopotential Height' },
  { value: 'VVEL', label: 'Vertical Velocity' },
  { value: 'ABSV', label: 'Absolute Vorticity' }
]

const pressureLevels = ['surface', '1000', '925', '850', '700', '500', '300', '250', '200', '100']

const maxDate = computed(() => new Date().toISOString().split('T')[0])

const isFormValid = computed(() => {
  return form.value.variables.length > 0 && form.value.levels.length > 0
})

const regions = {
  'gulf-of-mexico': { west: 260, east: 280, north: 32, south: 22 },
  'caribbean': { west: 270, east: 290, north: 25, south: 10 },
  'atlantic': { west: 280, east: 340, north: 50, south: 20 },
  'pacific': { west: 180, east: 240, north: 50, south: 20 },
  'global': { west: 0, east: 360, north: 90, south: -90 }
}

const onModelChange = () => {
  // Update available options based on model
  downloadStatus.value = ''
  downloadError.value = ''
}

const onRegionChange = () => {
  if (form.value.region !== 'custom' && regions[form.value.region as keyof typeof regions]) {
    const region = regions[form.value.region as keyof typeof regions]
    form.value.westLon = region.west
    form.value.eastLon = region.east
    form.value.northLat = region.north
    form.value.southLat = region.south
  }
}

const buildGribUrl = (): string => {
  const dateStr = form.value.date.replace(/-/g, '')
  const cycle = form.value.cycle
  
  // Build the base URL for GFS
  let baseUrl = `https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_${form.value.resolution}.pl?`
  
  // Add file parameter
  baseUrl += `file=gfs.t${cycle}z.pgrb2.${form.value.resolution}.f${String(form.value.startHour).padStart(3, '0')}`
  
  // Add variables
  form.value.variables.forEach(v => {
    baseUrl += `&var_${v}=on`
  })
  
  // Add levels
  form.value.levels.forEach(l => {
    const levelKey = l === 'surface' ? 'lev_surface' : `lev_${l}_mb`
    baseUrl += `&${levelKey}=on`
  })
  
  // Add bounding box
  baseUrl += `&subregion=`
  baseUrl += `&leftlon=${form.value.westLon}`
  baseUrl += `&rightlon=${form.value.eastLon}`
  baseUrl += `&toplat=${form.value.northLat}`
  baseUrl += `&bottomlat=${form.value.southLat}`
  
  // Add directory
  baseUrl += `&dir=%2Fgfs.${dateStr}%2F${cycle}%2Fatmos`
  
  return baseUrl
}

const downloadGrib = async () => {
  isDownloading.value = true
  downloadError.value = ''
  downloadStatus.value = 'Building download URL...'
  
  try {
    const url = buildGribUrl()
    downloadStatus.value = 'Downloading GRIB data from NOAA...'
    
    await downloadFile(url)
    
    downloadStatus.value = 'Download complete!'
    emit('downloaded')
    
    setTimeout(() => {
      downloadStatus.value = ''
    }, 3000)
  } catch (error: any) {
    downloadError.value = error.message || 'Failed to download GRIB data'
    downloadStatus.value = ''
  } finally {
    isDownloading.value = false
  }
}

// Initialize region on mount
onMounted(() => {
  onRegionChange()
})
</script>

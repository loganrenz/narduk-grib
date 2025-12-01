<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-2xl font-bold">Map Viewer</h2>
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">Map Provider:</label>
        <select
          v-model="mapProvider"
          @change="switchMapProvider"
          class="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="leaflet">Leaflet (OSM)</option>
          <option value="mapbox">Mapbox</option>
          <option value="mapkit">Apple MapKit JS</option>
        </select>
      </div>
    </div>

    <div v-if="!gribData" class="text-center py-12 text-gray-600">
      <p>Select a GRIB file to view data on the map</p>
    </div>

    <div v-else>
      <!-- Map Provider Config Messages -->
      <div v-if="mapProvider === 'mapbox' && !mapboxToken" class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm">
        <strong>Mapbox requires an API token.</strong> Set NUXT_PUBLIC_MAPBOX_TOKEN in your environment.
      </div>
      
      <div v-if="mapProvider === 'mapkit' && !mapkitToken" class="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm">
        <strong>MapKit JS requires an API token.</strong> Set NUXT_PUBLIC_MAPKIT_TOKEN in your environment.
      </div>

      <!-- Data Info -->
      <div class="mb-4 bg-gray-50 rounded-lg p-4">
        <div class="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span class="font-medium">File:</span>
            <span class="ml-2">{{ gribData.filename }}</span>
          </div>
          <div>
            <span class="font-medium">Variables:</span>
            <span class="ml-2">{{ gribData.variables.join(', ') }}</span>
          </div>
          <div>
            <span class="font-medium">Data Points:</span>
            <span class="ml-2">{{ dataPointCount }}</span>
          </div>
        </div>
      </div>

      <!-- Map Container -->
      <div class="relative">
        <div 
          ref="mapContainer" 
          :class="`map-container-${mapProvider}`"
          class="w-full h-96 rounded-lg border border-gray-300"
        ></div>

        <!-- Map Loading Overlay -->
        <div v-if="mapLoading" class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
          <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <p class="mt-2 text-sm text-gray-600">Loading map...</p>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="mt-4 p-4 bg-gray-50 rounded-lg">
        <h3 class="font-semibold mb-2">Data Visualization</h3>
        <p class="text-sm text-gray-600">
          Map shows {{ currentVariable }} data. 
          Use the map controls to zoom and pan. 
          Data points are displayed as markers/heatmap based on the selected provider.
        </p>
        <div class="mt-3 flex items-center space-x-4 text-xs text-gray-500">
          <div class="flex items-center">
            <div class="w-4 h-4 bg-blue-500 rounded-full mr-2"></div>
            <span>Data Point</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
            <span>High Value</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
            <span>Low Value</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

const props = defineProps<{
  gribData: GRIBData | null
}>()

const config = useRuntimeConfig()
const mapProvider = ref('leaflet')
const mapContainer = ref<HTMLElement | null>(null)
const mapInstance = ref<any>(null)
const mapLoading = ref(false)
const currentVariable = ref('')

const mapboxToken = config.public.mapboxToken || ''
const mapkitToken = config.public.mapkitToken || ''

const dataPointCount = computed(() => {
  if (!props.gribData) return 0
  const firstVar = props.gribData.variables[0]
  if (!firstVar || !props.gribData.data[firstVar]) return 0
  const data = props.gribData.data[firstVar]
  return Array.isArray(data) ? data.flat().length : 0
})

const loadLeaflet = () => {
  if (typeof window === 'undefined') return
  
  mapLoading.value = true
  
  // Dynamically import Leaflet
  import('leaflet').then((L) => {
    if (!mapContainer.value) return
    
    // Initialize map
    mapInstance.value = L.map(mapContainer.value).setView([27, -90], 6)
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(mapInstance.value)
    
    // Add GRIB data if available
    if (props.gribData) {
      plotDataOnLeaflet(L)
    }
    
    mapLoading.value = false
  }).catch((error) => {
    console.error('Error loading Leaflet:', error)
    mapLoading.value = false
  })
}

const plotDataOnLeaflet = (L: any) => {
  if (!props.gribData || !mapInstance.value) return
  
  const coords = props.gribData.metadata?.coordinates
  if (!coords || !coords.latitude || !coords.longitude) return
  
  currentVariable.value = props.gribData.variables[0]
  const data = props.gribData.data[currentVariable.value]
  
  if (!Array.isArray(data)) return
  
  // Plot data points as markers
  const lats = coords.latitude
  const lons = coords.longitude
  
  // Sample a subset of points to avoid overwhelming the map
  const step = Math.max(1, Math.floor(lats.length / 50))
  
  for (let i = 0; i < lats.length; i += step) {
    for (let j = 0; j < lons.length; j += step) {
      const lat = lats[i]
      let lon = lons[j]
      
      // Convert longitude from 0-360 to -180-180 if needed
      if (lon > 180) lon = lon - 360
      
      const value = Array.isArray(data[i]) ? data[i][j] : data
      
      if (value !== null && value !== undefined && !isNaN(value)) {
        const marker = L.circleMarker([lat, lon], {
          radius: 3,
          fillColor: getColorForValue(value),
          fillOpacity: 0.6,
          stroke: false
        }).addTo(mapInstance.value)
        
        marker.bindPopup(`${currentVariable.value}: ${value.toFixed(2)}`)
      }
    }
  }
  
  // Fit bounds to data
  if (lats.length > 0 && lons.length > 0) {
    const bounds = L.latLngBounds(
      [Math.min(...lats), Math.min(...lons.map(l => l > 180 ? l - 360 : l))],
      [Math.max(...lats), Math.max(...lons.map(l => l > 180 ? l - 360 : l))]
    )
    mapInstance.value.fitBounds(bounds)
  }
}

const loadMapbox = () => {
  if (!mapboxToken) {
    mapLoading.value = false
    return
  }
  
  mapLoading.value = true
  
  // Load Mapbox GL JS dynamically
  const script = document.createElement('script')
  script.src = 'https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'
  script.onload = () => {
    const link = document.createElement('link')
    link.href = 'https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css'
    link.rel = 'stylesheet'
    document.head.appendChild(link)
    
    // Initialize Mapbox
    const mapboxgl = (window as any).mapboxgl
    mapboxgl.accessToken = mapboxToken
    
    if (mapContainer.value) {
      mapInstance.value = new mapboxgl.Map({
        container: mapContainer.value,
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [-90, 27],
        zoom: 5
      })
      
      mapInstance.value.on('load', () => {
        if (props.gribData) {
          plotDataOnMapbox()
        }
        mapLoading.value = false
      })
    }
  }
  document.head.appendChild(script)
}

const plotDataOnMapbox = () => {
  // Placeholder for Mapbox data plotting
  console.log('Plotting data on Mapbox')
  currentVariable.value = props.gribData?.variables[0] || ''
}

const loadMapKit = () => {
  if (!mapkitToken) {
    mapLoading.value = false
    return
  }
  
  mapLoading.value = true
  
  // Load MapKit JS
  const script = document.createElement('script')
  script.src = 'https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.js'
  script.crossOrigin = 'anonymous'
  script.onload = () => {
    const mapkit = (window as any).mapkit
    mapkit.init({
      authorizationCallback: (done: any) => {
        done(mapkitToken)
      }
    })
    
    if (mapContainer.value) {
      mapInstance.value = new mapkit.Map(mapContainer.value, {
        center: new mapkit.Coordinate(27, -90),
        zoom: 6
      })
      
      if (props.gribData) {
        plotDataOnMapKit()
      }
      mapLoading.value = false
    }
  }
  document.head.appendChild(script)
}

const plotDataOnMapKit = () => {
  // Placeholder for MapKit data plotting
  console.log('Plotting data on MapKit')
  currentVariable.value = props.gribData?.variables[0] || ''
}

const getColorForValue = (value: number): string => {
  // Simple color scale from blue (low) to red (high)
  // This should be improved with proper data scaling
  const normalized = Math.max(0, Math.min(1, (value + 50) / 100))
  const r = Math.floor(normalized * 255)
  const b = Math.floor((1 - normalized) * 255)
  return `rgb(${r}, 0, ${b})`
}

const switchMapProvider = () => {
  // Clean up existing map
  if (mapInstance.value) {
    if (typeof mapInstance.value.remove === 'function') {
      mapInstance.value.remove()
    }
    mapInstance.value = null
  }
  
  // Clear container
  if (mapContainer.value) {
    mapContainer.value.innerHTML = ''
  }
  
  // Load new provider
  nextTick(() => {
    loadMap()
  })
}

const loadMap = () => {
  if (!mapContainer.value) return
  
  switch (mapProvider.value) {
    case 'leaflet':
      loadLeaflet()
      break
    case 'mapbox':
      loadMapbox()
      break
    case 'mapkit':
      loadMapKit()
      break
  }
}

// Watch for GRIB data changes
watch(() => props.gribData, (newData) => {
  if (newData && mapInstance.value) {
    // Reload map with new data
    switchMapProvider()
  }
})

onMounted(() => {
  loadMap()
})

onUnmounted(() => {
  if (mapInstance.value && typeof mapInstance.value.remove === 'function') {
    mapInstance.value.remove()
  }
})
</script>

<style scoped>
.map-container-leaflet,
.map-container-mapbox,
.map-container-mapkit {
  position: relative;
}
</style>

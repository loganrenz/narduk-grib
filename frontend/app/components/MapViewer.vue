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

      <!-- Timeline Scrubber -->
      <div v-if="hasTimeSteps" class="mt-4 p-4 bg-white rounded-lg border border-gray-300">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-sm">Timeline</h3>
          <div class="flex items-center space-x-2">
            <button
              @click="toggleAnimation"
              class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
            >
              {{ isAnimating ? '⏸ Pause' : '▶ Play' }}
            </button>
            <select
              v-model="animationSpeed"
              class="px-2 py-1 border border-gray-300 rounded text-sm"
            >
              <option :value="0.5">0.5x</option>
              <option :value="1">1x</option>
              <option :value="2">2x</option>
            </select>
          </div>
        </div>
        
        <div class="space-y-2">
          <div class="flex items-center space-x-3">
            <span class="text-xs font-medium text-gray-600 w-24">Time Step:</span>
            <input
              type="range"
              v-model="currentTimeIndex"
              :min="0"
              :max="timeSteps.length - 1"
              class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
              @input="onTimeStepChange"
            />
            <span class="text-xs font-mono text-gray-700 w-20">{{ currentTimeIndex + 1 }}/{{ timeSteps.length }}</span>
          </div>
          
          <div class="text-sm text-center py-2 bg-gray-50 rounded border border-gray-200">
            <span class="font-semibold text-blue-600">{{ currentTimeDisplay }}</span>
            <span v-if="forecastHour !== null" class="ml-3 text-gray-600">
              Forecast Hour: +{{ forecastHour }}h
            </span>
          </div>
        </div>
      </div>

      <!-- Color Legend -->
      <div class="mt-4 p-4 bg-gray-50 rounded-lg">
        <h3 class="font-semibold mb-3">Color Scale</h3>
        <div class="space-y-3">
          <!-- Color gradient bar -->
          <div class="h-6 rounded" :style="{ background: colorGradient }"></div>
          
          <div class="flex justify-between text-xs text-gray-600">
            <span>{{ minValue.toFixed(1) }} {{ getUnit(currentVariable) }}</span>
            <span>{{ ((minValue + maxValue) / 2).toFixed(1) }} {{ getUnit(currentVariable) }}</span>
            <span>{{ maxValue.toFixed(1) }} {{ getUnit(currentVariable) }}</span>
          </div>
          
          <p class="text-sm text-gray-600 mt-3">
            Map shows <strong>{{ currentVariable }}</strong> data.
            {{ hasWindBarbs ? 'Wind barbs show direction and speed.' : 'Use the map controls to zoom and pan.' }}
          </p>
        </div>
      </div>

      <!-- Visualization Type Selector -->
      <div v-if="hasWindData" class="mt-4 p-4 bg-white rounded-lg border border-gray-300">
        <div class="flex items-center justify-between">
          <span class="font-semibold text-sm">Visualization Type:</span>
          <div class="flex space-x-2">
            <button
              @click="visualizationType = 'points'"
              :class="[
                'px-3 py-1 rounded text-sm',
                visualizationType === 'points' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              Points
            </button>
            <button
              @click="visualizationType = 'barbs'"
              :class="[
                'px-3 py-1 rounded text-sm',
                visualizationType === 'barbs' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              Wind Barbs
            </button>
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

// Timeline controls
const currentTimeIndex = ref(0)
const timeSteps = ref<any[]>([])
const isAnimating = ref(false)
const animationSpeed = ref(1)
const animationInterval = ref<any>(null)

// Visualization controls
const visualizationType = ref<'points' | 'barbs'>('points')
const minValue = ref(0)
const maxValue = ref(100)

const mapboxToken = config.public.mapboxToken || ''
const mapkitToken = config.public.mapkitToken || ''

const dataPointCount = computed(() => {
  if (!props.gribData) return 0
  const firstVar = props.gribData.variables[0]
  if (!firstVar || !props.gribData.data[firstVar]) return 0
  const data = props.gribData.data[firstVar]
  return Array.isArray(data) ? data.flat().length : 0
})

const hasTimeSteps = computed(() => {
  return timeSteps.value.length > 1
})

const hasWindData = computed(() => {
  if (!props.gribData) return false
  const vars = props.gribData.variables
  return (vars.includes('u10') && vars.includes('v10')) || 
         (vars.includes('u') && vars.includes('v'))
})

const hasWindBarbs = computed(() => {
  return hasWindData.value && visualizationType.value === 'barbs'
})

const currentTimeDisplay = computed(() => {
  if (timeSteps.value.length === 0) return 'No time data'
  const currentTime = timeSteps.value[currentTimeIndex.value]
  if (!currentTime) return 'Unknown'
  return new Date(currentTime).toLocaleString()
})

const forecastHour = computed(() => {
  if (timeSteps.value.length === 0) return null
  return currentTimeIndex.value * 3 // Assuming 3-hour intervals
})

const colorGradient = computed(() => {
  // Generate color gradient based on variable type
  if (currentVariable.value.includes('tmp') || currentVariable.value.includes('t2m')) {
    // Temperature: blue -> cyan -> green -> yellow -> red
    return 'linear-gradient(to right, #0000ff, #00ffff, #00ff00, #ffff00, #ff0000)'
  } else if (currentVariable.value.includes('wind') || currentVariable.value.includes('u10') || currentVariable.value.includes('v10')) {
    // Wind: light blue -> dark blue
    return 'linear-gradient(to right, #e0f7ff, #0066cc, #003366)'
  } else if (currentVariable.value.includes('pres')) {
    // Pressure: purple -> white -> orange
    return 'linear-gradient(to right, #9b59b6, #ecf0f1, #e67e22)'
  } else {
    // Default: blue -> red
    return 'linear-gradient(to right, #0000ff, #00ff00, #ff0000)'
  }
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
  
  // Calculate min/max values for color scaling
  calculateDataRange(data)
  
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
          radius: 4,
          fillColor: getColorForValue(value),
          fillOpacity: 0.7,
          stroke: true,
          color: '#fff',
          weight: 1
        }).addTo(mapInstance.value)
        
        marker.bindPopup(`${currentVariable.value}: ${value.toFixed(2)} ${getUnit(currentVariable.value)}`)
      }
    }
  }

const calculateDataRange = (data: any) => {
  let min = Infinity
  let max = -Infinity
  
  const processValue = (val: number) => {
    if (val !== null && val !== undefined && !isNaN(val)) {
      min = Math.min(min, val)
      max = Math.max(max, val)
    }
  }
  
  if (Array.isArray(data)) {
    data.forEach((row: any) => {
      if (Array.isArray(row)) {
        row.forEach(processValue)
      } else {
        processValue(row)
      }
    })
  }
  
  minValue.value = min === Infinity ? 0 : min
  maxValue.value = max === -Infinity ? 100 : max
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
  // Improved color scale with meteorological standards
  const normalized = Math.max(0, Math.min(1, (value - minValue.value) / (maxValue.value - minValue.value)))
  
  if (currentVariable.value.includes('tmp') || currentVariable.value.includes('t2m')) {
    // Temperature scale: blue -> cyan -> green -> yellow -> orange -> red
    if (normalized < 0.2) {
      const t = normalized / 0.2
      return `rgb(${Math.floor(t * 0)}, ${Math.floor(t * 255)}, 255)`
    } else if (normalized < 0.4) {
      const t = (normalized - 0.2) / 0.2
      return `rgb(0, 255, ${Math.floor(255 * (1 - t))})`
    } else if (normalized < 0.6) {
      const t = (normalized - 0.4) / 0.2
      return `rgb(${Math.floor(t * 255)}, 255, 0)`
    } else if (normalized < 0.8) {
      const t = (normalized - 0.6) / 0.2
      return `rgb(255, ${Math.floor(255 * (1 - t * 0.5))}, 0)`
    } else {
      const t = (normalized - 0.8) / 0.2
      return `rgb(255, ${Math.floor(128 * (1 - t))}, 0)`
    }
  } else {
    // Default scale: blue -> green -> red
    const r = Math.floor(normalized * 255)
    const g = Math.floor(Math.sin(normalized * Math.PI) * 255)
    const b = Math.floor((1 - normalized) * 255)
    return `rgb(${r}, ${g}, ${b})`
  }
}

const getUnit = (variable: string): string => {
  if (variable.includes('tmp') || variable.includes('t2m')) return 'K'
  if (variable.includes('wind') || variable.includes('u') || variable.includes('v')) return 'm/s'
  if (variable.includes('pres')) return 'hPa'
  if (variable.includes('rh')) return '%'
  return ''
}

const initializeTimeline = () => {
  // Extract time steps from GRIB data
  // For now, we'll create a simple timeline
  // In a real implementation, this would parse the time coordinate
  timeSteps.value = [new Date().toISOString()]
  currentTimeIndex.value = 0
}

const onTimeStepChange = () => {
  // Update visualization when time step changes
  if (mapInstance.value) {
    updateVisualization()
  }
}

const toggleAnimation = () => {
  isAnimating.value = !isAnimating.value
  
  if (isAnimating.value) {
    startAnimation()
  } else {
    stopAnimation()
  }
}

const startAnimation = () => {
  const interval = 1000 / animationSpeed.value
  animationInterval.value = setInterval(() => {
    currentTimeIndex.value = (currentTimeIndex.value + 1) % timeSteps.value.length
    onTimeStepChange()
  }, interval)
}

const stopAnimation = () => {
  if (animationInterval.value) {
    clearInterval(animationInterval.value)
    animationInterval.value = null
  }
}

const updateVisualization = () => {
  if (!mapInstance.value || !props.gribData) return
  
  // Clear existing overlays
  if (mapProvider.value === 'leaflet') {
    clearLeafletOverlays()
    if (visualizationType.value === 'barbs' && hasWindData.value) {
      plotWindBarbs()
    } else {
      plotDataOnLeaflet((window as any).L)
    }
  }
}

const clearLeafletOverlays = () => {
  if (!mapInstance.value) return
  // Remove all layers except the base tile layer
  mapInstance.value.eachLayer((layer: any) => {
    if (layer._url === undefined) { // Not a tile layer
      mapInstance.value.removeLayer(layer)
    }
  })
}

const plotWindBarbs = () => {
  if (!props.gribData || !mapInstance.value) return
  
  const coords = props.gribData.metadata?.coordinates
  if (!coords || !coords.latitude || !coords.longitude) return
  
  // Get u and v components
  const uVar = props.gribData.variables.find(v => v === 'u10' || v === 'u')
  const vVar = props.gribData.variables.find(v => v === 'v10' || v === 'v')
  
  if (!uVar || !vVar) return
  
  const uData = props.gribData.data[uVar]
  const vData = props.gribData.data[vVar]
  
  if (!Array.isArray(uData) || !Array.isArray(vData)) return
  
  const lats = coords.latitude
  const lons = coords.longitude
  const step = Math.max(1, Math.floor(lats.length / 20)) // Sample for wind barbs
  
  const L = (window as any).L
  
  for (let i = 0; i < lats.length; i += step) {
    for (let j = 0; j < lons.length; j += step) {
      const lat = lats[i]
      let lon = lons[j]
      
      if (lon > 180) lon = lon - 360
      
      const u = Array.isArray(uData[i]) ? uData[i][j] : uData
      const v = Array.isArray(vData[i]) ? vData[i][j] : vData
      
      if (u !== null && v !== null && !isNaN(u) && !isNaN(v)) {
        // Calculate wind speed and direction
        const speed = Math.sqrt(u * u + v * v)
        const direction = (Math.atan2(u, v) * 180 / Math.PI + 180) % 360
        
        // Draw wind barb
        drawWindBarb(L, lat, lon, speed, direction)
      }
    }
  }
}

const drawWindBarb = (L: any, lat: number, lon: number, speed: number, direction: number) => {
  // Simplified wind barb representation
  // In production, use a proper wind barb library
  
  const barbLength = 20
  const angle = (direction - 90) * Math.PI / 180
  
  // Calculate barb end point
  const endLat = lat + (barbLength / 111000) * Math.cos(angle)
  const endLon = lon + (barbLength / 111000) * Math.sin(angle) / Math.cos(lat * Math.PI / 180)
  
  // Draw line
  const polyline = L.polyline([[lat, lon], [endLat, endLon]], {
    color: getColorForValue(speed * 3.6), // Convert to km/h for coloring
    weight: 2,
    opacity: 0.8
  }).addTo(mapInstance.value)
  
  // Add popup
  polyline.bindPopup(`Wind: ${speed.toFixed(1)} m/s<br>Direction: ${Math.round(direction)}°`)
  
  // Add speed flags (simplified)
  const flagCount = Math.floor(speed / 5) // 1 flag per 5 m/s
  for (let i = 0; i < Math.min(flagCount, 3); i++) {
    const flagPos = 0.3 + (i * 0.2)
    const flagLat = lat + (barbLength * flagPos / 111000) * Math.cos(angle)
    const flagLon = lon + (barbLength * flagPos / 111000) * Math.sin(angle) / Math.cos(lat * Math.PI / 180)
    
    const perpAngle = angle + Math.PI / 2
    const flagEndLat = flagLat + (10 / 111000) * Math.cos(perpAngle)
    const flagEndLon = flagLon + (10 / 111000) * Math.sin(perpAngle) / Math.cos(flagLat * Math.PI / 180)
    
    L.polyline([[flagLat, flagLon], [flagEndLat, flagEndLon]], {
      color: getColorForValue(speed * 3.6),
      weight: 2,
      opacity: 0.8
    }).addTo(mapInstance.value)
  }
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
  if (newData) {
    initializeTimeline()
    if (mapInstance.value) {
      // Reload map with new data
      switchMapProvider()
    }
  }
})

// Watch for visualization type changes
watch(visualizationType, () => {
  if (mapInstance.value && props.gribData) {
    updateVisualization()
  }
})

onMounted(() => {
  initializeTimeline()
  loadMap()
})

onUnmounted(() => {
  stopAnimation()
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

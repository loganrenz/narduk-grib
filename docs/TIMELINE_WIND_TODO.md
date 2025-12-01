# Timeline Scrubber and Wind Barbs - Future Improvements

## Overview

The timeline scrubber and wind barbs features are implemented with comprehensive documentation. This document tracks future enhancements based on code review feedback and potential improvements.

## Backend Enhancements

### Multi-Time GRIB Support

**Current State**: Backend extracts single time step from GRIB files
**Goal**: Support files with multiple time dimensions

**Tasks:**
- [ ] Update `get_grib_data()` to handle time coordinate
- [ ] Extract all time steps from GRIB file
- [ ] Return time array in metadata
- [ ] Support time filtering in API (`?time_index=5`)
- [ ] Add time coordinate to GRIBDataResponse model

**Example Enhancement:**
```python
# backend/grib_service.py
async def get_grib_data(self, file_id: str, time_index: Optional[int] = None):
    ds = xr.open_dataset(file_path, engine='cfgrib')
    
    # Extract time coordinate if present
    if 'time' in ds.coords:
        times = ds.coords['time'].values.tolist()
        if time_index is not None:
            ds = ds.isel(time=time_index)
    else:
        times = [ds.coords.get('valid_time', None)]
    
    metadata['times'] = times
    metadata['time_count'] = len(times)
```

## Frontend Enhancements

### 1. Dynamic Time Parsing

**Issue**: Timeline currently creates placeholder timestamps
**Location**: `frontend/app/components/MapViewer.vue`, lines 495-501

**Current Code:**
```javascript
const initializeTimeline = () => {
  timeSteps.value = [new Date().toISOString()]
  currentTimeIndex.value = 0
}
```

**Proposed Enhancement:**
```javascript
const initializeTimeline = () => {
  if (!props.gribData || !props.gribData.metadata) return
  
  // Parse time coordinates from GRIB metadata
  const times = props.gribData.metadata.times || []
  
  if (times.length > 0) {
    timeSteps.value = times.map(t => new Date(t).toISOString())
  } else {
    timeSteps.value = [new Date().toISOString()]
  }
  
  currentTimeIndex.value = 0
}
```

### 2. Dynamic Forecast Hour Calculation

**Issue**: Hard-coded 3-hour interval assumption
**Location**: `frontend/app/components/MapViewer.vue`, lines 236-239

**Current Code:**
```javascript
const forecastHour = computed(() => {
  if (timeSteps.value.length === 0) return null
  return currentTimeIndex.value * 3 // Assuming 3-hour intervals
})
```

**Proposed Enhancement:**
```javascript
const forecastHour = computed(() => {
  if (timeSteps.value.length === 0) return null
  if (!props.gribData?.metadata?.forecast_hours) {
    // Fallback: calculate from time differences
    return calculateForecastHour(currentTimeIndex.value)
  }
  return props.gribData.metadata.forecast_hours[currentTimeIndex.value]
})

const calculateForecastHour = (index: number) => {
  if (index === 0) return 0
  const startTime = new Date(timeSteps.value[0])
  const currentTime = new Date(timeSteps.value[index])
  return Math.round((currentTime - startTime) / (1000 * 60 * 60))
}
```

### 3. Wind Direction Formula Correction

**Issue**: Wind direction calculation doesn't follow standard convention
**Location**: `frontend/app/components/MapViewer.vue`, line 595

**Current Code:**
```javascript
const direction = (Math.atan2(u, v) * 180 / Math.PI + 180) % 360
```

**Proposed Enhancement:**
```javascript
// Meteorological convention: direction FROM which wind is blowing
const direction = (Math.atan2(-u, -v) * 180 / Math.PI + 180) % 360

// Alternative: Add configuration option
const getWindDirection = (u: number, v: number, convention: 'from' | 'to' = 'from') => {
  if (convention === 'from') {
    return (Math.atan2(-u, -v) * 180 / Math.PI + 180) % 360
  } else {
    return (Math.atan2(u, v) * 180 / Math.PI + 180) % 360
  }
}
```

### 4. Standard Wind Barb Notation

**Issue**: Wind barb flags use non-standard increments
**Location**: `frontend/app/components/MapViewer.vue`, line 626

**Current Code:**
```javascript
const flagCount = Math.floor(speed / 5) // 1 flag per 5 m/s
```

**Proposed Enhancement:**
```javascript
// Convert m/s to knots for standard notation
const speedKnots = speed * 1.94384

// Standard barb components
const pennants = Math.floor(speedKnots / 50)
const longBarbs = Math.floor((speedKnots % 50) / 10)
const shortBarbs = Math.floor((speedKnots % 10) / 5)

// Draw components in order from staff end
drawWindBarbComponents(lat, lon, direction, pennants, longBarbs, shortBarbs)
```

### 5. Robust Layer Detection

**Issue**: Using private property `_url` for tile layer detection
**Location**: `frontend/app/components/MapViewer.vue`, line 553

**Current Code:**
```javascript
mapInstance.value.eachLayer((layer: any) => {
  if (layer._url === undefined) { // Not a tile layer
    mapInstance.value.removeLayer(layer)
  }
})
```

**Proposed Enhancement:**
```javascript
// Import Leaflet types
import type * as L from 'leaflet'

// More robust detection
mapInstance.value.eachLayer((layer: any) => {
  // Check if it's NOT a tile layer using instanceof
  if (!(layer instanceof L.TileLayer)) {
    mapInstance.value.removeLayer(layer)
  }
})

// Or use marker/feature tracking
const dataLayers = ref<any[]>([])

const addDataLayer = (layer: any) => {
  dataLayers.value.push(layer)
  layer.addTo(mapInstance.value)
}

const clearDataLayers = () => {
  dataLayers.value.forEach(layer => mapInstance.value.removeLayer(layer))
  dataLayers.value = []
}
```

### 6. Named Constants

**Issue**: Magic numbers throughout code
**Locations**: Various

**Proposed Enhancement:**
```javascript
// Add constants at top of script
const CONSTANTS = {
  MS_TO_KMH: 3.6,
  MS_TO_KNOTS: 1.94384,
  KNOTS_TO_MS: 0.514444,
  WIND_BARB: {
    SHORT_BARB_KNOTS: 5,
    LONG_BARB_KNOTS: 10,
    PENNANT_KNOTS: 50
  },
  BARB_LENGTH_PX: 20,
  FLAG_LENGTH_PX: 10,
  SAMPLING: {
    POINTS_STEP: 50,
    BARBS_STEP: 20
  }
}

// Usage
const speedKmh = speed * CONSTANTS.MS_TO_KMH
const barbLength = CONSTANTS.BARB_LENGTH_PX
```

## Wind Barb Library Integration

**Goal**: Use professional wind barb rendering library

**Options:**
1. **Leaflet.windbarb** plugin
2. **d3-wind-barbs** with D3.js
3. **Custom Canvas renderer** for performance

**Benefits:**
- Standard meteorological notation
- Better performance with many barbs
- Configurable styling
- Proper speed increments

**Implementation Example:**
```javascript
// Install: npm install leaflet-windbarb
import 'leaflet-windbarb'

const plotWindBarbs = () => {
  const windBarbLayer = L.windBarbLayer(windData, {
    pointStyle: {
      color: speed => getColorForValue(speed),
      weight: 2
    },
    barbStyle: 'standard', // or 'simple', 'detailed'
    units: 'kt' // or 'ms', 'mph'
  })
  
  windBarbLayer.addTo(mapInstance.value)
}
```

## Documentation Enhancements

### Interactive Examples

**Goal**: Add live examples to documentation

**Tasks:**
- [ ] Create sample GRIB files with multiple time steps
- [ ] Add animated GIFs showing features
- [ ] Record video tutorials
- [ ] Create interactive CodeSandbox demos

### Code Examples

**Goal**: Provide working code snippets

**Tasks:**
- [ ] Add example API calls
- [ ] Show data structure examples
- [ ] Provide frontend integration examples
- [ ] Create troubleshooting flowcharts

## Testing Enhancements

### Unit Tests

**Goal**: Test timeline and wind barb functions

**Tasks:**
- [ ] Test time parsing from metadata
- [ ] Test wind direction calculations
- [ ] Test color scale mappings
- [ ] Test animation controls
- [ ] Test wind barb drawing

**Example Test:**
```javascript
describe('Wind Direction Calculation', () => {
  it('should calculate north wind correctly', () => {
    const direction = getWindDirection(0, -5) // u=0, v=-5 (from north)
    expect(direction).toBe(0)
  })
  
  it('should calculate east wind correctly', () => {
    const direction = getWindDirection(-5, 0) // u=-5, v=0 (from east)
    expect(direction).toBe(90)
  })
})
```

### Integration Tests

**Goal**: Test with real GRIB files

**Tasks:**
- [ ] Test multi-time GFS file
- [ ] Test HRRR wind file
- [ ] Test animation playback
- [ ] Test visualization switching
- [ ] Performance testing with large files

## Performance Optimizations

### Canvas Rendering

**Goal**: Improve performance for large datasets

**Current**: Each data point is a separate Leaflet marker
**Proposed**: Use Canvas renderer for data points and wind barbs

**Benefits:**
- Handle thousands of points
- Smooth animations
- Lower memory usage
- Faster re-rendering

### Web Workers

**Goal**: Offload data processing

**Tasks:**
- [ ] Move wind barb calculations to worker
- [ ] Process GRIB data in background
- [ ] Parallelize color mapping

### Caching

**Goal**: Reduce redundant calculations

**Tasks:**
- [ ] Cache rendered frames
- [ ] Memoize color calculations
- [ ] Store processed data layers

## User Experience Enhancements

### Keyboard Shortcuts

**Goal**: Improve usability

**Shortcuts:**
- Space: Play/Pause
- Left/Right Arrow: Previous/Next step
- Home/End: First/Last step
- +/-: Speed up/slow down
- P: Toggle Points/Barbs
- C: Cycle color schemes

### Touch Controls

**Goal**: Mobile-friendly timeline

**Features:**
- Swipe left/right for time navigation
- Pinch to adjust animation speed
- Tap to play/pause
- Long press for details

### Accessibility

**Goal**: WCAG compliance

**Tasks:**
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] High contrast mode
- [ ] Focus indicators
- [ ] ARIA labels

## Priority Levels

### High Priority
1. ✅ Basic timeline scrubber UI (DONE)
2. ✅ Wind barbs visualization (DONE)
3. ✅ Color scales (DONE)
4. ✅ Documentation (DONE)
5. 🔄 Multi-time backend support
6. 🔄 Wind direction formula correction

### Medium Priority
7. Dynamic time parsing
8. Standard wind barb notation
9. Named constants
10. Robust layer detection
11. Unit tests

### Low Priority
12. Wind barb library integration
13. Canvas rendering
14. Web workers
15. Keyboard shortcuts
16. Touch controls
17. Interactive documentation

## Contributing

To work on these improvements:

1. Choose a task from this list
2. Create a feature branch
3. Implement with tests
4. Update documentation
5. Submit PR referencing this TODO

## Notes

- Current implementation provides working baseline
- Enhancements can be added incrementally
- Backwards compatibility should be maintained
- Document any breaking changes

## Related Issues

Link GitHub issues here as they're created for specific enhancements.

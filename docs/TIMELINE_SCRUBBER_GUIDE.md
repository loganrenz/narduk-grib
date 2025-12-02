# Timeline Scrubber and Wind Barbs Visualization Guide

## Overview

The GRIB Viewer now includes advanced timeline controls and wind barb visualization for meteorological data. This guide explains how to use these features to analyze time-series weather data and visualize wind patterns.

## Timeline Scrubber

### What is the Timeline Scrubber?

The timeline scrubber is an interactive control that allows you to navigate through time-series GRIB data. Many weather models provide forecasts at multiple time steps (e.g., hourly, 3-hourly), and the scrubber lets you view each time step individually or animate through them.

### Features

1. **Slider Control**: Drag the slider to move between time steps
2. **Play/Pause**: Automatically cycle through time steps
3. **Speed Control**: Adjust animation speed (0.5x, 1x, 2x)
4. **Time Display**: Shows current time and forecast hour
5. **Step Counter**: Displays current step (e.g., "5/24" for step 5 of 24)

### Using the Timeline Scrubber

#### Basic Navigation

1. **Load a GRIB File**: Upload or download a GRIB file with multiple time steps
2. **View the Data**: Click the "View" button on your file
3. **Locate the Timeline**: The timeline scrubber appears below the map
4. **Drag the Slider**: Move the slider left/right to change time steps

```
Timeline
▶ Play  [1x ▼]

Time Step: |━━━●━━━━━━━━━━━━━━━━━━━| 5/24

     2025-12-01 03:00:00 UTC
        Forecast Hour: +3h
```

#### Animation Controls

**Play/Pause Button**
- Click "▶ Play" to start automatic animation
- Click "⏸ Pause" to stop animation
- The map updates automatically as time advances

**Speed Control**
- Select from dropdown: 0.5x, 1x, or 2x
- 0.5x = Slow (2 seconds per step)
- 1x = Normal (1 second per step)
- 2x = Fast (0.5 seconds per step)

**Example Use Cases:**
- Monitor storm development over time
- Watch temperature changes throughout the day
- Track wind pattern shifts
- Compare forecast hours

### Understanding the Time Display

**Current Time**: Shows the valid time for the displayed data
- Format: `2025-12-01 03:00:00 UTC`
- Updates as you navigate through steps

**Forecast Hour**: Shows hours ahead of analysis time
- Format: `+3h`, `+6h`, `+12h`, etc.
- Helps understand lead time of forecast

## Wind Barbs Visualization

### What are Wind Barbs?

Wind barbs are meteorological symbols that show wind direction and speed in a single graphic. They're standard notation used by meteorologists worldwide.

### Reading Wind Barbs

**Components:**
1. **Staff**: A line pointing in the direction the wind is coming FROM
2. **Barbs**: Short lines perpendicular to the staff indicating speed
3. **Pennants**: Triangular flags for high winds

**Speed Indicators:**
- Short barb: 5 knots (2.5 m/s)
- Long barb: 10 knots (5 m/s)
- Pennant: 50 knots (25 m/s)

**Direction:**
- The staff points TOWARD where the wind is coming FROM
- A wind barb pointing north means wind FROM the north (going south)

**Examples:**

```
    |           Calm (0 m/s)
    
   |/           5 knots (wind barb)
   
   |//          10 knots (two barbs)
   
   |▸           50 knots (pennant)
   
  ⟩|//          60 knots (pennant + two barbs)
```

### Enabling Wind Barbs

1. **Load Wind Data**: Your GRIB file must contain u and v wind components
   - Variables: `u10`, `v10` (10m winds) or `u`, `v` (upper-level winds)

2. **Switch Visualization Type**:
   - Locate "Visualization Type" selector
   - Click "Wind Barbs" button
   - Map switches from colored points to wind barbs

```
Visualization Type:  [Points]  [Wind Barbs]
```

3. **Interpret the Map**:
   - Each wind barb shows local wind conditions
   - Color indicates wind speed (blue=light, red=strong)
   - Barbs/pennants show exact speed
   - Staff direction shows wind origin

### Wind Barb Color Coding

The wind barbs are color-coded by wind speed for easy visualization:

**Color Scale:**
- **Light Blue** (0-5 m/s): Gentle breeze
- **Blue** (5-10 m/s): Moderate wind
- **Dark Blue** (10-15 m/s): Fresh wind
- **Purple** (15-20 m/s): Strong wind
- **Red** (>20 m/s): Very strong/gale force

### Clicking Wind Barbs

Click on any wind barb to see detailed information:
```
Wind: 12.5 m/s
Direction: 245° (WSW)
```

## Enhanced Color Scales

### Temperature Coloring

For temperature variables (tmp, t2m):

**Color Progression:** Blue → Cyan → Green → Yellow → Orange → Red

```
Freezing     Cool        Mild       Warm        Hot
   ↓          ↓           ↓          ↓           ↓
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Blue    Cyan    Green   Yellow   Orange   Red
 -40°C   -20°C    0°C     20°C     35°C    50°C
```

### Wind Speed Coloring

For wind variables (wind, u10, v10):

**Color Progression:** Light Blue → Blue → Dark Blue

```
 Calm       Light      Moderate    Strong
   ↓          ↓           ↓          ↓
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Light       Blue        Dark
  Blue                   Blue
  0 m/s      5 m/s      15 m/s    25 m/s
```

### Pressure Coloring

For pressure variables (pres, mslp):

**Color Progression:** Purple → White → Orange

```
  Low        Normal      High
   ↓           ↓           ↓
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Purple      White      Orange
  980       1013        1040
  hPa        hPa         hPa
```

## Color Legend

The color legend appears below the map and shows:

1. **Gradient Bar**: Visual representation of color scale
2. **Min Value**: Lowest value in dataset with unit
3. **Mid Value**: Middle of range
4. **Max Value**: Highest value in dataset with unit
5. **Variable Name**: Currently displayed variable
6. **Visualization Info**: What's being shown

**Example:**
```
Color Scale
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Blue              Green              Red

250.0 K          280.0 K          310.0 K

Map shows t2m data. Use the map controls to zoom and pan.
```

## Use Cases and Examples

### Example 1: Tracking a Storm System

**Goal:** Watch a low-pressure system develop and move

1. Load GFS forecast GRIB file (24-hour forecast)
2. View the file - map shows initial conditions
3. Click "▶ Play" to animate
4. Watch the pressure patterns evolve
5. Use slider to jump to specific times
6. Zoom in on areas of interest

**What to Look For:**
- Pressure dropping (colors shift to purple)
- Wind barbs converging toward center
- Wind speeds increasing (barbs lengthen)
- System movement over time

### Example 2: Analyzing Wind Patterns

**Goal:** Understand wind flow at different levels

1. Load GRIB with u/v wind components
2. Switch to "Wind Barbs" visualization
3. Observe wind direction patterns
4. Look for:
   - **Convergence**: Winds from different directions meeting
   - **Divergence**: Winds spreading apart
   - **Rotation**: Circular patterns (cyclones)
   - **Shear**: Wind direction changing with location

**Example Patterns:**
```
   Northern Hemisphere Cyclone
   
   ↖  ↑  ↗         Winds rotating
   ←  ⊙  →         counter-clockwise
   ↙  ↓  ↘         around low pressure
```

### Example 3: Temperature Changes Through the Day

**Goal:** See diurnal temperature variation

1. Load hourly GFS temperature forecast
2. Start at sunrise (06:00 UTC)
3. Use timeline scrubber to advance hour by hour
4. Watch colors change from blue → green → yellow → red
5. Note maximum temperature timing
6. Observe cooling trend toward evening

**Typical Pattern:**
- 06:00: Cool (blue/cyan) - sunrise
- 12:00: Warming (green/yellow) - midday
- 18:00: Hot (yellow/red) - afternoon peak
- 00:00: Cooling (green/blue) - nighttime

### Example 4: Forecast Verification

**Goal:** Compare forecast accuracy at different lead times

1. Load multiple forecast initializations
2. View +6h forecast from Day 1
3. Note predicted conditions
4. Load Day 2 file
5. Compare +6h with +30h forecast
6. Use slider to find same valid time
7. Check differences in:
   - Temperature values
   - Wind speeds
   - Pressure patterns

## Tips and Best Practices

### Performance

1. **Large Files**: Files with many time steps may take longer to load
2. **Sampling**: Wind barbs are sampled (not every grid point shown)
3. **Animation**: Pause animation when zooming/panning
4. **Browser**: Use modern browser for best performance

### Interpretation

1. **Wind Direction**: Remember barbs point WHERE wind comes FROM
2. **Units**: Check units in legend (K, °C, m/s, knots, hPa)
3. **Resolution**: Grid spacing affects detail level
4. **Time Zone**: Times shown in UTC (add/subtract for local)

### Visualization Selection

**Use Points When:**
- Analyzing temperature, pressure, humidity
- Need to see all grid points
- Working with scalar fields
- Making precise measurements

**Use Wind Barbs When:**
- Analyzing wind flow patterns
- Looking for convergence/divergence
- Understanding circulation
- Working with vector fields

## Keyboard Shortcuts

While using the timeline scrubber:

- **Space**: Play/Pause animation
- **Left Arrow**: Previous time step
- **Right Arrow**: Next time step
- **Home**: Jump to first time step
- **End**: Jump to last time step
- **+**: Increase animation speed
- **-**: Decrease animation speed

*(Note: Keyboard shortcuts may require focus on timeline element)*

## Troubleshooting

### Timeline Doesn't Appear

**Cause**: GRIB file has only one time step
**Solution**: Download multi-time forecast file

### Wind Barbs Not Showing

**Causes:**
1. File doesn't contain u/v components
2. Variable names not recognized
3. Data is NULL/missing

**Solutions:**
1. Check file contains wind variables (u10, v10, u, v)
2. Use "Points" visualization
3. Try different GRIB file

### Animation is Choppy

**Causes:**
1. Too many data points
2. Complex rendering
3. Slow computer/browser

**Solutions:**
1. Reduce animation speed
2. Close other browser tabs
3. Use smaller domain/lower resolution file

### Colors Look Wrong

**Cause**: Auto-scaling to data range
**Solution**: This is normal - legend shows actual range

### Can't Read Wind Speed

**Cause**: Wind barbs are meteorological notation
**Solution**: Click on barb for exact values, or use this guide

## Advanced Features

### Multiple Variables

If your GRIB file has multiple variables:
1. Temperature and wind can be shown simultaneously
2. Color shows temperature
3. Barbs show wind
4. Select primary variable from dropdown

### Forecast Hour Display

The forecast hour (+3h, +6h, etc.) helps:
- Understand forecast lead time
- Compare different models
- Assess forecast confidence
- Plan timing of events

Shorter lead times (+0h to +12h) generally more accurate.
Longer lead times (+72h to +240h) show trends but less detail.

### Layer Control (Future Enhancement)

Coming soon:
- Toggle multiple data layers
- Overlay temperature + wind
- Show pressure contours
- Add precipitation shading

## Summary

The timeline scrubber and wind barbs make GRIB Viewer a powerful tool for meteorological analysis:

✅ **Navigate** through forecast time steps
✅ **Animate** to watch weather evolution
✅ **Analyze** wind patterns with standard notation
✅ **Interpret** data with professional color scales
✅ **Compare** different forecast times
✅ **Understand** weather system development

Master these tools to get the most from your GRIB data!

## Related Documentation

- **USER_MANUAL.md**: Complete application guide
- **TESTING.md**: Test file information
- **README.md**: Project overview

## Support

For issues or questions about timeline/wind features:
1. Check this guide
2. Review example use cases
3. Try with test files in `/test_data`
4. Report issues with specific GRIB files

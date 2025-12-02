# GRIB Viewer User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Working with GRIB Files](#working-with-grib-files)
4. [Viewing GRIB Data](#viewing-grib-data)
5. [Map Visualization](#map-visualization)
6. [Test Data](#test-data)
7. [Troubleshooting](#troubleshooting)

## Introduction

GRIB Viewer is a modern web-based application for viewing and analyzing GRIB (GRIdded Binary) meteorological data files. It provides an intuitive interface for uploading, downloading, and visualizing weather model data from various sources.

### Key Features
- Upload GRIB files from your computer
- Download GRIB files directly from URLs
- View comprehensive metadata and variables
- Interactive map visualization with multiple provider options
- Support for GRIB1 and GRIB2 formats
- Compatible with major weather models (GFS, NAM, HRRR, RAP, etc.)

## Getting Started

### Accessing the Application

1. Open your web browser
2. Navigate to the GRIB Viewer URL (default: `http://localhost:3000` for local development)
3. You'll see the main interface with two tabs:
   - **Browse Files**: View and manage uploaded GRIB files
   - **Download GRIB Data**: Download files directly from URLs

![Homepage](https://github.com/user-attachments/assets/49bfd4e7-cc88-4a93-b874-9c81c8be72e4)
*Figure 1: GRIB Viewer homepage showing the upload interface*

## Working with GRIB Files

### Uploading GRIB Files

There are two ways to upload GRIB files:

#### Method 1: Drag and Drop
1. Locate your GRIB file on your computer
2. Drag the file to the dashed upload area
3. Drop the file to begin uploading
4. Wait for the upload to complete

#### Method 2: Click to Browse
1. Click on the dashed upload area
2. Navigate to your GRIB file in the file browser
3. Select the file and click "Open"
4. Wait for the upload to complete

### Downloading GRIB Files from URLs

1. Click the "Download GRIB Data" tab
2. Enter the URL of the GRIB file in the text box
3. Click the "Download" button
4. The file will be downloaded and automatically added to your file list

**Supported URLs:**
- NOAA NOMADS: `https://nomads.ncep.noaa.gov/...`
- CMC Datamart: `https://dd.weather.gc.ca/...`
- NOAA NCEI Archive: `https://www.ncei.noaa.gov/...`
- Any publicly accessible GRIB file URL

### Managing GRIB Files

Once files are uploaded, they appear in the "GRIB Files" section:

![File List](https://github.com/user-attachments/assets/bd9f3caf-532b-4b39-b298-21c80c4ecb8d)
*Figure 2: List of uploaded GRIB files with metadata*

Each file entry shows:
- **Filename**: Original or generated filename
- **Size**: File size in KB or MB
- **Upload Time**: Date and time of upload
- **Actions**: 
  - **View**: Open the file to view data and maps
  - **Delete**: Remove the file from storage

## Viewing GRIB Data

### Opening a GRIB File

1. Locate your file in the "GRIB Files" list
2. Click the blue "View" button
3. The GRIB Data Viewer panel will load with file information

### Understanding the Data View

The GRIB Data Viewer shows:

#### File Information
- Filename and basic metadata
- List of available variables (e.g., temperature, pressure, humidity)
- Data dimensions (latitude, longitude, levels)

#### Variable Selection
- Use the dropdown menu to select which variable to view
- Different variables may have different dimensions and ranges
- The map will update to show the selected variable

#### Coordinates
- Latitude and longitude ranges
- Pressure levels (if applicable)
- Time steps (if multiple times are available)

#### Attributes
- GRIB edition (1 or 2)
- Data source (e.g., NOAA, CMC)
- Model name and configuration
- Forecast time and validity

## Map Visualization

### Map Providers

GRIB Viewer supports three map visualization providers:

#### 1. Leaflet (Default)
- Uses OpenStreetMap tiles
- No API key required
- Works out of the box
- Best for general use

#### 2. Mapbox
- Professional map styling
- Requires Mapbox API token
- Set `NUXT_PUBLIC_MAPBOX_TOKEN` environment variable
- Get token from: https://account.mapbox.com/access-tokens/

#### 3. Apple MapKit JS
- Apple Maps integration
- Requires MapKit JS token
- Set `NUXT_PUBLIC_MAPKIT_TOKEN` environment variable
- Get token from: https://developer.apple.com/maps/

### Switching Map Providers

1. Locate the "Map Provider" dropdown in the Map Viewer section
2. Select your preferred provider:
   - Leaflet (OSM) - Default
   - Mapbox
   - Apple MapKit JS
3. The map will reload with the new provider

**Note:** If you select Mapbox or MapKit JS without configuring the API token, you'll see a warning message.

### Interacting with the Map

- **Zoom**: Use mouse wheel or +/- buttons
- **Pan**: Click and drag the map
- **Data Points**: Colored markers represent data values
  - Blue: Moderate values
  - Red: High values
  - Green: Low values
- **Popups**: Click on a data point to see its exact value

## Test Data

### Available Test Files

The `/test_data` directory contains real GRIB files from various weather model sources for testing:

#### 1. GFS Sample (gfs_sample.grib2)
- **Source**: NOAA GFS (Global Forecast System)
- **Size**: ~850 KB
- **Variables**: 2-meter temperature (t2m)
- **Resolution**: 0.25° (approximately 25 km)
- **Coverage**: Global
- **Dimensions**: 721 latitudes × 1440 longitudes
- **Use Case**: Quick testing of global model data

**Data Structure:**
```json
{
  "variables": ["t2m"],
  "dimensions": {
    "latitude": 721,
    "longitude": 1440
  },
  "coordinates": {
    "latitude": [90.0, 89.75, ..., -90.0],
    "longitude": [0.0, 0.25, ..., 359.75]
  }
}
```

#### 2. NAM Sample (nam_sample.grib2 / nam_sample_small.grib2)
- **Source**: NOAA NAM (North American Mesoscale)
- **Size**: ~54 MB (full) / ~10 MB (sample)
- **Coverage**: North America
- **Resolution**: 12 km
- **Use Case**: Testing regional model data
- **Contains**: Multiple atmospheric variables and levels

#### 3. HRRR Sample (hrrr_sample.grib2 / hrrr_sample_small.grib2)
- **Source**: NOAA HRRR (High Resolution Rapid Refresh)
- **Size**: ~136 MB (full) / ~10 MB (sample)
- **Coverage**: Continental United States (CONUS)
- **Resolution**: 3 km
- **Use Case**: Testing high-resolution regional forecasts
- **Update Frequency**: Hourly

#### 4. GFS Archived (gfs_archived.grb2)
- **Source**: NOAA NCEI Archive
- **Date**: January 1, 2020
- **Size**: ~86 MB
- **Use Case**: Stable reference file for regression testing
- **Contains**: Complete GFS analysis dataset

### Using Test Files

To test the application with the provided files:

1. Navigate to the `/test_data` directory
2. Select a file to upload using the web interface
3. Or use the API to upload programmatically:

```bash
curl -X POST http://localhost:8000/api/grib/upload \
  -F "file=@test_data/gfs_sample.grib2"
```

### Updating Test Files

To get the latest data from weather model sources:

```bash
cd test_data

# Update GFS sample (filtered for 2m temperature)
curl "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.$(date -u +%Y%m%d)%2F00%2Fatmos&file=gfs.t00z.pgrb2.0p25.f000&var_TMP=on&lev_2_m_above_ground=on" -o gfs_sample.grib2

# Update NAM sample
curl "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nam/prod/nam.$(date -u +%Y%m%d)/nam.t00z.awphys00.tm00.grib2" -o nam_sample.grib2

# Update HRRR sample
curl "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.$(date -u +%Y%m%d)/conus/hrrr.t00z.wrfsfcf00.grib2" -o hrrr_sample.grib2
```

See `/test_data/README.md` for more details on test files.

## Troubleshooting

### File Won't Upload
- **Check file format**: Ensure the file is a valid GRIB or GRIB2 file
- **Check file size**: Very large files (>500 MB) may timeout
- **Check network**: Ensure stable internet connection

### Data Not Displaying
- **Wait for loading**: Large files may take time to process
- **Check file validity**: Some corrupted GRIB files may not parse correctly
- **Check browser console**: Press F12 to view error messages

### Map Not Loading
- **Check provider configuration**: Ensure API tokens are set for Mapbox/MapKit
- **Try Leaflet**: Switch to Leaflet (default) which doesn't require tokens
- **Check browser**: Ensure JavaScript is enabled
- **Check network**: Leaflet requires internet access for map tiles

### Download from URL Fails
- **Check URL accessibility**: Ensure the URL is publicly accessible
- **Check file format**: Some servers may not serve GRIB files correctly
- **Check server**: Some weather model servers may be temporarily unavailable
- **Security**: URLs pointing to private IPs or localhost are blocked for security

### Slow Performance
- **Large files**: Files over 100 MB may be slow to process
- **Complex data**: Files with many variables/levels take longer
- **Map rendering**: Displaying thousands of data points can be slow
- **Solution**: Filter to specific variables or use smaller sample files

## Support and Resources

### Documentation
- **TESTING.md**: Comprehensive testing guide
- **README.md**: Project overview and setup instructions
- **SECURITY_SUMMARY.md**: Security features and best practices
- **test_data/README.md**: Information about test GRIB files

### Data Sources
- **NOAA NOMADS**: https://nomads.ncep.noaa.gov/
- **CMC Datamart**: https://dd.weather.gc.ca/
- **NOAA NCEI**: https://www.ncei.noaa.gov/
- **LuckGrib Models**: https://www.luckgrib.com/models/

### API Documentation
When the backend is running, access interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Getting Help
For issues, questions, or contributions:
1. Check the documentation files
2. Review the API documentation
3. Check the GitHub repository issues
4. Submit a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

## Advanced Features

### Timeline Scrubber

For GRIB files with multiple time steps (forecast hours), the timeline scrubber provides:
- Interactive slider to navigate between time steps
- Play/pause animation controls
- Speed adjustment (0.5x, 1x, 2x)
- Current time and forecast hour display
- Automatic cycling through forecast times

**See [TIMELINE_SCRUBBER_GUIDE.md](TIMELINE_SCRUBBER_GUIDE.md) for comprehensive documentation with examples.**

### Wind Barbs Visualization

For wind data (u/v components), wind barbs show:
- Wind direction (staff points FROM wind origin)
- Wind speed (barbs and pennants)
- Color-coded wind intensity
- Standard meteorological notation

**Key Features:**
- Toggle between Points and Wind Barbs
- Click barbs for exact wind values
- Color scale from light blue (calm) to red (strong)
- Professional meteorological symbols

**See [TIMELINE_SCRUBBER_GUIDE.md](TIMELINE_SCRUBBER_GUIDE.md) for detailed wind barb interpretation.**

### Enhanced Color Scales

The map uses meteorologically appropriate color scales:

**Temperature**: Blue → Cyan → Green → Yellow → Orange → Red  
**Wind Speed**: Light Blue → Blue → Dark Blue  
**Pressure**: Purple → White → Orange

Each variable type gets an optimized color progression for easy interpretation.

## Appendix: Supported GRIB Models

The application supports GRIB files from all major weather model sources:

### Global Models (Public Access)
- GFS, GDPS, GFS Ensemble, CMC Ensemble
- RTOFS Global, HYCOM, OSCAR (ocean currents)
- ASCAT (satellite wind observations)
- CFS (Climate Forecast System)

### Regional Models (Public Access)
- HRRR, RAP, NAM, HRDPS
- NDFD, NBM, WW3
- Various OFS and NCOM regional models

### European Models (Require Token)
- ECMWF, ECMWF AIFS, ECMWF Ensemble
- Météo-France Arome, Arpège

See **TESTING.md** for complete list and authentication requirements.

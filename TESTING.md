# Testing Guide

This document describes the testing infrastructure and test coverage for the narduk-grib project.

## Backend Testing

### Prerequisites

Install test dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Running Tests

Run all tests:
```bash
cd backend
pytest
```

Run specific test categories:
```bash
# Unit tests only (no network access required)
pytest -m "not integration"

# Integration tests (may require network access)
pytest -m integration

# Run tests with verbose output
pytest -v

# Run specific test file
pytest test_grib_transformation.py -v
```

### Test Coverage

#### 1. GRIB Transformation Tests (`test_grib_transformation.py`)

Comprehensive tests for GRIB file to JSON transformation:

- **Metadata Extraction**
  - Variable names extraction
  - Dimension information
  - Coordinate arrays
  - Global attributes

- **Data Conversion**
  - Full dataset conversion to JSON
  - Variable filtering
  - Pressure level filtering
  - NaN value handling (converted to None for JSON)
  - Multi-dimensional array conversion to nested lists

- **Coordinate Systems**
  - Proper coordinate serialization
  - Latitude/longitude handling
  - Dimension reporting

- **Error Handling**
  - Non-existent file handling
  - Invalid variable names
  - Graceful error recovery

- **Data Integrity**
  - Value preservation during conversion
  - Coordinate value accuracy
  - Floating-point precision maintenance

All 15 transformation tests pass successfully.

#### 2. GRIB Download Tests (`test_grib_downloads.py`)

Tests for downloading GRIB files from various weather model sources:

- **URL Validation & Security**
  - SSRF protection (blocks private IPs, localhost, loopback)
  - Link-local address rejection
  - Protocol validation (HTTP/HTTPS only)
  - Public URL acceptance

- **File Management**
  - Unique ID generation
  - File size recording
  - Filename extraction from URLs

- **Public Model Sources (Integration Tests)**
  - GFS (Global Forecast System) - NOAA
  - NAM (North American Mesoscale) - NOAA
  - HRRR (High Resolution Rapid Refresh) - NOAA
  - RAP (Rapid Refresh) - NOAA
  - GDPS (Global Deterministic Prediction System) - CMC Canada

- **Authenticated Sources**
  - ECMWF (requires API key) - marked as needing assistance
  - Commercial services - documented as requiring subscription

All unit tests pass. Integration tests are marked to skip if data sources are unavailable.

### Supported GRIB Models

Based on LuckGrib's model list, the following models are documented and testable:

#### Global Models (Public Access)
- **GFS** (Global Forecast System) - NOAA
- **GDPS** (Global Deterministic Prediction System) - CMC Canada
- **GFS Ensemble** - NOAA
- **CMC Ensemble** - Canada
- **RTOFS Global** (Ocean currents) - NOAA
- **HYCOM** (Ocean currents) - Navy Research Lab
- **OSCAR** (Ocean currents) - NASA/NOAA
- **ASCAT** (Satellite wind observations) - EUMETSAT
- **CFS** (Climate Forecast System) - NOAA

#### Regional Models (Public Access)
- **HRRR** (High Resolution Rapid Refresh) - NOAA
- **RAP** (Rapid Refresh) - NOAA
- **NAM** (North American Mesoscale) - NOAA
- **HRDPS** (High Resolution Deterministic Prediction System) - CMC Canada
- **NDFD** (National Digital Forecast Database) - NOAA
- **NBM** (National Blend of Models) - NOAA
- **WW3** (Great Lakes Wave) - NOAA
- Various **OFS** regional ocean models - NOAA
- Various **NCOM** regional models - Navy

#### Ocean/Wave Models (Public Access)
- **WW3** (NOAA global and regional)
- **MFWAM** (Météo-France wave model)
- **Mercator Global** (Ocean currents)

#### European Models (Require Token/Subscription)
- **ECMWF** - Requires API key from ECMWF
- **ECMWF AIFS** (AI Forecasting System) - Requires API key
- **ECMWF Ensemble** - Requires API key
- **Météo-France Arome** - May require authentication
- **Arpège** - May require authentication

#### Commercial Services (Require Subscription)
- **LuckGrib Offshore Service** - Paid subscription
- Various commercial providers - Paid subscriptions

### Authentication Requirements

**No Authentication Required:**
- All NOAA models (GFS, NAM, HRRR, RAP, etc.) - Public via NOMADS
- CMC models (GDPS, HRDPS) - Public via Datamart
- NOAA ocean models (RTOFS, WW3) - Public access
- Navy HYCOM - Public access (some mirrors)

**API Key Required:**
- ECMWF - Register at https://www.ecmwf.int/
- Set `ECMWF_API_KEY` environment variable

**Subscription Required:**
- LuckGrib Offshore - https://offshore.luckgrib.com/
- Premium weather routing services

## Frontend Testing

### Map Provider Support

The frontend supports three map providers with Leaflet as the default:

1. **Leaflet** (Default)
   - Uses OpenStreetMap tiles
   - No API key required
   - Fully functional out of the box

2. **Mapbox**
   - Requires Mapbox API token
   - Set `NUXT_PUBLIC_MAPBOX_TOKEN` in `.env`
   - Get token from: https://account.mapbox.com/access-tokens/

3. **Apple MapKit JS**
   - Requires MapKit JS token
   - Set `NUXT_PUBLIC_MAPKIT_TOKEN` in `.env`
   - Get token from: https://developer.apple.com/maps/

### Map Provider Configuration

The map provider can be selected via dropdown in the UI. The default is Leaflet.

To configure map providers, copy `.env.example` to `.env` and add your tokens:

```bash
cd frontend
cp .env.example .env
# Edit .env and add your tokens
```

Configuration in `.env`:
```
# Map Provider API Tokens (Optional)
NUXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
NUXT_PUBLIC_MAPKIT_TOKEN=your_mapkit_token_here
```

### Verifying Map Providers

1. **Leaflet (Default)**
   - Start the frontend: `npm run dev`
   - Upload or download a GRIB file
   - Verify the map loads with OpenStreetMap tiles
   - Data points should appear as colored markers

2. **Mapbox**
   - Add Mapbox token to `.env`
   - Select "Mapbox" from the Map Provider dropdown
   - Verify Mapbox map style loads
   - Verify GRIB data is plotted

3. **MapKit JS**
   - Add MapKit token to `.env`
   - Select "Apple MapKit JS" from the Map Provider dropdown
   - Verify Apple Maps loads
   - Verify GRIB data is plotted

## Continuous Integration

The test suite is designed to work in CI/CD environments:

- Unit tests run without external dependencies
- Integration tests gracefully skip if data sources are unavailable
- No hardcoded dates or URLs that become stale
- Security tests validate SSRF protection

## Test Markers

Tests use pytest markers for categorization:

- `@pytest.mark.unit` - Unit tests (no external dependencies)
- `@pytest.mark.integration` - Integration tests (may require network)
- `@pytest.mark.requires_token` - Tests requiring API tokens
- `@pytest.mark.slow` - Tests that may take longer to execute

## Known Limitations

1. Integration tests for GRIB downloads depend on external data availability
2. Some weather model URLs change daily (date-specific)
3. ECMWF tests require manual API key configuration
4. Commercial service tests cannot be automated without subscriptions

## Contributing

When adding new GRIB model support:

1. Add integration test to `test_grib_downloads.py`
2. Document authentication requirements
3. Mark tests appropriately with pytest markers
4. Update this document with model information

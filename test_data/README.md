# Test GRIB Files

This directory contains real GRIB files downloaded from various weather model sources for testing purposes.

## Files

### gfs_sample.grib2 (Included in Repository)
- **Source**: NOAA GFS (Global Forecast System)
- **URL Pattern**: `https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl`
- **Description**: Small filtered GFS file containing 2-meter temperature data at 0.25° resolution
- **Size**: ~850 KB
- **Variables**: Temperature at 2m above ground
- **Use Case**: Quick testing of global model data
- **Status**: ✅ Included in git repository

### nam_sample.grib2 (Download Required)
- **Source**: NOAA NAM (North American Mesoscale)
- **URL**: `https://nomads.ncep.noaa.gov/pub/data/nccf/com/nam/prod/`
- **Description**: NAM model physics file for North American region
- **Size**: ~54 MB
- **Use Case**: Testing regional model data
- **Status**: ⚠️ Too large for GitHub - download using commands below

### hrrr_sample.grib2 (Download Required)
- **Source**: NOAA HRRR (High Resolution Rapid Refresh)
- **URL**: `https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/`
- **Description**: HRRR surface forecast for CONUS (Continental US)
- **Size**: ~136 MB
- **Resolution**: 3 km
- **Use Case**: Testing high-resolution regional forecasts
- **Status**: ⚠️ Too large for GitHub - download using commands below

### gfs_archived.grb2 (Download Required)
- **Source**: NOAA NCEI Archive
- **URL**: `https://www.ncei.noaa.gov/thredds/fileServer/model-gfs-g4-anl-files-old/`
- **Description**: Archived GFS analysis file from January 1, 2020
- **Size**: ~86 MB
- **Use Case**: Stable reference file for regression testing
- **Status**: ⚠️ Too large for GitHub - download using commands below

## Note on File Sizes

Only `gfs_sample.grib2` (~850 KB) is included in the repository due to GitHub's file size limits. The larger files (NAM, HRRR, archived GFS) should be downloaded locally when needed for testing.

## Purpose

These files are used for:

1. **Integration Testing**: Verify the backend can parse real GRIB2 files from production sources
2. **Frontend Testing**: Test the web UI with actual meteorological data
3. **Performance Testing**: Benchmark data processing and visualization with real-world file sizes
4. **Documentation**: Generate screenshots and examples for the user manual
5. **Regression Testing**: Ensure new changes don't break compatibility with real data

## Updating Test Files

To refresh the test files with the latest data:

```bash
cd test_data

# Update GFS sample
curl "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.$(date -u +%Y%m%d)%2F00%2Fatmos&file=gfs.t00z.pgrb2.0p25.f000&var_TMP=on&lev_2_m_above_ground=on" -o gfs_sample.grib2

# Update NAM sample
curl "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nam/prod/nam.$(date -u +%Y%m%d)/nam.t00z.awphys00.tm00.grib2" -o nam_sample.grib2

# Update HRRR sample
curl "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.$(date -u +%Y%m%d)/conus/hrrr.t00z.wrfsfcf00.grib2" -o hrrr_sample.grib2
```

## Data Sources

- **NOAA NOMADS**: https://nomads.ncep.noaa.gov/
- **NOAA NCEI**: https://www.ncei.noaa.gov/
- **CMC Datamart**: https://dd.weather.gc.ca/

## License

These GRIB files contain public domain data from NOAA and other government weather services. They are freely available for use in research, education, and commercial applications.

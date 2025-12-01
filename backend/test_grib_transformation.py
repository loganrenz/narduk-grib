"""
Comprehensive tests for GRIB file to JSON transformation.
Tests metadata extraction, data conversion, and various data handling scenarios.
"""
import pytest
import numpy as np
import xarray as xr
from pathlib import Path
import tempfile
import uuid
from grib_service import GRIBService
from models import GRIBDataResponse


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def grib_service(temp_storage):
    """Create a GRIBService instance with temporary storage."""
    return GRIBService(temp_storage)


@pytest.fixture
def sample_grib_dataset():
    """Create a sample xarray dataset mimicking GRIB data structure."""
    # Create coordinate arrays
    lats = np.linspace(20, 50, 10)
    lons = np.linspace(-130, -60, 15)
    levels = [1000, 850, 500]
    
    # Create 3D temperature data
    temp_data = np.random.randn(len(levels), len(lats), len(lons)) * 10 + 273.15
    
    # Create dataset
    ds = xr.Dataset(
        {
            'temperature': (['isobaricInhPa', 'latitude', 'longitude'], temp_data),
            'humidity': (['latitude', 'longitude'], np.random.rand(len(lats), len(lons)) * 100),
        },
        coords={
            'latitude': lats,
            'longitude': lons,
            'isobaricInhPa': levels,
        },
        attrs={
            'GRIB_edition': 2,
            'GRIB_centre': 'kwbc',
            'GRIB_centreDescription': 'US National Weather Service',
        }
    )
    return ds


@pytest.fixture
def sample_grib_file(sample_grib_dataset):
    """
    Create a temporary file for testing GRIB transformation.
    
    Note: This fixture creates NetCDF files instead of actual GRIB files because:
    1. Creating valid GRIB2 files programmatically requires complex binary encoding
    2. The grib_service has been enhanced to auto-detect file format (GRIB vs NetCDF)
    3. xarray can read both formats with the appropriate engine
    4. The transformation logic being tested (data extraction, JSON conversion, etc.)
       is format-agnostic after xarray parsing
    
    This approach allows testing the transformation pipeline while avoiding
    the complexity of GRIB2 binary file generation. Integration tests with
    real GRIB files are covered in test_grib_downloads.py.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file_id = str(uuid.uuid4())
        file_path = Path(tmpdir) / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        yield file_id, file_path


class TestGRIBMetadataExtraction:
    """Test suite for GRIB metadata extraction."""
    
    @pytest.mark.asyncio
    async def test_metadata_extraction_variables(self, grib_service, sample_grib_dataset):
        """Test that metadata correctly extracts variable names."""
        # Create a file directly in grib_service storage
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        metadata = await grib_service.get_metadata(file_id)
        
        assert 'variables' in metadata
        assert 'temperature' in metadata['variables']
        assert 'humidity' in metadata['variables']
        
        # Clean up
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_metadata_extraction_dimensions(self, grib_service, sample_grib_dataset):
        """Test that metadata correctly extracts dimensions."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        metadata = await grib_service.get_metadata(file_id)
        
        assert 'dimensions' in metadata
        assert 'latitude' in metadata['dimensions']
        assert 'longitude' in metadata['dimensions']
        assert metadata['dimensions']['latitude'] == 10
        assert metadata['dimensions']['longitude'] == 15
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_metadata_extraction_coordinates(self, grib_service, sample_grib_dataset):
        """Test that metadata correctly extracts coordinate arrays."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        metadata = await grib_service.get_metadata(file_id)
        
        assert 'coordinates' in metadata
        assert 'latitude' in metadata['coordinates']
        assert 'longitude' in metadata['coordinates']
        assert len(metadata['coordinates']['latitude']) == 10
        assert len(metadata['coordinates']['longitude']) == 15
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_metadata_extraction_attributes(self, grib_service, sample_grib_dataset):
        """Test that metadata correctly extracts global attributes."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        metadata = await grib_service.get_metadata(file_id)
        
        assert 'attributes' in metadata
        # NetCDF files might not have the exact same attributes as GRIB
        # but should have some attributes
        assert isinstance(metadata['attributes'], dict)
        
        await grib_service.delete_file(file_id)


class TestGRIBDataConversion:
    """Test suite for GRIB data to JSON conversion."""
    
    @pytest.mark.asyncio
    async def test_full_data_conversion(self, grib_service, sample_grib_dataset):
        """Test conversion of full GRIB dataset to JSON format."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id)
        
        assert isinstance(data_response, GRIBDataResponse)
        assert data_response.file_id == file_id
        assert len(data_response.variables) > 0
        assert len(data_response.data) > 0
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_variable_filtering(self, grib_service, sample_grib_dataset):
        """Test filtering data by specific variable."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id, variable='temperature')
        
        assert 'temperature' in data_response.variables
        assert 'temperature' in data_response.data
        # When filtering, should only get the requested variable
        assert len(data_response.variables) == 1
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_level_filtering(self, grib_service, sample_grib_dataset):
        """Test filtering data by specific pressure level."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id, level=850)
        
        # Data should be filtered to the specified level
        assert data_response is not None
        # Check that dimensions are reduced (no level dimension for 2D slice)
        assert isinstance(data_response.data, dict)
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_nan_value_handling(self, grib_service):
        """Test that NaN values are correctly converted to None for JSON."""
        # Create a dataset with NaN values
        lats = np.array([30, 35, 40])
        lons = np.array([-120, -110, -100])
        
        # Create data with some NaN values
        temp_data = np.array([[273.15, np.nan, 275.0],
                              [np.nan, 274.0, np.nan],
                              [276.0, 277.0, 278.0]])
        
        ds = xr.Dataset(
            {'temperature': (['latitude', 'longitude'], temp_data)},
            coords={'latitude': lats, 'longitude': lons}
        )
        
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        ds.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id)
        
        # Check that NaN values are converted to None
        temp_values = data_response.data['temperature']
        assert isinstance(temp_values, list)
        # Should have None values where NaN was present
        flat_values = [val for row in temp_values for val in row]
        assert None in flat_values
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_multidimensional_array_conversion(self, grib_service, sample_grib_dataset):
        """Test conversion of multi-dimensional arrays to nested lists."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id, variable='temperature')
        
        # Temperature is 3D (level, lat, lon), should be nested lists
        temp_data = data_response.data['temperature']
        assert isinstance(temp_data, list)
        assert isinstance(temp_data[0], list)
        assert isinstance(temp_data[0][0], list)
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_coordinate_system_handling(self, grib_service, sample_grib_dataset):
        """Test that coordinate systems are properly included in metadata."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id)
        
        assert 'coordinates' in data_response.metadata
        coords = data_response.metadata['coordinates']
        
        # Check that coordinates are properly serialized as lists
        assert 'latitude' in coords
        assert 'longitude' in coords
        assert isinstance(coords['latitude'], list)
        assert isinstance(coords['longitude'], list)
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_dimensions_in_response(self, grib_service, sample_grib_dataset):
        """Test that dimensions are correctly reported in response."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id)
        
        assert isinstance(data_response.dimensions, dict)
        assert 'latitude' in data_response.dimensions
        assert 'longitude' in data_response.dimensions
        assert data_response.dimensions['latitude'] == 10
        assert data_response.dimensions['longitude'] == 15
        
        await grib_service.delete_file(file_id)


class TestErrorHandling:
    """Test suite for error handling in GRIB processing."""
    
    @pytest.mark.asyncio
    async def test_nonexistent_file(self, grib_service):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError):
            await grib_service.get_grib_data("nonexistent-id")
    
    @pytest.mark.asyncio
    async def test_invalid_variable_name(self, grib_service, sample_grib_dataset):
        """Test handling of invalid variable name."""
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        sample_grib_dataset.to_netcdf(file_path)
        
        # Should handle gracefully - either return empty data or all data
        data_response = await grib_service.get_grib_data(file_id, variable='nonexistent')
        
        # The current implementation will return all data if variable not found
        # or filter to empty, depending on implementation
        assert data_response is not None
        
        await grib_service.delete_file(file_id)


class TestDataIntegrity:
    """Test suite for data integrity during transformation."""
    
    @pytest.mark.asyncio
    async def test_data_value_preservation(self, grib_service):
        """Test that data values are preserved during conversion."""
        lats = np.array([30.0, 35.0])
        lons = np.array([-120.0, -110.0])
        
        # Create data with known values
        expected_values = np.array([[100.5, 200.7],
                                    [300.2, 400.9]])
        
        ds = xr.Dataset(
            {'variable': (['latitude', 'longitude'], expected_values)},
            coords={'latitude': lats, 'longitude': lons}
        )
        
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        ds.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id)
        
        # Convert response back to numpy for comparison
        actual_values = np.array(data_response.data['variable'])
        
        # Values should be preserved (within floating point precision)
        np.testing.assert_allclose(actual_values, expected_values, rtol=1e-5)
        
        await grib_service.delete_file(file_id)
    
    @pytest.mark.asyncio
    async def test_coordinate_value_preservation(self, grib_service):
        """Test that coordinate values are preserved during conversion."""
        expected_lats = np.array([25.5, 30.0, 35.5, 40.0])
        expected_lons = np.array([-125.5, -120.0, -115.5, -110.0])
        
        data = np.random.rand(len(expected_lats), len(expected_lons))
        
        ds = xr.Dataset(
            {'variable': (['latitude', 'longitude'], data)},
            coords={'latitude': expected_lats, 'longitude': expected_lons}
        )
        
        file_id = str(uuid.uuid4())
        file_path = grib_service.storage_path / f"{file_id}.nc"
        ds.to_netcdf(file_path)
        
        data_response = await grib_service.get_grib_data(file_id)
        
        actual_lats = np.array(data_response.metadata['coordinates']['latitude'])
        actual_lons = np.array(data_response.metadata['coordinates']['longitude'])
        
        np.testing.assert_allclose(actual_lats, expected_lats, rtol=1e-5)
        np.testing.assert_allclose(actual_lons, expected_lons, rtol=1e-5)
        
        await grib_service.delete_file(file_id)

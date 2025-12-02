"""
Service for managing and processing GRIB files.
"""
import os
import uuid
import re
import aiofiles
import requests
import cfgrib
import xarray as xr
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse, unquote, parse_qs
from ipaddress import ip_address, IPv4Address, IPv6Address
from fastapi import UploadFile, HTTPException
import logging

from models import GRIBFileInfo, GRIBDataResponse

logger = logging.getLogger(__name__)


class GRIBService:
    """Service for handling GRIB file operations."""
    
    # Supported GRIB file extensions
    GRIB_EXTENSIONS = ['.grib', '.grib2', '.grb', '.grb2', '.nc']
    
    def __init__(self, storage_path: Path):
        """
        Initialize the GRIB service.
        
        Args:
            storage_path: Path to store GRIB files
        """
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"GRIB storage initialized at: {self.storage_path}")
    
    async def list_files(self) -> List[GRIBFileInfo]:
        """
        List all GRIB files in storage.
        
        Returns:
            List of GRIBFileInfo objects
        """
        files = []
        # Check all supported GRIB extensions
        for ext in self.GRIB_EXTENSIONS:
            for file_path in self.storage_path.glob(f"*{ext}"):
                # Skip if already added (in case of duplicate patterns)
                stat = file_path.stat()
                files.append(GRIBFileInfo(
                    id=file_path.stem,
                    filename=file_path.name,
                    size=stat.st_size,
                    uploaded_at=datetime.fromtimestamp(stat.st_ctime),
                    path=str(file_path)
                ))
        # Remove duplicates (in case a file matches multiple patterns)
        seen_ids = set()
        unique_files = []
        for file_info in files:
            if file_info.id not in seen_ids:
                seen_ids.add(file_info.id)
                unique_files.append(file_info)
        return sorted(unique_files, key=lambda x: x.uploaded_at, reverse=True)
    
    async def upload_file(self, file: UploadFile) -> GRIBFileInfo:
        """
        Upload a GRIB file to storage.
        
        Args:
            file: Uploaded file
            
        Returns:
            GRIBFileInfo object
        """
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Determine file extension
        original_name = file.filename or "upload.grib"
        ext = Path(original_name).suffix or ".grib"
        
        # Save file
        file_path = self.storage_path / f"{file_id}{ext}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        stat = file_path.stat()
        return GRIBFileInfo(
            id=file_id,
            filename=original_name,
            size=stat.st_size,
            uploaded_at=datetime.now(),
            path=str(file_path)
        )
    
    def _validate_url(self, url: str) -> None:
        """
        Validate URL to prevent SSRF attacks.
        
        Args:
            url: URL to validate
            
        Raises:
            HTTPException: If URL is invalid or points to internal resources
        """
        try:
            parsed = urlparse(url)
            
            # Only allow http and https schemes
            if parsed.scheme not in ('http', 'https'):
                raise HTTPException(
                    status_code=400, 
                    detail="Only HTTP and HTTPS URLs are allowed"
                )
            
            hostname = parsed.hostname
            if not hostname:
                raise HTTPException(status_code=400, detail="Invalid URL")
            
            # Try to parse as IP address
            try:
                ip = ip_address(hostname)
                
                # Block private, loopback, link-local, and multicast addresses
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot download from private, loopback, link-local, or multicast IP addresses"
                    )
                
                # Block reserved IP ranges
                if ip.is_reserved:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot download from reserved IP addresses"
                    )
                    
            except ValueError:
                # Not an IP address, check hostname patterns
                hostname_lower = hostname.lower()
                
                # Block localhost variants
                if hostname_lower in ('localhost', 'localhost.localdomain'):
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot download from localhost"
                    )
                
                # Block .local domain
                if hostname_lower.endswith('.local'):
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot download from .local domains"
                    )
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}")
    
    async def download_file(self, url: str) -> GRIBFileInfo:
        """
        Download a GRIB file from a URL.
        
        This method intentionally allows downloading from user-provided URLs
        but implements comprehensive SSRF protection through URL validation.
        
        Args:
            url: URL to download from
            
        Returns:
            GRIBFileInfo object
        """
        # Validate URL to prevent SSRF - blocks private IPs, localhost, etc.
        self._validate_url(url)
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Download file with timeout to prevent hanging
        response = requests.get(url, stream=True, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        # Determine filename and extension from URL or Content-Type
        parsed_url = urlparse(url)
        
        # Try to get filename from Content-Disposition header
        filename = None
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            match = re.search(r'filename[*]?=([^;]+)', content_disposition)
            if match:
                filename = unquote(match.group(1).strip('"\''))
        
        # If not in header, try to extract from URL
        if not filename:
            url_path = unquote(parsed_url.path)
            filename = Path(url_path).name if url_path else None
            # If it's a CGI script, check query params for file parameter
            if filename and filename.endswith('.pl'):
                query_params = parse_qs(parsed_url.query)
                if 'file' in query_params:
                    filename = query_params['file'][0]
        
        # Determine extension
        if filename:
            ext = Path(filename).suffix
            # Validate extension is a supported GRIB extension
            if ext not in self.GRIB_EXTENSIONS:
                # Default to .grib2 for GRIB files
                ext = '.grib2'
        else:
            # Check Content-Type to determine extension
            content_type = response.headers.get('Content-Type', '').lower()
            if 'grib' in content_type or 'octet-stream' in content_type:
                ext = '.grib2'
            else:
                ext = '.grib2'  # Default for GRIB downloads
        
        # Use a reasonable default filename if still not set
        if not filename:
            filename = f"grib_download_{file_id}{ext}"
        
        # Ensure filename has correct extension
        if not filename.endswith(ext):
            filename = f"{Path(filename).stem}{ext}"
        
        file_path = self.storage_path / f"{file_id}{ext}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                await f.write(chunk)
        
        stat = file_path.stat()
        return GRIBFileInfo(
            id=file_id,
            filename=filename,
            size=stat.st_size,
            uploaded_at=datetime.now(),
            path=str(file_path)
        )
    
    async def delete_file(self, file_id: str) -> None:
        """
        Delete a GRIB file from storage.
        
        Args:
            file_id: ID of the file to delete
        """
        # Find the file with this ID
        matching_files = list(self.storage_path.glob(f"{file_id}.*"))
        
        if not matching_files:
            raise FileNotFoundError(f"File with ID {file_id} not found")
        
        for file_path in matching_files:
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
    
    def _find_file(self, file_id: str) -> Path:
        """
        Find a file by its ID.
        
        Args:
            file_id: ID of the file
            
        Returns:
            Path to the file
        """
        matching_files = list(self.storage_path.glob(f"{file_id}.*"))
        
        if not matching_files:
            raise FileNotFoundError(f"File with ID {file_id} not found")
        
        # Prioritize GRIB files over index files (.idx)
        grib_files = [f for f in matching_files if f.suffix in self.GRIB_EXTENSIONS]
        
        if grib_files:
            return grib_files[0]
        
        return matching_files[0]
    
    async def get_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata from a GRIB file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            Dictionary containing metadata
        """
        file_path = self._find_file(file_id)
        
        # Determine the engine based on file extension
        engine = 'cfgrib' if file_path.suffix in self.GRIB_EXTENSIONS and file_path.suffix != '.nc' else None
        
        # Open file with appropriate engine
        ds = xr.open_dataset(file_path, engine=engine)
        
        metadata = {
            "variables": list(ds.data_vars.keys()),
            "dimensions": dict(ds.dims),
            "coordinates": {
                name: coord.values.tolist() if hasattr(coord.values, 'tolist') else list(coord.values)
                for name, coord in ds.coords.items()
            },
            "attributes": dict(ds.attrs)
        }
        
        ds.close()
        return metadata
    
    async def get_grib_data(
        self, 
        file_id: str, 
        variable: Optional[str] = None,
        level: Optional[int] = None
    ) -> GRIBDataResponse:
        """
        Get GRIB file data in JSON format.
        
        Args:
            file_id: ID of the file
            variable: Optional specific variable to extract
            level: Optional specific level to extract
            
        Returns:
            GRIBDataResponse object
        """
        file_path = self._find_file(file_id)
        
        # Determine the engine based on file extension
        engine = 'cfgrib' if file_path.suffix in self.GRIB_EXTENSIONS and file_path.suffix != '.nc' else None
        
        # Open file with appropriate engine
        ds = xr.open_dataset(file_path, engine=engine)
        
        # Get metadata
        variables = list(ds.data_vars.keys())
        dimensions = dict(ds.dims)
        
        # Filter by variable if specified
        if variable and variable in variables:
            ds = ds[[variable]]
            variables = [variable]
        
        # Filter by level if specified
        if level is not None and 'isobaricInhPa' in ds.coords:
            ds = ds.sel(isobaricInhPa=level, method='nearest')
        
        # Convert data to JSON-serializable format
        data = {}
        for var in variables:
            var_data = ds[var]
            
            # Convert to numpy array and handle NaN values
            values = var_data.values
            if isinstance(values, np.ndarray):
                # Replace NaN with None for JSON serialization
                values = np.where(np.isnan(values), None, values)
                data[var] = values.tolist()
            else:
                data[var] = float(values) if not np.isnan(values) else None
        
        # Get coordinates
        coords = {}
        for coord_name, coord in ds.coords.items():
            coords[coord_name] = coord.values.tolist() if hasattr(coord.values, 'tolist') else [float(coord.values)]
        
        metadata = {
            "coordinates": coords,
            "attributes": dict(ds.attrs)
        }
        
        ds.close()
        
        return GRIBDataResponse(
            file_id=file_id,
            filename=file_path.name,
            variables=variables,
            dimensions=dimensions,
            metadata=metadata,
            data=data
        )

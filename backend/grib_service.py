"""
Service for managing and processing GRIB files.
"""
import os
import uuid
import aiofiles
import requests
import cfgrib
import xarray as xr
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse
from ipaddress import ip_address, IPv4Address, IPv6Address
from fastapi import UploadFile, HTTPException
import logging

from models import GRIBFileInfo, GRIBDataResponse

logger = logging.getLogger(__name__)


class GRIBService:
    """Service for handling GRIB file operations."""
    
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
        for file_path in self.storage_path.glob("*.grib*"):
            stat = file_path.stat()
            files.append(GRIBFileInfo(
                id=file_path.stem,
                filename=file_path.name,
                size=stat.st_size,
                uploaded_at=datetime.fromtimestamp(stat.st_ctime),
                path=str(file_path)
            ))
        return sorted(files, key=lambda x: x.uploaded_at, reverse=True)
    
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
        
        # Determine filename from URL
        filename = Path(url).name or f"{file_id}.grib"
        ext = Path(filename).suffix or ".grib"
        
        # Download file with timeout to prevent hanging
        file_path = self.storage_path / f"{file_id}{ext}"
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
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
        
        # Open GRIB file with cfgrib
        ds = xr.open_dataset(file_path, engine='cfgrib')
        
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
        
        # Open GRIB file with cfgrib
        ds = xr.open_dataset(file_path, engine='cfgrib')
        
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

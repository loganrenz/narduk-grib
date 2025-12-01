"""
Pydantic models for API request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class GRIBFileInfo(BaseModel):
    """Information about a GRIB file."""
    id: str
    filename: str
    size: int
    uploaded_at: datetime
    path: str


class GRIBDataResponse(BaseModel):
    """Response model for GRIB data in JSON format."""
    file_id: str
    filename: str
    variables: List[str]
    dimensions: Dict[str, int]
    metadata: Dict[str, Any]
    data: Dict[str, Any]


class GRIBMetadata(BaseModel):
    """Metadata extracted from a GRIB file."""
    variables: List[str]
    dimensions: Dict[str, int]
    coordinates: Dict[str, List[float]]
    attributes: Dict[str, Any]

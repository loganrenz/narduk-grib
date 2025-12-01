"""
Main FastAPI application for GRIB file viewer backend.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import os
from dotenv import load_dotenv
from typing import List, Optional
import logging

from grib_service import GRIBService
from models import GRIBFileInfo, GRIBDataResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GRIB Viewer API",
    description="Backend API for downloading, managing, and converting GRIB files to JSON",
    version="1.0.0"
)

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GRIB service
storage_path = Path(os.getenv("GRIB_STORAGE_PATH", "./grib_files"))
grib_service = GRIBService(storage_path)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "GRIB Viewer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/grib/files", response_model=List[GRIBFileInfo])
async def list_grib_files():
    """List all available GRIB files."""
    try:
        files = await grib_service.list_files()
        return files
    except Exception as e:
        logger.error(f"Error listing GRIB files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/grib/upload")
async def upload_grib_file(file: UploadFile = File(...)):
    """Upload a GRIB file to the server."""
    try:
        file_info = await grib_service.upload_file(file)
        return file_info
    except Exception as e:
        logger.error(f"Error uploading GRIB file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/grib/download")
async def download_grib_file(url: str):
    """Download a GRIB file from a URL."""
    try:
        file_info = await grib_service.download_file(url)
        return file_info
    except Exception as e:
        logger.error(f"Error downloading GRIB file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/grib/data/{file_id}", response_model=GRIBDataResponse)
async def get_grib_data(
    file_id: str,
    variable: Optional[str] = None,
    level: Optional[int] = None
):
    """Get GRIB file data in JSON format."""
    try:
        data = await grib_service.get_grib_data(file_id, variable, level)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="GRIB file not found")
    except Exception as e:
        logger.error(f"Error reading GRIB data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/grib/metadata/{file_id}")
async def get_grib_metadata(file_id: str):
    """Get metadata from a GRIB file."""
    try:
        metadata = await grib_service.get_metadata(file_id)
        return metadata
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="GRIB file not found")
    except Exception as e:
        logger.error(f"Error reading GRIB metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/grib/files/{file_id}")
async def delete_grib_file(file_id: str):
    """Delete a GRIB file."""
    try:
        await grib_service.delete_file(file_id)
        return {"message": "File deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="GRIB file not found")
    except Exception as e:
        logger.error(f"Error deleting GRIB file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)

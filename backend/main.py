"""
Main FastAPI application for GRIB file viewer backend.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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

# Configure CORS - allow all origins in production, localhost in dev
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
if allowed_origins_env == "*":
    origins = ["*"]
else:
    origins = allowed_origins_env.split(",")
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GRIB service
storage_path = Path(os.getenv("GRIB_STORAGE_PATH", "./grib_files"))
grib_service = GRIBService(storage_path)

# Mount static files directory if it exists (for frontend)
static_dir = Path("/app/static")
static_files_mounted = False

if static_dir.exists():
    # Mount static assets (CSS, JS, images, etc.)
    if (static_dir / "_nuxt").exists():
        app.mount("/_nuxt", StaticFiles(directory=static_dir / "_nuxt"), name="nuxt_static")
        static_files_mounted = True
    
    # Serve favicon if it exists
    if (static_dir / "favicon.ico").exists():
        @app.get("/favicon.ico")
        async def favicon():
            return FileResponse(static_dir / "favicon.ico")


@app.get("/")
async def root():
    """Root endpoint - serves frontend if available, otherwise API info."""
    # If static files exist, serve the frontend
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    # Otherwise return API info (for development without frontend)
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


# Serve frontend SPA catch-all route (must be last route)
if static_dir.exists() and (static_dir / "index.html").exists():
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Catch-all route to serve the frontend SPA.
        This must be the last route defined to not interfere with API routes.
        """
        # Skip if it's an API route, OpenAPI docs, or static assets
        if (full_path.startswith("api/") or 
            full_path.startswith("docs") or 
            full_path.startswith("openapi.json") or
            full_path.startswith("redoc") or
            full_path.startswith("_nuxt")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for SPA routing
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Frontend not found")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)

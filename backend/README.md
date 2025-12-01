# GRIB Viewer Backend

Python FastAPI backend for downloading, managing, and converting GRIB files to JSON format.

## Features

- Upload GRIB files via REST API
- Download GRIB files from URLs
- Convert GRIB data to JSON format for web consumption
- Extract metadata from GRIB files
- List and manage stored GRIB files
- CORS support for frontend integration

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment configuration:
```bash
cp .env.example .env
```

4. Edit `.env` file with your configuration:
```
HOST=0.0.0.0
PORT=8000
GRIB_STORAGE_PATH=./grib_files
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Running the Server

Start the development server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- `GET /health` - Check if the API is running

### GRIB File Management
- `GET /api/grib/files` - List all GRIB files
- `POST /api/grib/upload` - Upload a GRIB file
- `GET /api/grib/download?url=<url>` - Download a GRIB file from URL
- `DELETE /api/grib/files/{file_id}` - Delete a GRIB file

### GRIB Data Access
- `GET /api/grib/data/{file_id}` - Get GRIB data in JSON format
  - Query params: `variable` (optional), `level` (optional)
- `GET /api/grib/metadata/{file_id}` - Get GRIB file metadata

## Example Usage

### Upload a file
```bash
curl -X POST "http://localhost:8000/api/grib/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/file.grib"
```

### Get data from a file
```bash
curl "http://localhost:8000/api/grib/data/{file_id}"
```

### Download a file from URL
```bash
curl "http://localhost:8000/api/grib/download?url=https://example.com/data.grib"
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **cfgrib**: GRIB file reader using ECMWF ecCodes
- **xarray**: Multi-dimensional data arrays for scientific computing
- **numpy**: Numerical computing library
- **requests**: HTTP library for downloading files
- **uvicorn**: ASGI server for running FastAPI

## Development

### Project Structure
```
backend/
├── main.py           # FastAPI application entry point
├── grib_service.py   # GRIB file management service
├── models.py         # Pydantic data models
├── requirements.txt  # Python dependencies
├── .env.example      # Example environment configuration
└── README.md         # This file
```

## Notes

- GRIB files are stored in the directory specified by `GRIB_STORAGE_PATH`
- The API uses cfgrib which requires ECMWF ecCodes to be installed
- Large GRIB files may take some time to process

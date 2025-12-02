# narduk-grib
A modern web-based GRIB file viewer with Vue Nuxt frontend and Python FastAPI backend.

## Overview

This application provides a complete solution for viewing and managing GRIB (GRIdded Binary) meteorological data files. It consists of two main components:

1. **Backend** (Python FastAPI): Handles GRIB file downloads, storage, parsing, and conversion to JSON format
2. **Frontend** (Vue Nuxt 3): Modern, responsive web interface for uploading, managing, and viewing GRIB data

## Features

### Backend
- Upload GRIB files via REST API
- Download GRIB files from external URLs
- Parse GRIB files using cfgrib (ECMWF ecCodes)
- Convert GRIB data to JSON format for web consumption
- Extract comprehensive metadata from GRIB files
- RESTful API with OpenAPI documentation
- CORS support for frontend integration

### Frontend
- Modern, responsive UI built with Vue 3 and Tailwind CSS
- Drag-and-drop file upload
- Download GRIB files from URLs
- Browse and manage stored GRIB files
- View GRIB file metadata and data
- Variable selection and filtering
- TypeScript support

## Quick Start

### Prerequisites
- Python 3.8+ (for backend)
- Node.js 18+ (for frontend)
- ECMWF ecCodes library (required by cfgrib)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment configuration:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Start the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment configuration:
```bash
cp .env.example .env
# Edit .env with your backend API URL
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
narduk-grib/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # FastAPI application entry point
│   ├── grib_service.py     # GRIB file management service
│   ├── models.py           # Pydantic data models
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/               # Vue Nuxt 3 frontend
│   ├── app/               # Application root
│   │   ├── app.vue        # Root component
│   │   ├── components/    # Vue components
│   │   ├── composables/   # Vue composables
│   │   └── pages/         # Application pages
│   ├── assets/            # Static assets and styles
│   ├── public/            # Public static files
│   ├── nuxt.config.ts     # Nuxt configuration
│   └── README.md          # Frontend documentation
└── README.md              # This file
```

## API Documentation

Once the backend is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

- `GET /api/grib/files` - List all GRIB files
- `POST /api/grib/upload` - Upload a GRIB file
- `GET /api/grib/download` - Download a GRIB file from URL
- `GET /api/grib/data/{file_id}` - Get GRIB data in JSON format
- `GET /api/grib/metadata/{file_id}` - Get GRIB file metadata
- `DELETE /api/grib/files/{file_id}` - Delete a GRIB file

## Technologies Used

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **cfgrib**: Python interface to ECMWF ecCodes for reading GRIB files
- **xarray**: Multi-dimensional arrays for scientific computing
- **numpy**: Numerical computing library
- **Pydantic**: Data validation using Python type annotations

### Frontend
- **Nuxt 3**: Vue.js framework with server-side rendering
- **Vue 3**: Progressive JavaScript framework
- **TypeScript**: Typed superset of JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Leaflet**: JavaScript library for interactive maps

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## Production Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
npm run preview
```

## Testing

This project includes comprehensive test coverage for GRIB file transformation and downloading. See [TESTING.md](TESTING.md) for detailed information on:

- Running tests
- Test coverage
- Supported GRIB models
- Map provider verification
- Authentication requirements

Quick start:
```bash
cd backend
pytest  # Run all tests
pytest -m "not integration"  # Run unit tests only
```

## Map Provider Support

The frontend supports three map visualization providers:

1. **Leaflet** (Default) - OpenStreetMap, no API key required
2. **Mapbox** - Requires Mapbox API token
3. **Apple MapKit JS** - Requires MapKit JS token

Leaflet is configured as the default provider and works out of the box. For Mapbox or MapKit JS:

1. Get your API token from the respective provider
2. Add to `frontend/.env`:
   ```
   NUXT_PUBLIC_MAPBOX_TOKEN=your_token
   NUXT_PUBLIC_MAPKIT_TOKEN=your_token
   ```
3. Select provider from the dropdown in the UI

See [TESTING.md](TESTING.md) for detailed map provider configuration.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

When adding new features:
- Add appropriate tests (see [TESTING.md](TESTING.md))
- Update documentation
- Follow existing code style

## License

This project is open source and available under the MIT License.

## Acknowledgments

- ECMWF for the ecCodes library
- The cfgrib, xarray, and FastAPI communities

# GRIB Viewer Frontend

Modern Vue Nuxt 3 application for viewing GRIB files.

## Features

- Upload GRIB files from your computer
- Download GRIB files from URLs
- View GRIB file metadata and data
- List and manage stored GRIB files
- Modern, responsive UI with Tailwind CSS
- TypeScript support for type safety

## Prerequisites

- Node.js 18 or higher
- npm package manager

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` file with your backend API URL:
```
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Building for Production

Build the application:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── app/
│   ├── app.vue           # Root application component
│   ├── components/       # Vue components
│   │   ├── FileUpload.vue    # File upload component
│   │   ├── FileList.vue      # File list component
│   │   └── GribViewer.vue    # GRIB data viewer component
│   ├── composables/      # Vue composables
│   │   └── useGribApi.ts     # API interaction composable
│   └── pages/            # Application pages
│       └── index.vue         # Main page
├── assets/
│   └── css/
│       └── main.css      # Global styles and Tailwind imports
├── public/               # Static assets
├── nuxt.config.ts        # Nuxt configuration
└── package.json          # Dependencies
```

## Features & Components

### FileUpload Component
- Drag-and-drop file upload
- Manual file selection
- Download from URL
- Upload progress indication

### FileList Component
- Display all uploaded GRIB files
- File metadata (name, size, upload date)
- Select files for viewing
- Delete files

### GribViewer Component
- Display GRIB file data
- View metadata and coordinates
- Variable selection
- Data visualization placeholder

## Configuration

The application uses runtime configuration for the API base URL. You can configure it in:
- `.env` file for development
- Environment variables for production deployment

## Technologies Used

- **Nuxt 3**: Vue.js framework for server-side rendering and static generation
- **Vue 3**: Progressive JavaScript framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Leaflet**: Map visualization library (for future enhancements)

## API Integration

The frontend communicates with the Python FastAPI backend through the `useGribApi` composable, which provides methods for:
- Listing files
- Uploading files
- Downloading files from URLs
- Getting GRIB data
- Getting metadata
- Deleting files

## Future Enhancements

- Interactive map visualization using Leaflet
- Multiple variable comparison
- Time series animation
- Data export functionality
- Real-time updates via WebSocket

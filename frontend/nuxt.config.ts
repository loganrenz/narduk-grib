// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  
  modules: ['@nuxtjs/tailwindcss'],
  
  ssr: false, // Disable SSR for static generation
  
  runtimeConfig: {
    public: {
      // Use empty string for production (same origin), localhost for development
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000'),
      mapboxToken: process.env.NUXT_PUBLIC_MAPBOX_TOKEN || '',
      mapkitToken: process.env.NUXT_PUBLIC_MAPKIT_TOKEN || ''
    }
  },
  
  app: {
    head: {
      title: 'GRIB Viewer',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Modern GRIB file viewer' }
      ],
      link: [
        { rel: 'stylesheet', href: 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' }
      ]
    }
  }
})

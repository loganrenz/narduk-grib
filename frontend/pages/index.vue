<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
            <h1 class="text-2xl font-bold text-gray-900">GRIB Viewer</h1>
          </div>
          <div class="text-sm text-gray-600">
            Modern GRIB File Viewer
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Left Column: Upload and File List -->
        <div class="space-y-6">
          <FileUpload @uploaded="handleFileUploaded" />
          <FileList ref="fileListRef" @fileSelected="handleFileSelected" />
        </div>

        <!-- Right Column: Data Viewer -->
        <div class="lg:sticky lg:top-8 lg:self-start">
          <GribViewer :fileId="selectedFileId" @close="selectedFileId = null" />
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t mt-12">
      <div class="container mx-auto px-4 py-6">
        <div class="text-center text-sm text-gray-600">
          <p>GRIB Viewer - Modern web-based GRIB file visualization</p>
          <p class="mt-1">Built with Vue, Nuxt 3, and Python FastAPI</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const selectedFileId = ref<string | null>(null)
const fileListRef = ref<any>(null)

const handleFileUploaded = () => {
  // Refresh the file list when a new file is uploaded
  if (fileListRef.value) {
    fileListRef.value.loadFiles()
  }
}

const handleFileSelected = (fileId: string) => {
  selectedFileId.value = fileId
}

useHead({
  title: 'GRIB Viewer',
  meta: [
    { name: 'description', content: 'Modern web-based GRIB file viewer' }
  ]
})
</script>

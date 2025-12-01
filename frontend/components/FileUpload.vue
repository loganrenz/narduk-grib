<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h2 class="text-2xl font-bold mb-4">Upload GRIB File</h2>
    
    <div class="mb-4">
      <div
        class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer"
        @click="triggerFileInput"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        :class="{ 'border-blue-500 bg-blue-50': isDragging }"
      >
        <div v-if="!selectedFile">
          <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <p class="mt-2 text-sm text-gray-600">
            Click to upload or drag and drop a GRIB file
          </p>
        </div>
        <div v-else class="text-sm text-gray-600">
          <p class="font-medium">{{ selectedFile.name }}</p>
          <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
        </div>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept=".grib,.grib2,.grb,.grb2"
        class="hidden"
        @change="handleFileSelect"
      />
    </div>

    <div v-if="selectedFile" class="flex gap-2">
      <button
        @click="uploadFile"
        :disabled="isUploading"
        class="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        {{ isUploading ? 'Uploading...' : 'Upload File' }}
      </button>
      <button
        @click="clearFile"
        :disabled="isUploading"
        class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
      >
        Clear
      </button>
    </div>

    <div v-if="uploadError" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
      {{ uploadError }}
    </div>

    <div v-if="uploadSuccess" class="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
      File uploaded successfully!
    </div>

    <div class="mt-6 border-t pt-6">
      <h3 class="text-lg font-semibold mb-2">Or Download from URL</h3>
      <div class="flex gap-2">
        <input
          v-model="downloadUrl"
          type="url"
          placeholder="https://example.com/file.grib"
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          :disabled="isDownloading"
        />
        <button
          @click="downloadFromUrl"
          :disabled="isDownloading || !downloadUrl"
          class="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-6 rounded-lg disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {{ isDownloading ? 'Downloading...' : 'Download' }}
        </button>
      </div>
      <div v-if="downloadError" class="mt-2 text-sm text-red-600">
        {{ downloadError }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits(['uploaded'])
const { uploadFile: apiUploadFile, downloadFile: apiDownloadFile } = useGribApi()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref(false)
const isDragging = ref(false)

const downloadUrl = ref('')
const isDownloading = ref(false)
const downloadError = ref('')

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    uploadError.value = ''
    uploadSuccess.value = false
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
    uploadError.value = ''
    uploadSuccess.value = false
  }
}

const clearFile = () => {
  selectedFile.value = null
  uploadError.value = ''
  uploadSuccess.value = false
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  isUploading.value = true
  uploadError.value = ''
  uploadSuccess.value = false

  try {
    await apiUploadFile(selectedFile.value)
    uploadSuccess.value = true
    emit('uploaded')
    setTimeout(() => {
      clearFile()
      uploadSuccess.value = false
    }, 2000)
  } catch (error: any) {
    uploadError.value = error.message || 'Failed to upload file'
  } finally {
    isUploading.value = false
  }
}

const downloadFromUrl = async () => {
  if (!downloadUrl.value) return

  isDownloading.value = true
  downloadError.value = ''

  try {
    await apiDownloadFile(downloadUrl.value)
    emit('uploaded')
    downloadUrl.value = ''
  } catch (error: any) {
    downloadError.value = error.message || 'Failed to download file'
  } finally {
    isDownloading.value = false
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

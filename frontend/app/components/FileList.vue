<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold mb-4">GRIB Files</h2>
    
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      <p class="mt-2 text-gray-600">Loading files...</p>
    </div>

    <div v-else-if="error" class="text-center py-8 text-red-600">
      <p>Error loading files: {{ error }}</p>
      <button
        @click="loadFiles"
        class="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
      >
        Retry
      </button>
    </div>

    <div v-else-if="files.length === 0" class="text-center py-8 text-gray-600">
      <p>No GRIB files available. Upload or download a file to get started.</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="file in files"
        :key="file.id"
        class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors cursor-pointer"
        :class="{ 'border-blue-500 bg-blue-50': selectedFileId === file.id }"
        @click="selectFile(file.id)"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900">{{ file.filename }}</h3>
            <div class="mt-1 text-sm text-gray-600 space-x-4">
              <span>{{ formatFileSize(file.size) }}</span>
              <span>{{ formatDate(file.uploaded_at) }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click.stop="viewFile(file.id)"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm font-medium transition-colors"
            >
              View
            </button>
            <button
              @click.stop="confirmDelete(file.id)"
              class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 text-sm font-medium transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deleteConfirmId"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="deleteConfirmId = null"
    >
      <div class="bg-white rounded-lg p-6 max-w-md" @click.stop>
        <h3 class="text-xl font-bold mb-2">Confirm Delete</h3>
        <p class="text-gray-600 mb-4">Are you sure you want to delete this file? This action cannot be undone.</p>
        <div class="flex gap-2 justify-end">
          <button
            @click="deleteConfirmId = null"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="deleteFile"
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits(['fileSelected'])
const { listFiles, deleteFile: apiDeleteFile } = useGribApi()

interface GRIBFile {
  id: string
  filename: string
  size: number
  uploaded_at: string
  path: string
}

const files = ref<GRIBFile[]>([])
const loading = ref(false)
const error = ref('')
const selectedFileId = ref<string | null>(null)
const deleteConfirmId = ref<string | null>(null)

const loadFiles = async () => {
  loading.value = true
  error.value = ''
  try {
    files.value = await listFiles()
  } catch (e: any) {
    error.value = e.message || 'Failed to load files'
  } finally {
    loading.value = false
  }
}

const selectFile = (fileId: string) => {
  selectedFileId.value = fileId
}

const viewFile = (fileId: string) => {
  emit('fileSelected', fileId)
}

const confirmDelete = (fileId: string) => {
  deleteConfirmId.value = fileId
}

const deleteFile = async () => {
  if (!deleteConfirmId.value) return

  const fileIdToDelete = deleteConfirmId.value
  
  try {
    await apiDeleteFile(fileIdToDelete)
    await loadFiles()
    deleteConfirmId.value = null
    if (selectedFileId.value === fileIdToDelete) {
      selectedFileId.value = null
    }
  } catch (e: any) {
    error.value = e.message || 'Failed to delete file'
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// Load files on mount
onMounted(() => {
  loadFiles()
})

// Expose loadFiles method for parent components
defineExpose({ loadFiles })
</script>

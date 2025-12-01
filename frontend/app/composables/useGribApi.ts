/**
 * Composable for interacting with the GRIB API backend
 */
export const useGribApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || ''
  // If apiBase is empty, use relative paths (starts with /). Otherwise use the provided base URL.
  const baseUrl = apiBase ? (apiBase.endsWith('/') ? apiBase : `${apiBase}/`) : '/'

  /**
   * List all GRIB files
   */
  const listFiles = async () => {
    try {
      const response = await $fetch(`${baseUrl}api/grib/files`)
      return response
    } catch (error) {
      console.error('Error listing GRIB files:', error)
      throw error
    }
  }

  /**
   * Upload a GRIB file
   */
  const uploadFile = async (file: File) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await $fetch(`${baseUrl}api/grib/upload`, {
        method: 'POST',
        body: formData
      })
      return response
    } catch (error) {
      console.error('Error uploading GRIB file:', error)
      throw error
    }
  }

  /**
   * Download a GRIB file from URL
   */
  const downloadFile = async (url: string) => {
    try {
      const response = await $fetch(`${baseUrl}api/grib/download`, {
        params: { url }
      })
      return response
    } catch (error) {
      console.error('Error downloading GRIB file:', error)
      throw error
    }
  }

  /**
   * Get GRIB file data
   */
  const getGribData = async (fileId: string, variable?: string, level?: number) => {
    try {
      const params: any = {}
      if (variable) params.variable = variable
      if (level !== undefined) params.level = level

      const response = await $fetch(`${baseUrl}api/grib/data/${fileId}`, {
        params
      })
      return response
    } catch (error) {
      console.error('Error getting GRIB data:', error)
      throw error
    }
  }

  /**
   * Get GRIB file metadata
   */
  const getMetadata = async (fileId: string) => {
    try {
      const response = await $fetch(`${baseUrl}api/grib/metadata/${fileId}`)
      return response
    } catch (error) {
      console.error('Error getting GRIB metadata:', error)
      throw error
    }
  }

  /**
   * Delete a GRIB file
   */
  const deleteFile = async (fileId: string) => {
    try {
      const response = await $fetch(`${baseUrl}api/grib/files/${fileId}`, {
        method: 'DELETE'
      })
      return response
    } catch (error) {
      console.error('Error deleting GRIB file:', error)
      throw error
    }
  }

  return {
    listFiles,
    uploadFile,
    downloadFile,
    getGribData,
    getMetadata,
    deleteFile
  }
}

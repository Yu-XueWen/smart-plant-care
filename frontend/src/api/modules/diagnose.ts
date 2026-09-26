import request from '../request'

export const diagnoseApi = {
  // 诊断病害
  diagnoseDisease(file: File, plantId?: number, saveHistory = true) {
    const formData = new FormData()
    formData.append('image', file)
    if (plantId) {
      formData.append('plant_id', String(plantId))
    }
    formData.append('save_history', String(saveHistory))
    
    return request.post<any>('/ai/diagnose', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
}

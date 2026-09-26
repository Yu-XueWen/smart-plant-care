import request from '../request'
import type { PlantIdentification } from '@/types/models'

export const identifyApi = {
  // 识别植物
  identifyPlant(file: File, saveHistory = true) {
    const formData = new FormData()
    formData.append('image', file)
    formData.append('save_history', String(saveHistory))
    
    return request.post<PlantIdentification>('/ai/identify', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
}

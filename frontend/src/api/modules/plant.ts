import request from '../request'
import type { Plant } from '@/types/models'

export interface PlantCreateData {
  plant_name: string
  species_id?: string
  nickname?: string
  planting_date?: string
  source?: string
  initial_photos?: string[]
  notes?: string
  status?: number
}

export interface WateringRecordData {
  watering_date: string
  water_amount?: string
  notes?: string
}

export interface TreatmentRecordData {
  treatment_type: string
  product_name?: string
  dosage?: string
  application_date: string
  notes?: string
}

export const plantApi = {
  // 获取我的盆栽列表
  getMyPlants(params?: { page?: number; page_size?: number; status?: number }) {
    return request.get<{ items: any[]; total: number }>('/plants', { params })
  },

  // 获取盆栽详情
  getPlantDetail(id: number) {
    return request.get<any>(`/plants/${id}`)
  },

  // 创建盆栽
  createPlant(data: PlantCreateData) {
    return request.post<Plant>('/plants', data)
  },

  // 更新盆栽
  updatePlant(id: number, data: Partial<PlantCreateData>) {
    return request.put<Plant>(`/plants/${id}`, data)
  },

  // 删除盆栽（软删除）
  deletePlant(id: number) {
    return request.delete(`/plants/${id}`)
  },

  // 上传盆栽图片
  uploadPlantImage(file: File) {
    return request.upload<{ url: string }>('/plants/upload/image', file, 'file')
  },

  // 添加浇水记录
  addWatering(plantId: number, data: WateringRecordData) {
    return request.post(`/plants/${plantId}/watering`, data)
  },

  // 获取浇水记录
  getWateringRecords(plantId: number, limit = 20) {
    return request.get<{ items: any[]; total: number }>(`/plants/${plantId}/watering`, {
      params: { limit }
    })
  },

  // 添加养护记录
  addTreatment(plantId: number, data: TreatmentRecordData) {
    return request.post(`/plants/${plantId}/treatment`, data)
  },

  // 获取养护记录
  getTreatmentRecords(plantId: number, limit = 20) {
    return request.get<{ items: any[]; total: number }>(`/plants/${plantId}/treatments`, {
      params: { limit }
    })
  },

  // 从知识图谱查询植物信息
  searchPlantFromKG(plantName: string) {
    return request.get<any>('/plants/kg/search', {
      params: { plant_name: plantName }
    })
  },

  // 获取盆栽的知识图谱详细信息
  getPlantKGInfo(plantId: number) {
    return request.get<any>(`/plants/${plantId}/kg-info`)
  },

  // 快速浇水单个盆栽
  quickWaterPlant(plantId: number) {
    return request.post<{ 
      record_id: number
      watering_date: string
      next_watering_date: string | null
      interval_days: number | null
    }>(`/plants/${plantId}/quick-water`)
  },

  // 一键浇水所有盆栽
  batchQuickWaterAll() {
    return request.post<{
      success_count: number
      failed_count: number
      total: number
      details: Array<{
        plant_id: number
        plant_name: string
        nickname?: string
        status: 'success' | 'partial_success' | 'failed'
        next_watering_date?: string
        interval_days?: number
        message?: string
      }>
    }>('/plants/batch-quick-water')
  },
}

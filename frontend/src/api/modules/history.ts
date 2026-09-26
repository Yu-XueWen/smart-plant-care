import request from '../request'
import type { IdentifyHistoryItem, DiagnoseHistoryItem } from '@/types/models'

export const historyApi = {
  // 获取识花历史记录
  getIdentifyHistory(params?: { page?: number; page_size?: number }) {
    return request.get<{ items: IdentifyHistoryItem[]; total: number; page: number; page_size: number }>('/history/identify', { params })
  },

  // 获取诊断历史记录
  getDiagnoseHistory(params?: { page?: number; page_size?: number }) {
    return request.get<{ items: DiagnoseHistoryItem[]; total: number; page: number; page_size: number }>('/history/diagnose', { params })
  },

  // 获取历史记录详情
  getHistoryDetail(historyType: 'identify' | 'diagnose', id: number) {
    return request.get<any>(`/history/${historyType}/${id}`)
  },

  // 删除历史记录
  deleteHistory(historyType: 'identify' | 'diagnose', id: number) {
    return request.delete(`/history/${historyType}/${id}`)
  },
}

import request from '../request'
import type { Reminder } from '@/types/models'

export const reminderApi = {
  // 获取提醒列表
  getReminders(params?: { page?: number; page_size?: number }) {
    return request.get<{ items: Reminder[]; total: number }>('/reminders', { params })
  },

  // 创建提醒
  createReminder(data: Partial<Reminder>) {
    return request.post<Reminder>('/reminders', data)
  },

  // 更新提醒
  updateReminder(id: number, data: Partial<Reminder>) {
    return request.put<Reminder>(`/reminders/${id}`, data)
  },

  // 删除提醒
  deleteReminder(id: number) {
    return request.delete(`/reminders/${id}`)
  },

  // 标记提醒为已完成
  completeReminder(id: number) {
    return request.put(`/reminders/${id}/complete`)
  },
}

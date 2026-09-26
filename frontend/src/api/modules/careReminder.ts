import request from '../request'

// 养护提醒接口
export interface CareReminder {
  id: number
  user_id: number
  plant_id?: number
  plant_name?: string
  nickname?: string
  remind_type: 'water' | 'fertilize' | 'pesticide' | 'prune' | 'other'
  frequency_type: 'one_time' | 'daily' | 'weekly' | 'monthly' | 'interval'
  interval_days?: number
  repeat_interval?: number
  scheduled_date: string
  application_date?: string
  product_name?: string
  dosage?: string
  custom_message?: string
  notes?: string
  is_enabled: boolean
  status: 'pending' | 'completed' | 'overdue' | 'today' | 'unknown'
  created_at: string
  updated_at: string
}

// 创建提醒请求
export interface CreateCareReminderRequest {
  plant_id?: number
  remind_type: 'water' | 'fertilize' | 'pesticide' | 'prune' | 'other'
  scheduled_date: string
  product_name?: string
  dosage?: string
  notes?: string
  custom_message?: string
  frequency_type?: 'one_time' | 'daily' | 'weekly' | 'monthly' | 'interval'
  is_enabled?: boolean
  interval_days?: number
  repeat_interval?: number
}

// 更新提醒请求
export interface UpdateCareReminderRequest {
  remind_type?: 'water' | 'fertilize' | 'pesticide' | 'prune' | 'other'
  scheduled_date?: string
  product_name?: string
  dosage?: string
  notes?: string
  custom_message?: string
  is_enabled?: boolean
  frequency_type?: 'one_time' | 'daily' | 'weekly' | 'monthly' | 'interval'
  interval_days?: number
  repeat_interval?: number
}

// 完成提醒并同步响应
export interface CompleteReminderResponse {
  message: string
  treatment_record_id: number
  plant_name: string
  nickname?: string
  treatment_type: string
  application_date: string
  product_name?: string
  dosage?: string
}

export const careReminderApi = {
  // 获取提醒列表
  getReminders(params?: {
    page?: number
    page_size?: number
    remind_type?: string
    status_filter?: 'pending' | 'completed'
  }) {
    return request.get<{ items: CareReminder[]; total: number; page: number; page_size: number }>(
      '/care-reminders',
      { params }
    )
  },

  // 获取提醒详情
  getReminderDetail(id: number) {
    return request.get<CareReminder>(`/care-reminders/${id}`)
  },

  // 创建提醒
  createReminder(data: CreateCareReminderRequest) {
    return request.post<CareReminder>('/care-reminders', data)
  },

  // 更新提醒
  updateReminder(id: number, data: UpdateCareReminderRequest) {
    return request.put<CareReminder>(`/care-reminders/${id}`, data)
  },

  // 删除提醒
  deleteReminder(id: number) {
    return request.delete(`/care-reminders/${id}`)
  },

  // 完成提醒并同步到养护记录
  completeAndSync(
    id: number,
    params?: {
      actual_date?: string
      actual_product?: string
      actual_dosage?: string
      actual_notes?: string
    }
  ) {
    return request.post<CompleteReminderResponse>(
      `/care-reminders/${id}/complete`,
      null,
      { params }
    )
  },

  // 检查缺失的浇水提醒
  checkMissingWateringReminders() {
    return request.post<{ created_count: number; skipped_count: number; total_plants: number }>(
      '/care-reminders/check-missing'
    )
  }
}

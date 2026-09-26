import request from '../request'

// ApiResponse 类型定义
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 浇水提醒配置接口
export interface WateringReminderConfig {
  id: number
  interval_days: number
  scheduled_date: string
  frequency_type: string
  is_enabled: boolean
  current_season: string
  season_name: string
  last_watering_date?: string | null  // 最近一次浇水日期
}

// 今日提醒项接口
export interface TodayReminderItem {
  reminder_id: number
  plant_id: number
  plant_name: string
  nickname?: string
  status: 'pending' | 'completed' | 'postponed'
  completed_time_slot?: 'morning' | 'noon' | 'evening'
  postpone_count: number
  time_slots: Array<{
    time: string
    slot: 'morning' | 'noon' | 'evening'
    label: string
  }>
}

// 今日提醒响应接口
export interface TodayRemindersResponse {
  date: string
  count: number
  reminders: TodayReminderItem[]
}

// 完成提醒响应接口
export interface CompleteReminderResponse {
  message: string
  plant_name: string
  completed_at: string
  already_completed?: boolean
}

// 推迟提醒响应接口
export interface PostponeReminderResponse {
  message: string
  postpone_count: number
  next_reminder: string
  already_completed?: boolean
}

/**
 * 为植物设置浇水提醒
 */
export function setupWateringReminder(plantId: number): Promise<ApiResponse<WateringReminderConfig>> {
  return request.post(`/watering-reminders/plants/${plantId}/setup-reminder`)
}

/**
 * 获取今日浇水提醒列表
 */
export function getTodayReminders(): Promise<ApiResponse<TodayRemindersResponse>> {
  return request.get('/watering-reminders/today')
}

/**
 * 完成浇水提醒
 * @param reminderId 提醒ID
 * @param timeSlot 时间段 (morning/noon/evening)
 */
export function completeWateringReminder(
  reminderId: number,
  timeSlot: 'morning' | 'noon' | 'evening' = 'morning'
): Promise<ApiResponse<CompleteReminderResponse>> {
  return request.post(`/watering-reminders/${reminderId}/complete`, null, {
    params: { time_slot: timeSlot }
  })
}

/**
 * 推迟浇水提醒
 * @param reminderId 提醒ID
 * @param postponeHours 推迟小时数，默认24小时
 */
export function postponeWateringReminder(
  reminderId: number,
  postponeHours: number = 24
): Promise<ApiResponse<PostponeReminderResponse>> {
  return request.post(`/watering-reminders/${reminderId}/postpone`, null, {
    params: { postpone_hours: postponeHours }
  })
}

/**
 * 获取植物的浇水提醒配置
 * @param plantId 植物ID
 */
export function getReminderConfig(plantId: number): Promise<ApiResponse<WateringReminderConfig | null>> {
  return request.get(`/watering-reminders/config/${plantId}`)
}

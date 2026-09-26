// 本地存储键名
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER_INFO: 'userInfo',
} as const

// 用户角色
export const USER_ROLES = {
  USER: 'user',
  ADMIN: 'admin',
} as const

// 提醒类型
export const REMINDER_TYPES = {
  WATER: 'water',
  FERTILIZE: 'fertilize',
  PESTICIDE: 'pesticide',
  PRUNE: 'prune',
  OTHER: 'other',
} as const

export const REMINDER_TYPE_LABELS: Record<string, string> = {
  water: '浇水',
  fertilize: '施肥',
  pesticide: '施药',
  prune: '修剪',
  other: '养护',
}

// 提醒周期类型
export const FREQUENCY_TYPES = {
  DAILY: 'daily',
  WEEKLY: 'weekly',
  MONTHLY: 'monthly',
  INTERVAL: 'interval',
  ONE_TIME: 'one_time',
} as const

// 养护操作类型
export const TREATMENT_TYPES = {
  FERTILIZE: 'fertilize',
  PESTICIDE: 'pesticide',
  PRUNE: 'prune',
  OTHER: 'other',
} as const

// 分页默认值
export const PAGINATION_DEFAULTS = {
  PAGE: 1,
  PAGE_SIZE: 10,
  PAGE_SIZES: [10, 20, 50, 100],
} as const

// 文件上传限制
export const UPLOAD_LIMITS = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ACCEPT_TYPES: ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'],
}
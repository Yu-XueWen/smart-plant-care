/**
 * 组件相关类型定义
 */

import type { Plant, Reminder, Recommendation } from './models'

// 植物卡片属性
export interface PlantCardProps {
  plant: Plant
  showActions?: boolean
}

// 植物表单属性
export interface PlantFormProps {
  plant?: Plant
  mode?: 'create' | 'edit'
}

// 提醒项属性
export interface ReminderItemProps {
  reminder: Reminder
  showActions?: boolean
}

// 提醒表单属性
export interface ReminderFormProps {
  reminder?: Reminder
  mode?: 'create' | 'edit'
  plantOptions?: Array<{ label: string; value: number }>
}

// 推荐卡片属性
export interface RecommendCardProps {
  recommendation: Recommendation
}

// 问卷属性
export interface QuestionnaireProps {
  onSubmit: (answers: any) => void
}

// 图片上传器属性
export interface ImageUploaderProps {
  modelValue?: string
  maxSize?: number
  accept?: string
  disabled?: boolean
}

// 分页器属性
export interface PaginationProps {
  total: number
  currentPage: number
  pageSize: number
  pageSizes?: number[]
}

// 加载动画属性
export interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  text?: string
}

// 确认对话框属性
export interface ConfirmDialogProps {
  visible: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'info' | 'warning' | 'danger'
}

// 用户表格属性
export interface UserTableProps {
  users: any[]
  loading?: boolean
}

// 记录表格属性
export interface RecordTableProps {
  records: any[]
  loading?: boolean
}

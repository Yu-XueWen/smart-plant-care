/**
 * 数据模型类型定义
 */

// 用户模型
export interface User {
  id: number
  username: string
  email: string
  phone?: string
  avatar?: string
  role: 'user' | 'admin'
  status?: number
  created_at: string
  updated_at: string
}

// 植物模型
export interface Plant {
  id: number
  user_id: number
  name: string
  species: string
  variety?: string
  image?: string
  acquisition_date?: string
  location?: string
  status: 'healthy' | 'sick' | 'dead'
  notes?: string
  created_at: string
  updated_at: string
}

// 植物识别结果
export interface PlantIdentification {
  species: string
  confidence: number
  scientific_name?: string
  description?: string
  care_tips?: string[]
}

// 病害诊断结果
export interface DiseaseDiagnosis {
  primary_disease: string
  confidence: number
  symptoms: string
  treatment: {
    chemical: string
    organic: string
    prevention: string
  }
  history_id?: number
  image_url?: string
}

// 推荐结果
export interface Recommendation {
  plant_name: string
  scientific_name?: string
  match_score: number
  reasons: string[]
  care_difficulty: 'easy' | 'medium' | 'hard'
  light_requirement: string
  water_requirement?: string
  water_frequency?: string
  temperature_range: string
  humidity_range: string
  tags?: string[]
  benefits?: string[]
  description?: string
  care_tips?: string
  image?: string
}

// 问卷答案
export interface QuestionnaireAnswers {
  experience_level: 'beginner' | 'intermediate' | 'advanced'
  light_condition: string
  space_size: string
  time_availability: string
  preferences: string[]
  climate_zone?: string
}

// 提醒模型
export interface Reminder {
  id: number
  user_id: number
  plant_id?: number
  type: 'water' | 'fertilize' | 'prune' | 'repot' | 'other'
  title: string
  description?: string
  scheduled_time: string
  frequency?: 'once' | 'daily' | 'weekly' | 'monthly'
  completed: boolean
  completed_at?: string
  created_at: string
  updated_at: string
}

// 历史记录基础项
export interface HistoryItem {
  id: number
  image_url: string
  created_at: string
}

// 角色模型
export interface Role {
  id: number
  name: string
  description?: string
  permissions: string[]
  user_count: number
  created_at: string
  updated_at: string
}

// 植物知识库
export interface KnowledgePlant {
  id: number
  name: string
  scientific_name?: string
  family?: string
  care_level?: 'easy' | 'medium' | 'hard'
  light_requirement?: string
  water_requirement?: string
  temperature_range?: string
  humidity_range?: string
  description?: string
  image_url?: string
  created_at: string
  updated_at: string
}

// 病害知识库
export interface KnowledgeDisease {
  id: number
  name: string
  scientific_name?: string
  pathogen?: string
  symptoms?: string
  affected_plants?: string
  treatment?: string
  prevention?: string
  severity?: 'mild' | 'moderate' | 'severe'
  image_url?: string
  created_at: string
  updated_at: string
}

// 养护技巧
export interface KnowledgeTip {
  id: number
  title: string
  category?: string
  content?: string
  image_url?: string
  created_at: string
  updated_at: string
}

// 识花历史记录项
export interface IdentifyHistoryItem extends HistoryItem {
  plant_name: string
  confidence?: number
}

// 诊断历史记录项
export interface DiagnoseHistoryItem extends HistoryItem {
  disease_name: string
  confidence?: number
}

// 历史记录（通用）
export interface HistoryRecord {
  id: number
  user_id: number
  type: 'identification' | 'diagnosis' | 'recommendation'
  image_url?: string
  result: any
  created_at: string
}

// 统计数据
export interface Statistics {
  total_users: number
  total_plants: number
  total_identifications: number
  total_diagnoses: number
  active_users_today: number
}

// 仪表盘概览
export interface DashboardOverview {
  total_users: number
  total_plants: number
  total_identifications: number
  total_diagnoses: number
  active_users_today: number
  new_users_today: number
  new_plants_today: number
  system_uptime: number
  identify_count?: number
  diagnose_count?: number
}

// 今日统计
export interface TodayStats {
  date: string
  identifications: number
  diagnoses: number
  new_users: number
  new_plants: number
}

// 近期动态
export interface RecentActivity {
  id: number
  user_id: number
  username: string
  action: string
  target_type: string
  target_id: number
  detail: any
  created_at: string
}

// 图表数据
export interface ChartData {
  metric: string
  data?: Array<{ date: string; value: number }>
  labels?: string[]
  datasets?: {
    name: string
    data: number[]
  }[]
  identify?: { date: string; value: number }[]
  diagnose?: { date: string; value: number }[]
}

// 操作日志
export interface OperationLog {
  id: number
  admin_id: number
  username: string
  action: string
  target_type: string
  target_id: number
  detail: any
  ip_address: string
  created_at: string
}

// 登录日志
export interface LoginLog {
  id: number
  user_id: number
  username: string
  ip_address: string
  user_agent: string
  login_time: string
  success: boolean
  logout_time?: string
  duration_seconds?: number
}

// 系统状态
export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'critical'
  components: {
    name: string
    status: 'healthy' | 'degraded' | 'critical'
    message?: string
  }[]
  uptime: number
  last_check: string
}

// 系统指标
export interface SystemMetrics {
  cpu_percent: number
  memory: {
    total: number
    used: number
    percent: number
  }
  disk: {
    total: number
    used: number
    percent: number
  }
  processes: number
}

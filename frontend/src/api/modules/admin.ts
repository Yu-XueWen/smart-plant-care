import request from '../request'
import type { User, OperationLog, LoginLog, SystemStatus, SystemMetrics, DashboardOverview, TodayStats, ChartData, RecentActivity, Role, KnowledgePlant, KnowledgeDisease, KnowledgeTip } from '@/types/models'

export const adminApi = {
  // 获取用户列表
  getUsers(params?: { page?: number; page_size?: number; keyword?: string }) {
    return request.get<{ items: User[]; total: number }>('/admin/users', { params })
  },

  // 禁用/启用用户
  toggleUserStatus(userId: number, status: number) {
    return request.put(`/admin/users/${userId}/status?status=${status}`)
  },

  // 删除用户
  deleteUser(userId: number) {
    return request.delete(`/admin/users/${userId}`)
  },

  // 重置用户密码
  resetUserPassword(userId: number, newPassword: string) {
    return request.post(`/admin/users/${userId}/reset-password?new_password=${newPassword}`)
  },

  // 获取用户详情
  getUserDetail(userId: number) {
    return request.get<User>(`/admin/users/${userId}/detail`)
  },

  // 获取用户盆栽
  getUserPlants(userId: number, params?: { page?: number; page_size?: number }) {
    return request.get(`/admin/users/${userId}/plants`, { params })
  },

  // 获取用户记录
  getUserRecords(userId: number, params?: { page?: number; page_size?: number }) {
    return request.get(`/admin/users/${userId}/records`, { params })
  },

  // 获取用户历史
  getUserHistory(userId: number, historyType: string, params?: { page?: number; page_size?: number }) {
    return request.get(`/admin/users/${userId}/history?history_type=${historyType}`, { params })
  },

  // 获取仪表盘概览
  getDashboardOverview() {
    return request.get<DashboardOverview>('/admin/dashboard/overview')
  },

  // 获取今日统计
  getTodayStats() {
    return request.get<TodayStats>('/admin/dashboard/today-stats')
  },

  // 获取近期动态
  getRecentActivity(limit?: number) {
    return request.get<RecentActivity>('/admin/dashboard/recent-activity', { params: { limit } })
  },

  // 获取图表数据
  getChartData(params?: { period?: string; metric?: string }) {
    return request.get<ChartData>('/admin/dashboard/chart-data', { params })
  },

  // 获取操作日志
  getOperationLogs(params?: {
    page?: number
    page_size?: number
    action?: string
    admin_id?: number
    start_date?: string
    end_date?: string
  }) {
    return request.get<{ items: OperationLog[]; total: number }>('/admin/logs/operations', { params })
  },

  // 获取登录日志
  getLoginLogs(params?: {
    page?: number
    page_size?: number
    username?: string
    success?: boolean
    start_date?: string
    end_date?: string
  }) {
    return request.get<{ items: LoginLog[]; total: number }>('/admin/logs/login', { params })
  },

  // 获取系统状态
  getSystemStatus() {
    return request.get<SystemStatus>('/admin/system/status')
  },

  // 获取系统指标
  getSystemMetrics() {
    return request.get<SystemMetrics>('/admin/system/metrics')
  },

  // 获取数据库统计
  getDbStats() {
    return request.get<Record<string, number>>('/admin/system/db-stats')
  },

  // 获取角色列表
  getRoles(params?: { page?: number; page_size?: number }) {
    return request.get<{ items: Role[]; total: number }>('/admin/roles', { params })
  },

  // 获取单个角色
  getRole(roleId: number) {
    return request.get<Role>(`/admin/roles/${roleId}`)
  },

  // 创建角色
  createRole(data: Partial<Role>) {
    return request.post<Role>('/admin/roles', data)
  },

  // 更新角色
  updateRole(roleId: number, data: Partial<Role>) {
    return request.put<Role>(`/admin/roles/${roleId}`, data)
  },

  // 删除角色
  deleteRole(roleId: number) {
    return request.delete(`/admin/roles/${roleId}`)
  },

  // 获取权限列表
  getPermissions() {
    return request.get<Record<string, string>>('/admin/roles/permissions')
  },

  // 更新用户角色
  updateUserRole(userId: number, roleId: number) {
    return request.put(`/admin/users/${userId}/role`, { role_id: roleId })
  },

  // 获取植物知识库
  getPlantKnowledge(params?: { page?: number; page_size?: number; search?: string }) {
    return request.get<{ items: KnowledgePlant[]; total: number }>('/admin/knowledge/plants', { params })
  },

  // 获取植物知识库详情
  getPlantKnowledgeDetail(plantId: number) {
    return request.get<KnowledgePlant>(`/admin/knowledge/plants/${plantId}`)
  },

  // 创建植物知识
  createPlantKnowledge(data: Partial<KnowledgePlant>) {
    return request.post<KnowledgePlant>('/admin/knowledge/plants', data)
  },

  // 更新植物知识
  updatePlantKnowledge(plantId: number, data: Partial<KnowledgePlant>) {
    return request.put<KnowledgePlant>(`/admin/knowledge/plants/${plantId}`, data)
  },

  // 删除植物知识
  deletePlantKnowledge(plantId: number) {
    return request.delete(`/admin/knowledge/plants/${plantId}`)
  },

  // 获取病害知识库
  getDiseaseKnowledge(params?: { page?: number; page_size?: number; search?: string }) {
    return request.get<{ items: KnowledgeDisease[]; total: number }>('/admin/knowledge/diseases', { params })
  },

  // 获取病害知识库详情
  getDiseaseKnowledgeDetail(diseaseId: number) {
    return request.get<KnowledgeDisease>(`/admin/knowledge/diseases/${diseaseId}`)
  },

  // 创建病害知识
  createDiseaseKnowledge(data: Partial<KnowledgeDisease>) {
    return request.post<KnowledgeDisease>('/admin/knowledge/diseases', data)
  },

  // 更新病害知识
  updateDiseaseKnowledge(diseaseId: number, data: Partial<KnowledgeDisease>) {
    return request.put<KnowledgeDisease>(`/admin/knowledge/diseases/${diseaseId}`, data)
  },

  // 删除病害知识
  deleteDiseaseKnowledge(diseaseId: number) {
    return request.delete(`/admin/knowledge/diseases/${diseaseId}`)
  },

  // 获取养护技巧
  getCareTips(params?: { page?: number; page_size?: number; category?: string }) {
    return request.get<{ items: KnowledgeTip[]; total: number }>('/admin/knowledge/care-tips', { params })
  },

  // 获取养护技巧详情
  getCareTipDetail(tipId: number) {
    return request.get<KnowledgeTip>(`/admin/knowledge/care-tips/${tipId}`)
  },

  // 创建养护技巧
  createCareTip(data: Partial<KnowledgeTip>) {
    return request.post<KnowledgeTip>('/admin/knowledge/care-tips', data)
  },

  // 更新养护技巧
  updateCareTip(tipId: number, data: Partial<KnowledgeTip>) {
    return request.put<KnowledgeTip>(`/admin/knowledge/care-tips/${tipId}`, data)
  },

  // 删除养护技巧
  deleteCareTip(tipId: number) {
    return request.delete(`/admin/knowledge/care-tips/${tipId}`)
  },

  // 获取知识库统计
  getKnowledgeStats() {
    return request.get<{ plants: number; diseases: number; care_tips: number; total: number }>('/admin/knowledge/stats')
  },
}

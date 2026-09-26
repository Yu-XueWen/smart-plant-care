// 登录参数
export interface LoginParams {
  username: string
  password: string
}

// 注册参数
export interface RegisterParams {
  username: string
  password: string
  email?: string
  phone?: string
}

// Token 响应
export interface TokenResponse {
  access_token: string
  refresh_token: string
  expires_in: number
  user: UserInfo
}

// 用户信息
export interface UserInfo {
  id: number
  username: string
  email: string
  phone: string | null
  role: 'user' | 'admin'
  status: number
  created_at: string
}

// API 响应
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}
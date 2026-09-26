import request from '../request'
import type { LoginParams, RegisterParams, TokenResponse, UserInfo } from '@/types/api'

export const authApi = {
  // 登录
  login(data: LoginParams) {
    return request.post<TokenResponse>('/auth/login', data)
  },

  // 注册
  register(data: RegisterParams) {
    return request.post<{ message: string }>('/auth/register', data)
  },

  // 获取当前用户信息
  getMe() {
    return request.get<UserInfo>('/auth/me')
  },

  // 修改密码
  changePassword(oldPassword: string, newPassword: string) {
    return request.post<{ message: string }>('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  },

  // 更新个人信息
  updateProfile(data: Partial<UserInfo>) {
    return request.put<UserInfo>('/auth/profile', data)
  },
}

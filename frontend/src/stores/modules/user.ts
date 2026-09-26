import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/modules/auth'
import type { UserInfo } from '@/types/api'
import { setToken, getToken, removeToken } from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(getToken() || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => userInfo.value?.role || 'user')

  // 登录
  async function login(username: string, password: string) {
    const res = await authApi.login({ username, password })
    token.value = res.access_token
    setToken(res.access_token)
    await fetchUserInfo()
    return res
  }

  // 注册
  async function register(data: { username: string; password: string; email?: string; phone?: string }) {
    return authApi.register(data)
  }

  // 获取用户信息
  async function fetchUserInfo() {
    const res = await authApi.getMe()
    userInfo.value = res
    return res
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = null
    removeToken()
  }

  // 恢复会话
  async function restoreSession() {
    if (!token.value) {
      return
    }
    
    try {
      await fetchUserInfo()
    } catch (error) {
      console.error('获取用户信息失败，清除 token')
      logout()
      throw error
    }
  }

  // 修改密码
  async function changePassword(oldPassword: string, newPassword: string) {
    return authApi.changePassword(oldPassword, newPassword)
  }

  // 更新个人信息
  async function updateProfile(data: Partial<UserInfo>) {
    await authApi.updateProfile(data)
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...data }
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    userRole,
    login,
    register,
    logout,
    restoreSession,
    fetchUserInfo,
    changePassword,
    updateProfile,
  }
})
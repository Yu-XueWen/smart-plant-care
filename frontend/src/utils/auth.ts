/**
 * 认证工具函数
 */
import { STORAGE_KEYS } from './constants'

/**
 * 获取 token
 */
export function getToken(): string | null {
  return localStorage.getItem(STORAGE_KEYS.TOKEN)
}

/**
 * 设置 token
 */
export function setToken(token: string): void {
  localStorage.setItem(STORAGE_KEYS.TOKEN, token)
}

/**
 * 移除 token
 */
export function removeToken(): void {
  localStorage.removeItem(STORAGE_KEYS.TOKEN)
}

/**
 * 检查是否已登录
 */
export function isAuthenticated(): boolean {
  return !!getToken()
}

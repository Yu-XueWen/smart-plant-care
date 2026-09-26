/**
 * 本地存储工具函数
 */

/**
 * 设置存储项
 */
export function setStorage(key: string, value: any): void {
  try {
    const data = JSON.stringify(value)
    localStorage.setItem(key, data)
  } catch (error) {
    console.error('设置存储失败:', error)
  }
}

/**
 * 获取存储项
 */
export function getStorage<T = any>(key: string): T | null {
  try {
    const data = localStorage.getItem(key)
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error('获取存储失败:', error)
    return null
  }
}

/**
 * 移除存储项
 */
export function removeStorage(key: string): void {
  localStorage.removeItem(key)
}

/**
 * 清空所有存储
 */
export function clearStorage(): void {
  localStorage.clear()
}

/**
 * 设置会话存储
 */
export function setSessionStorage(key: string, value: any): void {
  try {
    const data = JSON.stringify(value)
    sessionStorage.setItem(key, data)
  } catch (error) {
    console.error('设置会话存储失败:', error)
  }
}

/**
 * 获取会话存储
 */
export function getSessionStorage<T = any>(key: string): T | null {
  try {
    const data = sessionStorage.getItem(key)
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error('获取会话存储失败:', error)
    return null
  }
}

/**
 * 移除会话存储
 */
export function removeSessionStorage(key: string): void {
  sessionStorage.removeItem(key)
}

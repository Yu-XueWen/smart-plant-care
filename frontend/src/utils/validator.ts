/**
 * 验证用户名
 */
export function validateUsername(username: string): boolean {
  const regex = /^[a-zA-Z0-9_]{3,50}$/
  return regex.test(username)
}

/**
 * 验证密码
 */
export function validatePassword(password: string): boolean {
  return password.length >= 6 && password.length <= 100
}

/**
 * 验证邮箱
 */
export function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

/**
 * 验证手机号（中国大陆）
 */
export function validatePhone(phone: string): boolean {
  const regex = /^1[3-9]\d{9}$/
  return regex.test(phone)
}
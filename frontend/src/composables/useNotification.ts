/**
 * 通知逻辑组合式函数
 */
import { ElNotification, ElMessage } from 'element-plus'

export interface NotificationOptions {
  title?: string
  message: string
  type?: 'success' | 'warning' | 'info' | 'error'
  duration?: number
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
}

export function useNotification() {
  /**
   * 显示通知
   */
  function show(options: NotificationOptions) {
    const {
      title = '提示',
      message,
      type = 'info',
      duration = 4500,
      position = 'top-right'
    } = options
    
    ElNotification({
      title,
      message,
      type,
      duration,
      position
    })
  }
  
  /**
   * 显示成功通知
   */
  function success(message: string, title?: string) {
    show({ title, message, type: 'success' })
  }
  
  /**
   * 显示警告通知
   */
  function warning(message: string, title?: string) {
    show({ title, message, type: 'warning' })
  }
  
  /**
   * 显示错误通知
   */
  function error(message: string, title?: string) {
    show({ title, message, type: 'error' })
  }
  
  /**
   * 显示信息通知
   */
  function info(message: string, title?: string) {
    show({ title, message, type: 'info' })
  }
  
  /**
   * 显示消息提示
   */
  function showMessage(message: string, type: 'success' | 'warning' | 'info' | 'error' = 'info') {
    ElMessage({
      message,
      type
    })
  }
  
  return {
    show,
    success,
    warning,
    error,
    info,
    showMessage
  }
}

/**
 * 浏览器通知工具
 * 用于申请通知权限和发送桌面通知
 */

export interface NotificationOptions {
  title: string
  body?: string
  icon?: string
  tag?: string
  requireInteraction?: boolean
}

/**
 * 检查浏览器是否支持通知
 */
export function isNotificationSupported(): boolean {
  return 'Notification' in window
}

/**
 * 获取当前通知权限状态
 */
export function getNotificationPermission(): NotificationPermission {
  if (!isNotificationSupported()) {
    return 'denied'
  }
  return Notification.permission
}

/**
 * 请求通知权限
 * @returns 用户授予的权限状态
 */
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!isNotificationSupported()) {
    console.warn('当前浏览器不支持桌面通知')
    return 'denied'
  }

  // 如果已经有权限，直接返回
  if (Notification.permission === 'granted') {
    return 'granted'
  }

  // 如果用户已经拒绝，提示如何重置
  if (Notification.permission === 'denied') {
    console.warn('用户已拒绝通知权限')
    console.info('如需启用通知，请在浏览器设置中重置权限：')
    console.info('1. 点击地址栏左侧的锁图标或信息图标')
    console.info('2. 找到"通知"选项')
    console.info('3. 将权限改为"允许"')
    console.info('4. 刷新页面')
    return 'denied'
  }

  // 请求权限
  try {
    const permission = await Notification.requestPermission()
    return permission
  } catch (error) {
    console.error('请求通知权限失败:', error)
    return 'denied'
  }
}

/**
 * 发送桌面通知
 * @param options 通知选项
 * @returns 是否成功发送
 */
export function sendNotification(options: NotificationOptions): boolean {
  if (!isNotificationSupported()) {
    console.warn('当前浏览器不支持桌面通知')
    return false
  }

  // 检查权限
  if (Notification.permission !== 'granted') {
    console.warn('没有通知权限，请先申请权限')
    return false
  }

  try {
    const notification = new Notification(options.title, {
      body: options.body || '',
      icon: options.icon || '/favicon.ico',
      tag: options.tag || 'plant-care-notification',
      requireInteraction: options.requireInteraction || false
    })

    // 点击通知时关闭
    notification.onclick = () => {
      window.focus()
      notification.close()
    }

    // 5秒后自动关闭（除非设置了requireInteraction）
    if (!options.requireInteraction) {
      setTimeout(() => {
        notification.close()
      }, 5000)
    }

    return true
  } catch (error) {
    console.error('发送通知失败:', error)
    return false
  }
}

/**
 * 初始化通知功能
 * 在应用启动时调用，预先申请权限
 */
export async function initNotifications(): Promise<boolean> {
  if (!isNotificationSupported()) {
    console.log('当前浏览器不支持桌面通知功能')
    return false
  }

  const permission = await requestNotificationPermission()
  
  if (permission === 'granted') {
    console.log('✅ 通知权限已授予')
    return true
  } else {
    console.warn('⚠️ 通知权限未授予:', permission)
    console.info('💡 提示：如需启用通知，请手动重置浏览器权限')
    return false
  }
}

/**
 * 显示通知权限引导对话框
 * 当用户拒绝权限后，可以调用此函数显示指导信息
 */
export function showPermissionGuide(): void {
  if (!isNotificationSupported()) {
    alert('您的浏览器不支持桌面通知功能')
    return
  }

  const permission = Notification.permission
  
  if (permission === 'granted') {
    alert('✅ 通知权限已授予，可以正常接收提醒！')
    return
  }

  let message = ''
  if (permission === 'denied') {
    message = '⚠️ 您之前拒绝了通知权限\n\n'
    message += '如需启用通知，请按以下步骤操作：\n\n'
    message += '方法1（推荐）：\n'
    message += '1. 点击地址栏左侧的 🔒 锁图标\n'
    message += '2. 找到“通知”选项\n'
    message += '3. 将权限改为“允许”\n'
    message += '4. 刷新页面\n\n'
    message += '方法2：\n'
    message += '1. 打开浏览器设置\n'
    message += '2. 搜索“网站设置”或“内容设置”\n'
    message += '3. 找到“通知”\n'
    message += '4. 在“不允许发送通知”列表中找到本网站\n'
    message += '5. 删除或改为“允许”\n'
    message += '6. 刷新页面'
  } else {
    message = '🔔 点击“确定”申请通知权限'
    Notification.requestPermission().then(perm => {
      if (perm === 'granted') {
        alert('✅ 通知权限已授予！')
      } else {
        showPermissionGuide() // 递归显示指导
      }
    })
    return
  }
  
  alert(message)
}

/**
 * 发送浇水提醒通知
 * @param plantName 植物名称
 * @param nickname 植物昵称
 */
export function sendWateringReminder(plantName: string, nickname?: string): boolean {
  const displayName = nickname ? `${plantName} (${nickname})` : plantName
  
  return sendNotification({
    title: '💧 浇水提醒',
    body: `${displayName} 需要浇水啦！`,
    icon: '/favicon.ico',
    tag: `watering-${plantName}`,
    requireInteraction: true
  })
}

/**
 * 发送多个植物的浇水提醒
 * @param plants 植物列表
 */
export function sendBatchWateringReminder(plants: Array<{ name: string; nickname?: string }>): void {
  if (plants.length === 0) return

  if (plants.length === 1) {
    // 单个植物，发送详细通知
    sendWateringReminder(plants[0].name, plants[0].nickname)
  } else {
    // 多个植物，发送汇总通知
    const plantNames = plants.map(p => p.nickname ? `${p.name}(${p.nickname})` : p.name).join('、')
    
    sendNotification({
      title: `💧 浇水提醒 (${plants.length}盆植物)`,
      body: `以下植物需要浇水：${plantNames}`,
      icon: '/favicon.ico',
      tag: 'batch-watering-reminder',
      requireInteraction: true
    })
  }
}

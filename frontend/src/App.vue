<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/modules/user'
import { initNotifications, sendNotification } from '@/utils/notification'
import { careReminderApi } from '@/api/modules/careReminder'

const userStore = useUserStore()
let pollingTimer: number | null = null
let lastNotifiedReminders = new Set<number>() // 记录已发送通知的提醒ID

onMounted(async () => {
  // 尝试恢复登录状态，但不阻塞页面渲染
  try {
    await userStore.restoreSession()
  } catch (error) {
    console.error('恢复会话失败:', error)
  }
  
  // 如果用户已登录，初始化通知权限并启动轮询
  if (userStore.isLoggedIn) {
    setTimeout(() => {
      initNotifications().then(granted => {
        if (granted) {
          console.log('✅ 通知功能已启用')
          // 启动提醒轮询
          startReminderPolling()
        }
      })
    }, 1000) // 延迟1秒，避免影响页面加载
  }
})

// 启动提醒轮询
function startReminderPolling() {
  // 立即检查一次
  checkTodayReminders()
  
  // 每5分钟检查一次
  pollingTimer = window.setInterval(() => {
    checkTodayReminders()
  }, 5 * 60 * 1000) // 5分钟
  
  console.log('🔔 提醒轮询已启动（每5分钟检查一次）')
}

// 检查今日提醒
async function checkTodayReminders() {
  if (!userStore.isLoggedIn) return
  
  try {
    const response = await careReminderApi.getReminders({
      page: 1,
      page_size: 100,
      status_filter: undefined // 获取所有状态的提醒
    })
    
    // 过滤出今天需要执行的提醒
    const todayReminders = response.items.filter(reminder => 
      reminder.status === 'today' && reminder.is_enabled
    )
    
    if (todayReminders.length > 0) {
      console.log(`📢 发现 ${todayReminders.length} 个今日待执行提醒`)
      
      // 为每个新提醒发送通知
      todayReminders.forEach(reminder => {
        // 如果这个提醒还没有发送过通知
        if (!lastNotifiedReminders.has(reminder.id)) {
          sendReminderNotification(reminder)
          lastNotifiedReminders.add(reminder.id)
        }
      })
    }
  } catch (error) {
    console.error('检查提醒失败:', error)
  }
}

// 发送提醒通知
function sendReminderNotification(reminder: any) {
  const plantName = reminder.nickname || reminder.plant_name || '植物'
  
  let title = ''
  let body = ''
  
  switch (reminder.remind_type) {
    case 'water':
      title = '💧 浇水提醒'
      body = `该给 ${plantName} 浇水啦！`
      break
    case 'fertilize':
      title = '🌱 施肥提醒'
      body = `该给 ${plantName} 施肥了！`
      break
    case 'pesticide':
      title = '🛡️ 施药提醒'
      body = `该给 ${plantName} 进行病虫害防治了！`
      break
    case 'prune':
      title = '✂️ 修剪提醒'
      body = `该给 ${plantName} 修剪了！`
      break
    default:
      title = '📋 养护提醒'
      body = `${plantName} 有新的养护任务！`
  }
  
  // 添加产品信息（如果有）
  if (reminder.product_name) {
    body += `\n产品：${reminder.product_name}`
  }
  if (reminder.dosage) {
    body += `\n用量：${reminder.dosage}`
  }
  
  sendNotification({
    title,
    body,
    tag: `reminder-${reminder.id}`,
    requireInteraction: true
  })
  
  console.log(`📢 已发送通知: ${title} - ${body}`)
}

// 组件卸载时清除定时器
onUnmounted(() => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
    console.log('🔕 提醒轮询已停止')
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}
</style>
<template>
  <div class="watering-reminder-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>💧 浇水提醒</h2>
      <p class="subtitle">智能浇水管理</p>
    </div>

    <!-- 今日日期和统计 -->
    <el-card class="stats-card" v-if="todayReminders">
      <div class="stats-content">
        <div class="stat-item">
          <div class="stat-label">今日日期</div>
          <div class="stat-value">{{ formatDate(todayReminders.date) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">待浇水植物</div>
          <div class="stat-value highlight">{{ pendingCount }} 盆</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">已完成</div>
          <div class="stat-value success">{{ completedCount }} 盆</div>
        </div>
      </div>
    </el-card>

    <!-- 今日待浇水列表 -->
    <el-card class="today-reminders-card" v-if="pendingCount > 0">
      <template #header>
        <div class="card-header">
          <h3>⏰ 今日待浇水</h3>
          <el-tag type="warning" size="large">{{ pendingCount }} 盆需要浇水</el-tag>
        </div>
      </template>

      <div class="reminders-list" v-loading="loading">
        <el-card 
          v-for="reminder in pendingReminders" 
          :key="reminder.reminder_id"
          class="reminder-card"
        >
          <div class="reminder-header">
            <div class="plant-info">
              <h3 class="plant-name">{{ reminder.plant_name }}</h3>
              <span class="nickname" v-if="reminder.nickname">{{ reminder.nickname }}</span>
            </div>
          </div>

          <!-- 时间段显示 -->
          <div class="time-slots">
            <div class="slot-label">提醒时间：</div>
            <div class="slots">
              <div 
                v-for="slot in reminder.time_slots" 
                :key="slot.slot"
                class="time-slot"
                :class="{ active: isCurrentTimeSlot(slot.time) }"
              >
                <span class="slot-time">{{ slot.time }}</span>
                <span class="slot-label-text">{{ slot.label }}</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="reminder-actions">
            <el-button 
              type="success" 
              size="large"
              @click="handleComplete(reminder)"
            >
              <el-icon><Select /></el-icon>
              已经浇过水啦
            </el-button>
            <el-button 
              type="warning" 
              size="large"
              @click="handlePostpone(reminder)"
            >
              <el-icon><Clock /></el-icon>
              推迟浇水
            </el-button>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 所有盆栽下次浇水时间表 -->
    <el-card class="schedule-card">
      <template #header>
        <div class="card-header">
          <h3>📅 下次浇水计划</h3>
          <el-button type="primary" size="small" @click="fetchScheduleData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table 
        :data="scheduleData" 
        style="width: 100%" 
        v-loading="scheduleLoading"
        :default-sort="{ prop: 'next_watering_date', order: 'ascending' }"
      >
        <el-table-column prop="plant_name" label="植物名称" width="150">
          <template #default="{ row }">
            <div class="plant-name-cell">
              <strong>{{ row.plant_name }}</strong>
              <span class="nickname" v-if="row.nickname">({{ row.nickname }})</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="current_season" label="当前季节" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeasonTagType(row.current_season)" size="small">
              {{ row.season_name }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="interval_days" label="浇水间隔" width="100" align="center">
          <template #default="{ row }">
            <span class="interval-days">{{ row.interval_days }} 天</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="next_watering_date" label="下次浇水日期" width="130" sortable>
          <template #default="{ row }">
            <div class="date-cell" :class="{ 'overdue': isOverdue(row.next_watering_date) }">
              <el-icon v-if="isOverdue(row.next_watering_date)" class="warning-icon"><WarningFilled /></el-icon>
              <span>{{ formatDate(row.next_watering_date) }}</span>
              <el-tag v-if="isToday(row.next_watering_date)" type="danger" size="small" style="margin-left: 8px">
                今天
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="last_watering_date" label="上次浇水日期" width="130">
          <template #default="{ row }">
            <div class="date-cell">
              <span v-if="row.last_watering_date">{{ formatDate(row.last_watering_date) }}</span>
              <span v-else class="no-record">暂无记录</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="days_remaining" label="剩余天数" width="100" align="center" sortable>
          <template #default="{ row }">
            <div class="days-remaining" :class="getDaysClass(row.days_remaining)">
              <span v-if="row.days_remaining > 0">{{ row.days_remaining }} 天后</span>
              <span v-else-if="row.days_remaining === 0" class="today-text">今天</span>
              <span v-else class="overdue-text">已逾期 {{ Math.abs(row.days_remaining) }} 天</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.days_remaining)" size="small">
              {{ getStatusText(row.days_remaining) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" min-width="120" align="center">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small"
              @click="setupReminderForPlant(row.plant_id)"
            >
              设置提醒
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!scheduleLoading && scheduleData.length === 0" description="暂无盆栽数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled, Select, Clock, Refresh } from '@element-plus/icons-vue'
import { 
  getTodayReminders, 
  completeWateringReminder, 
  postponeWateringReminder,
  setupWateringReminder,
  getReminderConfig,
  type TodayRemindersResponse,
  type TodayReminderItem
} from '@/api/modules/wateringReminder'
import { plantApi } from '@/api/modules/plant'
import { 
  initNotifications, 
  sendBatchWateringReminder,
  getNotificationPermission,
  isNotificationSupported
} from '@/utils/notification'

const loading = ref(false)
const scheduleLoading = ref(false)
const todayReminders = ref<TodayRemindersResponse | null>(null)
const scheduleData = ref<any[]>([])

// 定时器相关
let checkInterval: number | null = null
let lastCheckTime = 0
const CHECK_INTERVAL = 60000 // 每分钟检查一次

// 计算属性 - 待浇水的提醒
const pendingReminders = computed(() => {
  return todayReminders.value?.reminders.filter(r => r.status === 'pending') || []
})

const pendingCount = computed(() => {
  return pendingReminders.value.length
})

const completedCount = computed(() => {
  return todayReminders.value?.reminders.filter(r => r.status === 'completed').length || 0
})

// 获取今日提醒
async function fetchTodayReminders() {
  loading.value = true
  try {
    const response = await getTodayReminders()
    if (response.code === 200 && response.data) {
      todayReminders.value = response.data
    }
  } catch (error) {
    ElMessage.error('获取提醒列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 初始化通知权限
async function initNotificationPermission() {
  if (!isNotificationSupported()) {
    console.log('当前浏览器不支持桌面通知')
    return
  }

  const permission = getNotificationPermission()
  
  if (permission === 'default') {
    // 首次访问，请求权限
    try {
      await ElMessageBox.confirm(
        '是否允许发送桌面通知？这样即使您不在当前页面，也能及时收到浇水提醒。',
        '通知权限申请',
        {
          confirmButtonText: '允许',
          cancelButtonText: '拒绝',
          type: 'info'
        }
      )
      
      const result = await initNotifications()
      if (result) {
        ElMessage.success('通知权限已授予')
      } else {
        ElMessage.warning('通知权限未授予，您将无法收到桌面提醒')
      }
    } catch (error) {
      // 用户取消
      console.log('用户拒绝通知权限')
    }
  } else if (permission === 'denied') {
    console.log('用户已拒绝通知权限')
  }
}

// 检查并发送通知
function checkAndNotify() {
  if (!todayReminders.value || pendingReminders.value.length === 0) {
    return
  }

  const now = Date.now()
  // 避免重复通知（5分钟内不重复）
  if (now - lastCheckTime < 5 * 60 * 1000) {
    return
  }

  const permission = getNotificationPermission()
  if (permission !== 'granted') {
    return
  }

  // 发送批量通知
  const plants = pendingReminders.value.map(reminder => ({
    name: reminder.plant_name,
    nickname: reminder.nickname
  }))

  sendBatchWateringReminder(plants)
  lastCheckTime = now
}

// 启动定时检查
function startPeriodicCheck() {
  // 清除旧的定时器
  if (checkInterval) {
    clearInterval(checkInterval)
  }

  // 设置新的定时器，每分钟检查一次
  checkInterval = window.setInterval(() => {
    // 只在有待浇水植物时检查
    if (pendingReminders.value.length > 0) {
      checkAndNotify()
    }
  }, CHECK_INTERVAL)

  console.log('定时检查已启动，间隔:', CHECK_INTERVAL / 1000, '秒')
}

// 停止定时检查
function stopPeriodicCheck() {
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
    console.log('定时检查已停止')
  }
}

// 获取所有盆栽的浇水计划
async function fetchScheduleData() {
  scheduleLoading.value = true
  try {
    console.log('=== 开始获取浇水计划 ===')
    // 获取用户的所有盆栽
    const response = await plantApi.getMyPlants({ page: 1, page_size: 100 })
    console.log('盆栽列表响应:', response)
    
    // 注意：响应拦截器已经解包了 data，所以 response 直接就是 {total, items}
    if (response && response.items) {
      const plants = response.items || []
      console.log(`找到 ${plants.length} 个盆栽`)
      
      if (plants.length === 0) {
        ElMessage.warning('暂无盆栽数据')
        scheduleData.value = []
        return
      }
      
      // 为每个盆栽获取浇水提醒配置
      const schedulePromises = plants.map(async (plant: any) => {
        try {
          console.log(`\n处理植物: ${plant.plant_name} (ID: ${plant.id})`)
          
          // 先尝试获取现有配置
          // 注意：响应拦截器已经解包了 data，所以 config 直接就是 WateringReminderConfig 或 null
          let config = await getReminderConfig(plant.id)
          console.log('获取配置响应:', config)
          
          // 如果没有配置，则创建新配置
          if (!config) {
            console.log('未找到配置，创建新配置...')
            config = await setupWateringReminder(plant.id)
            console.log('创建配置响应:', config)
          }
          
          if (config) {
            console.log('配置数据:', config)
            
            // 检查必要字段是否存在
            if (!(config as any).scheduled_date) {
              console.error('配置中缺少 scheduled_date 字段!', config)
              return null
            }
            
            const nextDate = new Date((config as any).scheduled_date)
            const today = new Date()
            today.setHours(0, 0, 0, 0)
            nextDate.setHours(0, 0, 0, 0)
            
            const diffTime = nextDate.getTime() - today.getTime()
            const daysRemaining = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
            
            const result = {
              plant_id: plant.id,
              plant_name: plant.plant_name,
              nickname: plant.nickname,
              current_season: (config as any).current_season,
              season_name: (config as any).season_name,
              interval_days: (config as any).interval_days,
              next_watering_date: (config as any).scheduled_date,
              last_watering_date: (config as any).last_watering_date || null,
              days_remaining: daysRemaining
            }
            console.log('处理结果:', result)
            return result
          } else {
            console.warn('配置为空')
          }
        } catch (error) {
          console.error(`获取植物 ${plant.plant_name} 的提醒配置失败:`, error)
          // 单个植物失败不影响其他植物
        }
        return null
      })
      
      const results = await Promise.all(schedulePromises)
      console.log('\n所有结果:', results)
      scheduleData.value = results.filter(item => item !== null) as any[]
      console.log(`最终显示 ${scheduleData.value.length} 条浇水计划`)
    } else {
      console.error('获取盆栽列表失败:', response)
      ElMessage.error('获取盆栽列表失败')
    }
  } catch (error) {
    ElMessage.error('获取浇水计划失败')
    console.error('获取浇水计划异常:', error)
  } finally {
    scheduleLoading.value = false
  }
}

// 为单个植物设置提醒
async function setupReminderForPlant(plantId: number) {
  try {
    const config = await setupWateringReminder(plantId)
    if (config) {
      ElMessage.success('提醒设置成功')
      // 刷新计划表
      await fetchScheduleData()
    } else {
      ElMessage.error('设置提醒失败')
    }
  } catch (error) {
    ElMessage.error('设置提醒失败')
    console.error(error)
  }
}

// 完成浇水
async function handleComplete(reminder: TodayReminderItem) {
  try {
    // 确定当前时间段
    const currentTime = new Date()
    const currentHour = currentTime.getHours()
    let timeSlot: 'morning' | 'noon' | 'evening' = 'morning'
    
    if (currentHour >= 11 && currentHour < 14) {
      timeSlot = 'noon'
    } else if (currentHour >= 14) {
      timeSlot = 'evening'
    }

    const response = await completeWateringReminder(reminder.reminder_id, timeSlot)
    
    if (response.code === 200 && response.data) {
      ElMessage.success(response.data.message)
      // 刷新列表
      await fetchTodayReminders()
      // 刷新计划表
      await fetchScheduleData()
    }
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
  }
}

// 推迟浇水
async function handlePostpone(reminder: TodayReminderItem) {
  try {
    await ElMessageBox.confirm(
      '推迟后将在24小时后再次提醒，确定要推迟吗？',
      '推迟浇水',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await postponeWateringReminder(reminder.reminder_id, 24)
    
    if (response.code === 200 && response.data) {
      ElMessage.info(response.data.message)
      // 刷新列表
      await fetchTodayReminders()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

// 格式化日期
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

// 判断是否逾期
function isOverdue(dateStr: string): boolean {
  const date = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  date.setHours(0, 0, 0, 0)
  return date < today
}

// 判断是否是今天
function isToday(dateStr: string): boolean {
  const date = new Date(dateStr)
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

// 获取季节标签类型
function getSeasonTagType(season: string): 'success' | 'warning' | 'danger' | 'info' {
  switch (season) {
    case 'spring': return 'success'
    case 'summer': return 'danger'
    case 'autumn': return 'warning'
    case 'winter': return 'info'
    default: return 'info'
  }
}

// 获取天数样式类
function getDaysClass(days: number): string {
  if (days < 0) return 'overdue'
  if (days === 0) return 'today'
  if (days <= 3) return 'soon'
  return 'normal'
}

// 获取状态标签类型
function getStatusTagType(days: number): 'success' | 'warning' | 'danger' | 'info' {
  if (days < 0) return 'danger'
  if (days === 0) return 'warning'
  if (days <= 3) return 'warning'
  return 'success'
}

// 获取状态文本
function getStatusText(days: number): string {
  if (days < 0) return '已逾期'
  if (days === 0) return '今天'
  if (days <= 3) return '即将到期'
  return '正常'
}

// 判断是否是当前时间段
function isCurrentTimeSlot(timeStr: string): boolean {
  const [hours] = timeStr.split(':').map(Number)
  const currentHour = new Date().getHours()
  
  if (hours === 7 && currentHour >= 6 && currentHour < 11) return true
  if (hours === 12 && currentHour >= 11 && currentHour < 14) return true
  if (hours === 18 && currentHour >= 14) return true
  
  return false
}

// 页面加载时获取数据
onMounted(async () => {
  // 初始化通知权限
  await initNotificationPermission()
  
  // 获取数据
  await fetchTodayReminders()
  await fetchScheduleData()
  
  // 启动定时检查
  startPeriodicCheck()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopPeriodicCheck()
})
</script>

<style scoped lang="scss">
.watering-reminder-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 24px;

    h2 {
      font-size: 28px;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .stats-card {
    margin-bottom: 24px;

    .stats-content {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }

    .stat-item {
      text-align: center;
      padding: 16px;
      background: linear-gradient(135deg, #f5f7fa 0%, #fafbfc 100%);
      border-radius: 8px;

      .stat-label {
        font-size: 13px;
        color: #909399;
        margin-bottom: 8px;
      }

      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #303133;

        &.highlight {
          color: #409eff;
        }

        &.success {
          color: #67c23a;
        }
      }
    }
  }

  .today-reminders-card {
    margin-bottom: 24px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h3 {
        font-size: 18px;
        margin: 0;
      }
    }
  }

  .reminders-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .reminder-card {
    transition: all 0.3s;
    border-left: 4px solid #409eff;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .reminder-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .plant-info {
        .plant-name {
          font-size: 20px;
          font-weight: bold;
          color: #303133;
          margin: 0 0 4px 0;
        }

        .nickname {
          font-size: 13px;
          color: #909399;
        }
      }
    }

    .time-slots {
      margin-bottom: 16px;
      padding: 12px;
      background: #f5f7fa;
      border-radius: 6px;

      .slot-label {
        font-size: 13px;
        color: #606266;
        margin-bottom: 8px;
      }

      .slots {
        display: flex;
        gap: 12px;
      }

      .time-slot {
        flex: 1;
        padding: 8px 12px;
        background: white;
        border-radius: 4px;
        text-align: center;
        border: 1px solid #dcdfe6;
        transition: all 0.2s;

        &.active {
          border-color: #409eff;
          background: #ecf5ff;

          .slot-time {
            color: #409eff;
            font-weight: bold;
          }
        }

        .slot-time {
          display: block;
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 2px;
        }

        .slot-label-text {
          display: block;
          font-size: 12px;
          color: #909399;
        }
      }
    }

    .reminder-actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;

      .el-button {
        min-width: 140px;

        .el-icon {
          margin-right: 6px;
        }
      }
    }
  }

  .schedule-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h3 {
        font-size: 18px;
        margin: 0;
      }
    }

    :deep(.el-table) {
      .cell {
        padding: 8px 0;
      }
    }

    .plant-name-cell {
      display: flex;
      flex-direction: column;
      gap: 2px;

      strong {
        font-size: 14px;
        color: #303133;
      }

      .nickname {
        font-size: 12px;
        color: #909399;
      }
    }

    .interval-days {
      font-size: 14px;
      font-weight: 600;
      color: #409eff;
    }

    .date-cell {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 14px;

      &.overdue {
        color: #f56c6c;
        font-weight: 600;

        .warning-icon {
          font-size: 16px;
        }
      }
      
      .no-record {
        color: #c0c4cc;
        font-style: italic;
        font-size: 12px;
      }
    }

    .days-remaining {
      font-size: 14px;
      font-weight: 600;

      &.overdue {
        color: #f56c6c;
      }

      &.today {
        color: #e6a23c;
      }

      &.soon {
        color: #e6a23c;
      }

      &.normal {
        color: #67c23a;
      }
    }

    .today-text {
      color: #e6a23c;
      font-weight: bold;
    }

    .overdue-text {
      color: #f56c6c;
      font-weight: bold;
    }
  }
}

@media (max-width: 768px) {
  .watering-reminder-page {
    padding: 12px;

    .stats-card {
      .stats-content {
        grid-template-columns: 1fr;
        gap: 12px;
      }
    }

    .reminder-card {
      .reminder-actions {
        flex-direction: column;

        .el-button {
          width: 100%;
        }
      }
    }

    .schedule-card {
      :deep(.el-table) {
        font-size: 12px;
      }
    }
  }
}
</style>
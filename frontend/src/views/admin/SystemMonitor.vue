<template>
  <div class="system-monitor">
    <el-page-header title="系统监控" @back="handleBack" />
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 系统状态卡片 -->
      <el-col :span="24">
        <el-card class="status-card">
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
              <el-tag :type="statusType" size="large">
                {{ statusLabel }}
              </el-tag>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6" v-for="component in systemStatus?.components" :key="component.name">
              <div class="component-item">
                <el-icon :size="24" :color="getComponentColor(component.status)">
                  <component :is="getComponentIcon(component.name)" />
                </el-icon>
                <div class="component-info">
                  <div class="component-name">{{ component.name }}</div>
                  <el-tag :type="getComponentTagType(component.status)" size="small">
                    {{ getComponentStatusLabel(component.status) }}
                  </el-tag>
                </div>
                <div v-if="component.message" class="component-message">
                  {{ component.message }}
                </div>
              </div>
            </el-col>
          </el-row>
          
          <el-descriptions :column="4" border style="margin-top: 20px;">
            <el-descriptions-item label="系统运行时间">
              {{ formatUptime(systemStatus?.uptime || 0) }}
            </el-descriptions-item>
            <el-descriptions-item label="最后检查时间">
              {{ formatTime(systemStatus?.last_check) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <!-- 资源使用卡片 -->
      <el-col :span="12">
        <el-card class="metrics-card">
          <template #header>
            <span>CPU 使用率</span>
          </template>
          <el-progress 
            :percentage="Math.round(systemMetrics?.cpu_percent || 0)" 
            :color="getProgressColor(systemMetrics?.cpu_percent || 0)"
            :stroke-width="20"
          />
          <div class="metrics-value">
            {{ (systemMetrics?.cpu_percent || 0).toFixed(1) }}%
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="metrics-card">
          <template #header>
            <span>内存使用</span>
          </template>
          <el-progress 
            :percentage="Math.round(systemMetrics?.memory?.percent || 0)" 
            :color="getProgressColor(systemMetrics?.memory?.percent || 0)"
            :stroke-width="20"
          />
          <div class="metrics-value">
            {{ formatBytes(systemMetrics?.memory?.used || 0) }} / {{ formatBytes(systemMetrics?.memory?.total || 0) }}
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="metrics-card">
          <template #header>
            <span>磁盘使用</span>
          </template>
          <el-progress 
            :percentage="Math.round(systemMetrics?.disk?.percent || 0)" 
            :color="getProgressColor(systemMetrics?.disk?.percent || 0)"
            :stroke-width="20"
          />
          <div class="metrics-value">
            {{ formatBytes(systemMetrics?.disk?.used || 0) }} / {{ formatBytes(systemMetrics?.disk?.total || 0) }}
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="metrics-card">
          <template #header>
            <span>进程数</span>
          </template>
          <div class="process-count">
            <el-icon :size="48"><Monitor /></el-icon>
            <div class="count-value">{{ systemMetrics?.processes || 0 }}</div>
            <div class="count-label">当前运行进程</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="db-stats-card">
          <template #header>
            <span>数据库统计</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="4" v-for="(count, table) in dbStats" :key="table">
              <div class="db-table-item">
                <div class="table-name">{{ formatTableName(table) }}</div>
                <div class="table-count">{{ count }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    
    <div style="text-align: center; margin-top: 20px;">
      <el-button type="primary" :loading="loading" @click="fetchData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Monitor, Cpu, Connection, Refresh, Setting 
} from '@element-plus/icons-vue'
import { adminApi } from '@/api/modules/admin'
import type { SystemStatus, SystemMetrics } from '@/types/models'

const router = useRouter()
const loading = ref(false)
const systemStatus = ref<SystemStatus | null>(null)
const systemMetrics = ref<SystemMetrics | null>(null)
const dbStats = ref<Record<string, number>>({})

let refreshTimer: number | null = null

const handleBack = () => {
  router.back()
}

const fetchData = async () => {
  loading.value = true
  try {
    const [status, metrics, stats] = await Promise.all([
      adminApi.getSystemStatus(),
      adminApi.getSystemMetrics(),
      adminApi.getDbStats()
    ])
    systemStatus.value = status
    systemMetrics.value = metrics
    dbStats.value = stats
  } catch (error: any) {
    ElMessage.error(error.message || '获取系统数据失败')
  } finally {
    loading.value = false
  }
}

const statusType = computed(() => {
  switch (systemStatus.value?.status) {
    case 'healthy': return 'success'
    case 'degraded': return 'warning'
    case 'critical': return 'danger'
    default: return 'info'
  }
})

const statusLabel = computed(() => {
  switch (systemStatus.value?.status) {
    case 'healthy': return '健康'
    case 'degraded': return '降级'
    case 'critical': return '严重'
    default: return '未知'
  }
})

const getComponentColor = (status: string) => {
  switch (status) {
    case 'healthy': return '#67c23a'
    case 'degraded': return '#e6a23c'
    case 'critical': return '#f56c6c'
    default: return '#909399'
  }
}

const getComponentTagType = (status: string) => {
  switch (status) {
    case 'healthy': return 'success'
    case 'degraded': return 'warning'
    case 'critical': return 'danger'
    default: return 'info'
  }
}

const getComponentStatusLabel = (status: string) => {
  switch (status) {
    case 'healthy': return '正常'
    case 'degraded': return '降级'
    case 'critical': return '严重'
    default: return '未知'
  }
}

const getComponentIcon = (name: string) => {
  const icons: Record<string, any> = {
    'database': Connection,
    'cache': Setting,
    'api': Monitor,
    'worker': Cpu
  }
  return icons[name.toLowerCase()] || Monitor
}

const getProgressColor = (percent: number) => {
  if (percent < 50) return '#67c23a'
  if (percent < 80) return '#e6a23c'
  return '#f56c6c'
}

const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${days}天 ${hours}小时 ${minutes}分钟`
}

const formatTime = (time?: string): string => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTableName = (table: string): string => {
  const names: Record<string, string> = {
    'users': '用户',
    'plants': '盆栽',
    'watering_records': '浇水记录',
    'treatment_records': '治疗记录',
    'remind_configs': '提醒配置',
    'identify_histories': '识别历史',
    'diagnose_histories': '诊断历史',
    'operation_logs': '操作日志',
    'login_logs': '登录日志'
  }
  return names[table] || table
}

onMounted(() => {
  fetchData()
  refreshTimer = window.setInterval(fetchData, 30000) // 每30秒刷新
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped lang="scss">
.system-monitor {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.component-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  
  .component-info {
    margin-left: 10px;
    flex: 1;
    
    .component-name {
      font-weight: bold;
      margin-bottom: 5px;
    }
  }
  
  .component-message {
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
  }
}

.metrics-card {
  .metrics-value {
    text-align: center;
    margin-top: 15px;
    font-size: 14px;
    color: #606266;
  }
  
  .process-count {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
    
    .count-value {
      font-size: 32px;
      font-weight: bold;
      color: #409eff;
      margin-top: 10px;
    }
    
    .count-label {
      font-size: 14px;
      color: #909399;
      margin-top: 5px;
    }
  }
}

.db-stats-card {
  .db-table-item {
    text-align: center;
    padding: 15px;
    background: #f5f7fa;
    border-radius: 8px;
    
    .table-name {
      font-size: 12px;
      color: #606266;
      margin-bottom: 8px;
      word-break: break-all;
    }
    
    .table-count {
      font-size: 24px;
      font-weight: bold;
      color: #409eff;
    }
  }
}
</style>

file_path = r"d:\Improve\smart-plant-care\frontend\src\views\admin\Dashboard.vue"

content = '''<template>
  <div class="admin-dashboard">
    <el-page-header title="管理员统计看板" @back="handleBack" />
    
    <el-loading v-if="loading" element-full-screen />
    
    <el-card v-else class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6" v-for="(stat, index) in stats" :key="index">
          <el-statistic 
            :title="stat.label" 
            :value="stat.value" 
            suffix-template="#suffix"
            class="stat-item"
          >
            <template #suffix>
              <span class="stat-suffix">{{ stat.suffix }}</span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
      
      <el-describe :bordered="true" style="margin-top: 20px;">
        <el-describe-item label="更新时间" :label-style="{ 'font-weight': 'bold' }">
          {{ formattedTime }}
        </el-describe-item>
      </el-describe>
    </el-card>
    
    <el-card v-if="error" class="error-card">
      <el-alert type="error" :message="error.message" show-icon />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

// 定义统计数据类型
interface StatItem {
  label: string
  value: number | string
  suffix: string
}

interface DashboardData {
  total_users: number
  total_plants: number
  total_reminders: number
  recent_operation_logs: number
  recent_login_logs: number
  active_admins: number
  timestamp: string
}

const router = useRouter()
const loading = ref(true)
const error = ref<any>(null)
const stats = ref<StatItem[]>([])
const dashboardData = ref<DashboardData | null>(null)

// 格式化时间
const formattedTime = computed(() => {
  if (!dashboardData.value?.timestamp) return ''
  const date = new Date(dashboardData.value.timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
})

// 获取统计数据
async function fetchStats() {
  try {
    loading.value = true
    error.value = null
    
    // 调用后端 API
    const response = await request.get<DashboardData>('/admin/dashboard/summary')
    
    dashboardData.value = response
    
    // 准备统计数据卡片
    stats.value = [
      {
        label: '总用户数',
        value: response.total_users,
        suffix: '人'
      },
      {
        label: '总植物数',
        value: response.total_plants,
        suffix: '株'
      },
      {
        label: '总提醒数',
        value: response.total_reminders,
        suffix: '条'
      },
      {
        label: '今日操作日志',
        value: response.recent_operation_logs,
        suffix: '条'
      },
      {
        label: '今日登录日志',
        value: response.recent_login_logs,
        suffix: '条'
      },
      {
        label: '在线管理员',
        value: response.active_admins,
        suffix: '人'
      }
    ]
  } catch (err) {
    console.error('获取统计数据失败:', err)
    error.value = { message: '获取统计数据失败，请重试' }
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 返回按钮处理
function handleBack() {
  router.push({ name: 'AdminDashboard' })
}

// 页面加载时获取数据
onMounted(() => {
  fetchStats()
})
</script>

<style scoped lang="scss">
.admin-dashboard {
  padding: 20px;
  
  .stats-container {
    margin-top: 20px;
    
    .stat-item {
      text-align: center;
      padding: 20px;
      
      .stat-suffix {
        font-size: 18px;
        color: #606266;
      }
    }
  }
  
  .error-card {
    margin-top: 20px;
  }
}
</style>
'''

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {file_path}")
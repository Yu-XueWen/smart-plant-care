<template>
  <div class="admin-dashboard" v-loading="loading" element-full-screen>
    <el-page-header title="管理员统计看板" @back="handleBack" />
    
    <el-card v-if="!loading" class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6" v-for="(stat, index) in stats" :key="index">
          <el-statistic 
            :title="stat.label" 
            :value="stat.value"
            class="stat-item"
          >
            <template #suffix>
              <span class="stat-suffix">{{ stat.suffix }}</span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>用户增长趋势</span>
            </template>
            <v-chart :option="userGrowthChart" autoresize style="height: 300px;" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>识别与诊断趋势</span>
            </template>
            <v-chart :option="identifyDiagnoseChart" autoresize style="height: 300px;" />
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-descriptions :bordered="true">
            <el-descriptions-item label="更新时间" :label-style="{ 'font-weight': 'bold' }">
              {{ formattedTime }}
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
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
import VChart from 'vue-echarts'
import { adminApi } from '@/api/modules/admin'
import type { DashboardOverview, ChartData } from '@/types/models'

interface StatItem {
  label: string
  value: number
  suffix: string
}

const router = useRouter()
const loading = ref(true)
const error = ref<any>(null)
const stats = ref<StatItem[]>([])
const overviewData = ref<DashboardOverview | null>(null)
const chartData = ref<ChartData | null>(null)

// 格式化时间
const formattedTime = computed(() => {
  if (!overviewData.value) return ''
  const date = new Date()
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
})

// 用户增长图表配置
const userGrowthChart = computed(() => {
  const chart = chartData.value
  if (!chart || chart.metric !== 'user_growth') return {}
  const data = chart.data || []
  return {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.map((item: any) => item.date)
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '新增用户',
        type: 'line',
        smooth: true,
        data: data.map((item: any) => item.value),
        itemStyle: { color: '#409eff' }
      }
    ]
  }
})

// 识别与诊断趋势图表配置
const identifyDiagnoseChart = computed(() => {
  const chart = chartData.value
  if (!chart || chart.metric !== 'identify_diagnose') return {}
  const identifyData = chart.identify || []
  const diagnoseData = chart.diagnose || []
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['识别次数', '诊断次数'] },
    xAxis: {
      type: 'category',
      data: identifyData.map((item: any) => item.date)
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '识别次数',
        type: 'bar',
        data: identifyData.map((item: any) => item.value),
        itemStyle: { color: '#67c23a' }
      },
      {
        name: '诊断次数',
        type: 'bar',
        data: diagnoseData.map((item: any) => item.value),
        itemStyle: { color: '#e6a23c' }
      }
    ]
  }
})

// 获取统计数据
async function fetchStats() {
  try {
    loading.value = true
    error.value = null
    
    // 获取概览数据
    const overview = await adminApi.getDashboardOverview()
    overviewData.value = overview
    
    // 获取图表数据
    const chart = await adminApi.getChartData({ period: '7', metric: 'identify_diagnose' })
    chartData.value = chart
    
    // 准备统计数据卡片
    stats.value = [
      {
        label: '总用户数',
        value: overview.total_users,
        suffix: '人'
      },
      {
        label: '总植物数',
        value: overview.total_plants,
        suffix: '株'
      },
      {
        label: '识别次数',
        value: overview.identify_count || 0,
        suffix: '次'
      },
      {
        label: '诊断次数',
        value: overview.diagnose_count || 0,
        suffix: '次'
      },
      {
        label: '今日新增用户',
        value: overview.new_users_today,
        suffix: '人'
      },
      {
        label: '今日新增植物',
        value: overview.new_plants_today,
        suffix: '株'
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
  router.push('/my-plants')
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
  
  .chart-card {
    margin-top: 20px;
  }
  
  .error-card {
    margin-top: 20px;
  }
}
</style>
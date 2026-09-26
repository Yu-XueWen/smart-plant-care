<template>
  <div class="operation-log">
    <el-page-header title="操作日志" @back="handleBack" />
    
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="操作类型">
          <el-select v-model="filters.action" placeholder="全部" clearable style="width: 120px">
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员">
          <el-input v-model="filters.admin_id" placeholder="管理员ID" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="table-card">
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="管理员" width="120" />
        <el-table-column prop="action" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="目标类型" width="120" />
        <el-table-column prop="target_id" label="目标ID" width="100" />
        <el-table-column prop="detail" label="详情" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="formatDetail(row.detail)" placement="top">
              <span class="detail-text">{{ formatDetail(row.detail).slice(0, 50) }}...</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/modules/admin'
import type { OperationLog } from '@/types/models'

const router = useRouter()
const loading = ref(false)
const logs = ref<OperationLog[]>([])
const dateRange = ref<[string, string] | null>(null)

const filters = reactive({
  action: '',
  admin_id: '',
  start_date: '',
  end_date: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const handleBack = () => {
  router.back()
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    
    if (filters.action) params.action = filters.action
    if (filters.admin_id) params.admin_id = parseInt(filters.admin_id)
    if (filters.start_date) params.start_date = filters.start_date
    if (filters.end_date) params.end_date = filters.end_date
    
    const res = await adminApi.getOperationLogs(params)
    logs.value = res.items
    pagination.total = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取操作日志失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (dateRange.value) {
    filters.start_date = dateRange.value[0]
    filters.end_date = dateRange.value[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
  pagination.page = 1
  fetchLogs()
}

const handleReset = () => {
  filters.action = ''
  filters.admin_id = ''
  filters.start_date = ''
  filters.end_date = ''
  dateRange.value = null
  pagination.page = 1
  fetchLogs()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  fetchLogs()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchLogs()
}

const getActionType = (action: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  const types: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    create: 'success',
    update: 'warning',
    delete: 'danger',
    login: 'info',
    logout: 'info'
  }
  return types[action] || 'info'
}

const getActionLabel = (action: string) => {
  const labels: Record<string, string> = {
    create: '创建',
    update: '更新',
    delete: '删除',
    login: '登录',
    logout: '登出'
  }
  return labels[action] || action
}

const formatDetail = (detail: any): string => {
  if (!detail) return '-'
  if (typeof detail === 'string') return detail
  try {
    return JSON.stringify(detail, null, 2)
  } catch {
    return String(detail)
  }
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped lang="scss">
.operation-log {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
}

.detail-text {
  cursor: pointer;
  color: #409eff;
}

.detail-text:hover {
  text-decoration: underline;
}
</style>

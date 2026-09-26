<template>
  <div class="user-plants">
    <el-page-header title="用户盆栽管理" @back="handleBack" />
    
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="用户ID">
          <el-input-number v-model="filters.user_id" :min="1" placeholder="请输入用户ID" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="健康" value="healthy" />
            <el-option label="生病" value="sick" />
            <el-option label="死亡" value="dead" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="table-card">
      <el-table :data="plants" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="植物名称" width="150" />
        <el-table-column prop="species" label="物种" width="150" />
        <el-table-column prop="variety" label="品种" width="120" />
        <el-table-column prop="location" label="位置" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="acquisition_date" label="获取日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.acquisition_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
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
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/modules/admin'
import type { Plant } from '@/types/models'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const plants = ref<Plant[]>([])

const filters = reactive({
  user_id: null as number | null,
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const handleBack = () => {
  router.back()
}

const fetchPlants = async () => {
  const userId = route.params.userId as string
  if (!userId) {
    ElMessage.warning('请提供用户ID')
    return
  }
  
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    
    if (filters.status) params.status = filters.status
    
    const res = await adminApi.getUserPlants(parseInt(userId), params)
    plants.value = res.items
    pagination.total = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取盆栽列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchPlants()
}

const handleReset = () => {
  filters.status = ''
  pagination.page = 1
  fetchPlants()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  fetchPlants()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchPlants()
}

const getStatusType = (status: string): 'success' | 'warning' | 'danger' | 'info' => {
  const types: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    healthy: 'success',
    sick: 'warning',
    dead: 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    healthy: '健康',
    sick: '生病',
    dead: '死亡'
  }
  return labels[status] || status
}

const formatDate = (date?: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (date?: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchPlants()
})
</script>

<style scoped lang="scss">
.user-plants {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
}
</style>

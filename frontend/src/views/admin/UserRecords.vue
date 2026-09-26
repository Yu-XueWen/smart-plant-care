<template>
  <div class="user-records">
    <el-page-header title="用户记录管理" @back="handleBack" />
    
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="用户ID">
          <el-input-number v-model="filters.user_id" :min="1" placeholder="请输入用户ID" />
        </el-form-item>
        <el-form-item label="记录类型">
          <el-select v-model="filters.record_type" placeholder="全部" clearable style="width: 150px">
            <el-option label="识别记录" value="identify" />
            <el-option label="诊断记录" value="diagnose" />
            <el-option label="浇水记录" value="watering" />
            <el-option label="养护记录" value="care" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="table-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="识别记录" name="identify">
          <el-table :data="identifyRecords" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="plant_name" label="植物名称" width="150" />
            <el-table-column prop="confidence" label="置信度" width="100">
              <template #default="{ row }">
                {{ (row.confidence * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="image_url" label="图片" width="100">
              <template #default="{ row }">
                <el-image 
                  v-if="row.image_url"
                  :src="row.image_url" 
                  :preview-src-list="[row.image_url]"
                  style="width: 50px; height: 50px"
                  fit="cover"
                />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-tab-pane>
        
        <el-tab-pane label="诊断记录" name="diagnose">
          <el-table :data="diagnoseRecords" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="disease_name" label="病害名称" width="150" />
            <el-table-column prop="confidence" label="置信度" width="100">
              <template #default="{ row }">
                {{ (row.confidence * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="image_url" label="图片" width="100">
              <template #default="{ row }">
                <el-image 
                  v-if="row.image_url"
                  :src="row.image_url" 
                  :preview-src-list="[row.image_url]"
                  style="width: 50px; height: 50px"
                  fit="cover"
                />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-tab-pane>
        
        <el-tab-pane label="浇水记录" name="watering">
          <el-empty description="浇水记录功能开发中..." />
        </el-tab-pane>
        
        <el-tab-pane label="养护记录" name="care">
          <el-empty description="养护记录功能开发中..." />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/modules/admin'

interface IdentifyRecord {
  id: number
  plant_name: string
  confidence: number
  image_url: string
  created_at: string
}

interface DiagnoseRecord {
  id: number
  disease_name: string
  confidence: number
  image_url: string
  created_at: string
}

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const activeTab = ref('identify')

const filters = reactive({
  user_id: null as number | null,
  record_type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const identifyRecords = ref<IdentifyRecord[]>([])
const diagnoseRecords = ref<DiagnoseRecord[]>([])

const handleBack = () => {
  router.back()
}

const fetchIdentifyRecords = async () => {
  const userId = route.params.userId as string
  if (!userId) {
    ElMessage.warning('请提供用户ID')
    return
  }
  
  loading.value = true
  try {
    const res = await adminApi.getUserHistory(parseInt(userId), 'identify', {
      page: pagination.page,
      page_size: pagination.pageSize
    })
    identifyRecords.value = res.items
    pagination.total = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取识别记录失败')
  } finally {
    loading.value = false
  }
}

const fetchDiagnoseRecords = async () => {
  const userId = route.params.userId as string
  if (!userId) {
    ElMessage.warning('请提供用户ID')
    return
  }
  
  loading.value = true
  try {
    const res = await adminApi.getUserHistory(parseInt(userId), 'diagnose', {
      page: pagination.page,
      page_size: pagination.pageSize
    })
    diagnoseRecords.value = res.items
    pagination.total = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取诊断记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  if (activeTab.value === 'identify') {
    fetchIdentifyRecords()
  } else if (activeTab.value === 'diagnose') {
    fetchDiagnoseRecords()
  }
}

const handleReset = () => {
  pagination.page = 1
  if (activeTab.value === 'identify') {
    fetchIdentifyRecords()
  } else if (activeTab.value === 'diagnose') {
    fetchDiagnoseRecords()
  }
}

const handlePageChange = (page: number) => {
  pagination.page = page
  if (activeTab.value === 'identify') {
    fetchIdentifyRecords()
  } else if (activeTab.value === 'diagnose') {
    fetchDiagnoseRecords()
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  if (activeTab.value === 'identify') {
    fetchIdentifyRecords()
  } else if (activeTab.value === 'diagnose') {
    fetchDiagnoseRecords()
  }
}

const formatDateTime = (date?: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  if (activeTab.value === 'identify') {
    fetchIdentifyRecords()
  } else if (activeTab.value === 'diagnose') {
    fetchDiagnoseRecords()
  }
})
</script>

<style scoped lang="scss">
.user-records {
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

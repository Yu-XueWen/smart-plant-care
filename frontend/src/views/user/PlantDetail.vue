<template>
  <div class="plant-detail" v-loading="loading">
    <!-- 返回按钮 -->
    <div class="back-bar">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回我的盆栽
      </el-button>
    </div>

    <div v-if="plant" class="detail-content">
      <!-- 照片展示区域 - 顶部 -->
      <el-card class="photos-card" v-if="plant.initial_photos && plant.initial_photos.length > 0">
        <template #header>
          <h3>盆栽照片</h3>
        </template>
        <el-row :gutter="16">
          <el-col 
            v-for="(photo, index) in plant.initial_photos" 
            :key="index"
            :xs="24" 
            :sm="12" 
            :md="8"
          >
            <el-image
              :src="photo"
              fit="cover"
              class="photo-item"
              :preview-src-list="plant.initial_photos"
              :initial-index="index"
            />
          </el-col>
        </el-row>
      </el-card>

      <!-- 物种信息卡片 - 来自知识图谱 -->
      <el-card class="species-info-card" v-if="kgInfo && kgInfo.has_kg_info" v-loading="kgLoading">
        <template #header>
          <div class="card-header">
            <h3>🌿 物种详细信息</h3>
            <el-tag type="success" size="small">来自知识图谱</el-tag>
          </div>
        </template>

        <!-- 左右分栏布局 -->
        <div class="species-layout">
          <!-- 左侧栏 -->
          <div class="left-column">
            <!-- 植物基本信息 -->
            <div class="species-section compact">
              <div class="plant-header-info">
                <h4 class="plant-title">{{ kgInfo.care_guide.plant_name }}</h4>
                <p class="scientific-name" v-if="kgInfo.care_guide.scientific_name">
                  <em>{{ kgInfo.care_guide.scientific_name }}</em>
                </p>
              </div>
              
              <!-- 难度和生长速度标签 -->
              <div class="info-tags">
                <el-tag :type="getDifficultyType(kgInfo.care_guide.difficulty_level)" size="small">
                  <el-icon><Star /></el-icon>
                  {{ getDifficultyText(kgInfo.care_guide.difficulty_level) }}
                </el-tag>
                <el-tag type="info" size="small">
                  <el-icon><TrendCharts /></el-icon>
                  {{ kgInfo.care_guide.growth_rate || '未知' }}
                </el-tag>
              </div>
            </div>

            <!-- 植物简介 -->
            <div class="species-section compact description-section">
              <h5 class="section-title"><el-icon><InfoFilled /></el-icon> 简介</h5>
              <p class="species-description">
                {{ kgInfo.care_guide.description || '暂无描述' }}
              </p>
            </div>

            <!-- 生长环境需求 -->
            <div class="species-section compact">
              <h5 class="section-title"><el-icon><Sunny /></el-icon> 生长环境</h5>
              <div class="env-list">
                <div class="env-item">
                  <span class="env-icon">☀️</span>
                  <div class="env-text">
                    <div class="env-label">光照</div>
                    <div class="env-value">{{ kgInfo.care_guide.light_requirement || '未知' }}</div>
                  </div>
                </div>
                <div class="env-item">
                  <span class="env-icon">🌡️</span>
                  <div class="env-text">
                    <div class="env-label">温度</div>
                    <div class="env-value">{{ kgInfo.care_guide.temperature_range || '未知' }}</div>
                  </div>
                </div>
                <div class="env-item">
                  <span class="env-icon">💧</span>
                  <div class="env-text">
                    <div class="env-label">湿度</div>
                    <div class="env-value">{{ kgInfo.care_guide.humidity_requirement || '未知' }}</div>
                  </div>
                </div>
                <div class="env-item">
                  <span class="env-icon">🪴</span>
                  <div class="env-text">
                    <div class="env-label">土壤</div>
                    <div class="env-value">{{ kgInfo.care_guide.soil_type || '未知' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧栏 -->
          <div class="right-column">
            <!-- 养护管理 -->
            <div class="species-section compact">
              <h5 class="section-title"><el-icon><Tools /></el-icon> 养护管理</h5>
              <div class="care-list-compact">
                <div class="care-item-compact">
                  <div class="care-header">
                    <span class="care-icon">💦</span>
                    <strong>浇水</strong>
                  </div>
                  <div class="care-content">{{ kgInfo.care_guide.watering_management || '未知' }}</div>
                </div>
                <div class="care-item-compact">
                  <div class="care-header">
                    <span class="care-icon">🧪</span>
                    <strong>施肥</strong>
                  </div>
                  <div class="care-content">{{ kgInfo.care_guide.fertilization_plan || '未知' }}</div>
                </div>
                <div class="care-item-compact">
                  <div class="care-header">
                    <span class="care-icon">✂️</span>
                    <strong>修剪</strong>
                  </div>
                  <div class="care-content">{{ kgInfo.care_guide.pruning_guide || '未知' }}</div>
                </div>
                <div class="care-item-compact">
                  <div class="care-header">
                    <span class="care-icon">🌱</span>
                    <strong>繁殖</strong>
                  </div>
                  <div class="care-content">
                    {{ Array.isArray(kgInfo.care_guide.propagation_methods) 
                       ? kgInfo.care_guide.propagation_methods.join('、') 
                       : (kgInfo.care_guide.propagation_methods || '未知') }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 常见病虫害 -->
            <div class="species-section compact" v-if="kgInfo.common_diseases.length > 0 || kgInfo.common_pests.length > 0">
              <h5 class="section-title"><el-icon><Warning /></el-icon> 病虫害</h5>
              <div class="pest-compact">
                <div v-if="kgInfo.common_diseases.length > 0" class="pest-group-compact">
                  <div class="pest-label">🦠 病害</div>
                  <div class="pest-tags-compact">
                    <el-tag 
                      v-for="(disease, idx) in kgInfo.common_diseases" 
                      :key="idx"
                      type="warning"
                      size="small"
                      effect="light"
                    >
                      {{ disease }}
                    </el-tag>
                  </div>
                </div>
                <div v-if="kgInfo.common_pests.length > 0" class="pest-group-compact">
                  <div class="pest-label">🐛 虫害</div>
                  <div class="pest-tags-compact">
                    <el-tag 
                      v-for="(pest, idx) in kgInfo.common_pests" 
                      :key="idx"
                      type="danger"
                      size="small"
                      effect="light"
                    >
                      {{ pest }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 相似植物推荐 -->
            <div class="species-section compact" v-if="kgInfo.similar_plants && kgInfo.similar_plants.length > 0">
              <h5 class="section-title"><el-icon><Connection /></el-icon> 相似植物</h5>
              <div class="similar-plants-compact">
                <div 
                  v-for="(similar, idx) in kgInfo.similar_plants" 
                  :key="idx"
                  class="similar-plant-item"
                >
                  <div class="similar-name">{{ similar.name }}</div>
                  <el-tag size="small" type="info">{{ similar.similarity_score }}</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 无知识图谱信息提示 -->
      <el-alert
        v-else-if="kgInfo && !kgInfo.has_kg_info"
        title="知识图谱中暂无该植物的详细物种信息"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 24px;"
      />

      <!-- 基本信息卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <h2>{{ plant.nickname || plant.plant_name }}</h2>
            <el-tag :type="plant.status === 1 ? 'success' : 'info'">
              {{ plant.status === 1 ? '正常' : '已移除' }}
            </el-tag>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="盆栽名">
            {{ plant.plant_name }}
          </el-descriptions-item>
          <el-descriptions-item label="物种名">
            {{ plant.species_id || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="昵称">
            {{ plant.nickname || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="种植日期">
            {{ formatDate(plant.planting_date) || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="来源">
            {{ plant.source || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(plant.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ plant.notes || '无' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button type="primary" @click="showEditDialog = true">
          <el-icon><Edit /></el-icon>
          编辑信息
        </el-button>
        <el-button type="danger" @click="handleDelete">
          <el-icon><Delete /></el-icon>
          删除盆栽
        </el-button>
      </div>

      <!-- 记录卡片 - 左右布局 -->
      <el-card class="records-combined-card">
        <template #header>
          <div class="card-header">
            <h3>📋 养护记录</h3>
          </div>
        </template>

        <div class="records-layout">
          <!-- 左侧：浇水记录 -->
          <div class="record-column">
            <div class="record-section">
              <div class="section-header">
                <h4>💧 浇水记录</h4>
                <div class="header-actions">
                  <el-tag type="info" size="small">{{ wateringRecords.length }} 条</el-tag>
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="showWateringDialog = true"
                  >
                    <el-icon><Plus /></el-icon>
                    添加
                  </el-button>
                </div>
              </div>

              <el-table 
                :data="wateringRecords" 
                style="width: 100%" 
                class="compact-table" 
                empty-text="暂无浇水记录"
                :max-height="300"
              >
                <el-table-column prop="date" label="日期" width="90">
                  <template #default="{ row }">
                    {{ formatDate(row.date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="amount" label="水量" width="70" />
                <el-table-column prop="notes" label="备注" show-overflow-tooltip />
              </el-table>
            </div>
          </div>

          <!-- 右侧：养护记录 -->
          <div class="record-column">
            <div class="record-section">
              <div class="section-header">
                <h4>🛠️ 养护记录</h4>
                <div class="header-actions">
                  <el-tag type="info" size="small">{{ treatmentRecords.length }} 条</el-tag>
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="showTreatmentDialog = true"
                  >
                    <el-icon><Plus /></el-icon>
                    添加
                  </el-button>
                </div>
              </div>

              <el-table 
                :data="treatmentRecords" 
                style="width: 100%" 
                class="compact-table" 
                empty-text="暂无养护记录"
                :max-height="300"
              >
                <el-table-column prop="date" label="日期" width="90">
                  <template #default="{ row }">
                    {{ formatDate(row.date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="type" label="类型" width="70">
                  <template #default="{ row }">
                    <el-tag size="small">{{ getTreatmentTypeText(row.type) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="product" label="产品" width="80" show-overflow-tooltip />
                <el-table-column prop="dosage" label="用量" width="60" />
                <el-table-column prop="notes" label="备注" show-overflow-tooltip />
              </el-table>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑盆栽信息" width="600px">
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="100px"
      >
        <el-form-item label="盆栽名">
          <el-input v-model="editForm.plant_name" />
        </el-form-item>
        <el-form-item label="物种名">
          <el-input v-model="editForm.species_id" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="editForm.nickname" />
        </el-form-item>
        <el-form-item label="种植日期">
          <el-date-picker
            v-model="editForm.planting_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="editForm.source" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="updateLoading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加浇水记录对话框 -->
    <el-dialog v-model="showWateringDialog" title="添加浇水记录" width="500px">
      <el-form
        ref="wateringFormRef"
        :model="wateringForm"
        :rules="wateringRules"
        label-width="100px"
      >
        <el-form-item label="浇水日期" prop="watering_date">
          <el-date-picker
            v-model="wateringForm.watering_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="浇水量">
          <el-input v-model="wateringForm.water_amount" placeholder="例如：200ml" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="wateringForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showWateringDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddWatering" :loading="wateringLoading">
          添加
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加养护记录对话框 -->
    <el-dialog v-model="showTreatmentDialog" title="添加养护记录" width="500px">
      <el-form
        ref="treatmentFormRef"
        :model="treatmentForm"
        :rules="treatmentRules"
        label-width="100px"
      >
        <el-form-item label="养护类型" prop="treatment_type">
          <el-select v-model="treatmentForm.treatment_type" placeholder="请选择" style="width: 100%">
            <el-option label="施肥" value="fertilize" />
            <el-option label="施药" value="pesticide" />
            <el-option label="修剪" value="prune" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input v-model="treatmentForm.product_name" placeholder="肥料或药品名称" />
        </el-form-item>
        <el-form-item label="用量">
          <el-input v-model="treatmentForm.dosage" placeholder="例如：10g" />
        </el-form-item>
        <el-form-item label="操作日期" prop="application_date">
          <el-date-picker
            v-model="treatmentForm.application_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="treatmentForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTreatmentDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddTreatment" :loading="treatmentLoading">
          添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, Edit, Delete, Plus, Star, TrendCharts, InfoFilled, Sunny, Tools, Warning, Connection } from '@element-plus/icons-vue'
import { plantApi } from '@/api/modules/plant'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const updateLoading = ref(false)
const wateringLoading = ref(false)
const treatmentLoading = ref(false)
const kgLoading = ref(false)

const plant = ref<any>(null)
const wateringRecords = ref<any[]>([])
const treatmentRecords = ref<any[]>([])
const kgInfo = ref<any>(null)

// 编辑表单
const showEditDialog = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive({
  plant_name: '',
  species_id: '',
  nickname: '',
  planting_date: '',
  source: '',
  notes: ''
})

// 浇水记录表单
const showWateringDialog = ref(false)
const wateringFormRef = ref<FormInstance>()
const wateringForm = reactive({
  watering_date: new Date().toISOString().split('T')[0],
  water_amount: '',
  notes: ''
})
const wateringRules: FormRules = {
  watering_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

// 养护记录表单
const showTreatmentDialog = ref(false)
const treatmentFormRef = ref<FormInstance>()
const treatmentForm = reactive({
  treatment_type: '',
  product_name: '',
  dosage: '',
  application_date: new Date().toISOString().split('T')[0],
  notes: ''
})
const treatmentRules: FormRules = {
  treatment_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  application_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

// 折叠状态控制（已移除，改为始终显示）

// 获取盆栽详情
async function fetchPlantDetail() {
  const plantId = Number(route.params.id)
  if (!plantId) {
    ElMessage.error('无效的盆栽ID')
    goBack()
    return
  }

  loading.value = true
  kgLoading.value = true
  try {
    const res = await plantApi.getPlantDetail(plantId)
    plant.value = res
    wateringRecords.value = res.watering_records || []
    treatmentRecords.value = res.treatment_records || []
    
    // 初始化编辑表单
    editForm.plant_name = res.plant_name
    editForm.species_id = res.species_id || ''
    editForm.nickname = res.nickname || ''
    editForm.planting_date = res.planting_date || ''
    editForm.source = res.source || ''
    editForm.notes = res.notes || ''

    // 获取知识图谱信息
    try {
      const kgRes = await plantApi.getPlantKGInfo(plantId)
      kgInfo.value = kgRes
    } catch (kgError) {
      console.warn('获取知识图谱信息失败:', kgError)
      kgInfo.value = null
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取详情失败')
  } finally {
    loading.value = false
    kgLoading.value = false
  }
}

// 返回
function goBack() {
  router.push('/my-plants')
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 格式化日期时间
function formatDateTime(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 获取养护类型文本
function getTreatmentTypeText(type: string) {
  const map: Record<string, string> = {
    fertilize: '施肥',
    pesticide: '施药',
    prune: '修剪',
    other: '其他'
  }
  return map[type] || type
}

// 获取难度等级文本
function getDifficultyText(level: string) {
  const map: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[level] || level || '未知'
}

// 获取难度等级标签类型
function getDifficultyType(level: string) {
  const map: Record<string, any> = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return map[level] || 'info'
}

// 更新盆栽信息
async function handleUpdate() {
  const plantId = Number(route.params.id)
  updateLoading.value = true
  try {
    await plantApi.updatePlant(plantId, editForm)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    fetchPlantDetail()
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    updateLoading.value = false
  }
}

// 删除盆栽
async function handleDelete() {
  const plantId = Number(route.params.id)
  try {
    await ElMessageBox.confirm('确定要删除这个盆栽吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await plantApi.deletePlant(plantId)
    ElMessage.success('删除成功')
    goBack()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 添加浇水记录
async function handleAddWatering() {
  if (!wateringFormRef.value) return
  
  await wateringFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    const plantId = Number(route.params.id)
    wateringLoading.value = true
    try {
      await plantApi.addWatering(plantId, wateringForm)
      ElMessage.success('添加成功')
      showWateringDialog.value = false
      fetchPlantDetail()
      // 重置表单
      wateringForm.water_amount = ''
      wateringForm.notes = ''
    } catch (error: any) {
      ElMessage.error(error.message || '添加失败')
    } finally {
      wateringLoading.value = false
    }
  })
}

// 添加养护记录
async function handleAddTreatment() {
  if (!treatmentFormRef.value) return
  
  await treatmentFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    const plantId = Number(route.params.id)
    treatmentLoading.value = true
    try {
      await plantApi.addTreatment(plantId, treatmentForm)
      ElMessage.success('添加成功')
      showTreatmentDialog.value = false
      fetchPlantDetail()
      // 重置表单
      treatmentForm.product_name = ''
      treatmentForm.dosage = ''
      treatmentForm.notes = ''
    } catch (error: any) {
      ElMessage.error(error.message || '添加失败')
    } finally {
      treatmentLoading.value = false
    }
  })
}

onMounted(() => {
  fetchPlantDetail()
})
</script>

<style scoped lang="scss">
.plant-detail {
  .back-bar {
    margin-bottom: 20px;
  }

  .detail-content {
    max-width: 1200px;
    margin: 0 auto;
  }

  .info-card,
  .photos-card,
  .species-info-card,
  .records-card {
    margin-bottom: 24px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2, h3 {
      margin: 0;
      font-size: 20px;
      color: #303133;
    }

    h3 {
      font-size: 18px;
    }
  }

  .photo-item {
    width: 100%;
    height: 200px;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.3s;

    &:hover {
      transform: scale(1.05);
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
  }

  :deep(.el-descriptions__label) {
    font-weight: 600;
  }

  // 物种信息卡片样式
  .species-info-card {
    .card-header {
      h3 {
        font-size: 18px;
        margin: 0;
      }
    }

    // 左右分栏布局
    .species-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;

      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
    }

    .left-column,
    .right-column {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .species-section {
      &.compact {
        margin-bottom: 0;
      }
    }

    .section-title {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 10px 0;
      display: flex;
      align-items: center;
      gap: 6px;

      .el-icon {
        font-size: 16px;
        color: #409eff;
      }
    }

    // 植物标题区域
    .plant-header-info {
      margin-bottom: 8px;

      .plant-title {
        font-size: 20px;
        font-weight: bold;
        color: #303133;
        margin: 0 0 2px 0;
      }

      .scientific-name {
        font-size: 13px;
        color: #909399;
        margin: 0;
      }
    }

    // 信息标签
    .info-tags {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 8px;

      .el-tag {
        display: flex;
        align-items: center;
        gap: 3px;
        padding: 4px 8px;
        font-size: 12px;

        .el-icon {
          font-size: 12px;
        }
      }
    }

    // 简介区域
    .description-section {
      .species-description {
        font-size: 13px;
        line-height: 1.6;
        color: #606266;
        text-align: justify;
        padding: 10px;
        background: linear-gradient(135deg, #f5f7fa 0%, #fafbfc 100%);
        border-radius: 6px;
        margin: 0;
        border-left: 3px solid #409eff;
      }
    }

    // 环境列表
    .env-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .env-item {
      display: flex;
      align-items: center;
      padding: 8px 10px;
      background: #fafbfc;
      border-radius: 6px;
      border: 1px solid #e4e7ed;
      transition: all 0.2s;

      &:hover {
        background: #f5f7fa;
        border-color: #409eff;
      }

      .env-icon {
        font-size: 20px;
        margin-right: 10px;
        flex-shrink: 0;
      }

      .env-text {
        flex: 1;
        min-width: 0;

        .env-label {
          font-size: 11px;
          color: #909399;
          margin-bottom: 2px;
        }

        .env-value {
          font-size: 13px;
          font-weight: 500;
          color: #303133;
          word-break: break-word;
        }
      }
    }

    // 养护项目列表（紧凑版）
    .care-list-compact {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .care-item-compact {
      padding: 10px;
      background: #fafbfc;
      border-radius: 6px;
      border: 1px solid #e4e7ed;
      transition: all 0.2s;

      &:hover {
        background: #f5f7fa;
        border-color: #409eff;
      }

      .care-header {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
        font-size: 13px;
        color: #303133;

        .care-icon {
          font-size: 16px;
        }

        strong {
          font-weight: 600;
        }
      }

      .care-content {
        font-size: 12px;
        line-height: 1.5;
        color: #606266;
        padding-left: 22px;
      }
    }

    // 病虫害区域（紧凑版）
    .pest-compact {
      .pest-group-compact {
        margin-bottom: 10px;

        &:last-child {
          margin-bottom: 0;
        }

        .pest-label {
          font-size: 12px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 6px;
        }

        .pest-tags-compact {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;

          .el-tag {
            font-size: 11px;
            padding: 3px 8px;
          }
        }
      }
    }

    // 相似植物（紧凑版）
    .similar-plants-compact {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .similar-plant-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 10px;
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      border-radius: 6px;
      border: 1px solid #bae6fd;
      transition: all 0.2s;

      &:hover {
        transform: translateX(2px);
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
      }

      .similar-name {
        font-size: 13px;
        font-weight: 500;
        color: #303133;
      }

      .el-tag {
        font-size: 11px;
      }
    }
  }

  // 记录卡片样式（左右布局）
  .records-combined-card {
    .card-header {
      h3 {
        font-size: 18px;
        margin: 0;
      }
    }

    .records-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;

      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
    }

    .record-column {
      min-width: 0;
    }

    .record-section {
      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e4e7ed;

        h4 {
          font-size: 15px;
          font-weight: 600;
          color: #303133;
          margin: 0;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 8px;

          .el-button {
            padding: 5px 10px;
            font-size: 12px;

            .el-icon {
              font-size: 12px;
            }
          }
        }
      }
    }

    // 紧凑表格样式
    .compact-table {
      font-size: 12px;

      :deep(.el-table__header) {
        th {
          padding: 8px 0;
          font-size: 12px;
          font-weight: 600;
          background-color: #f5f7fa;
          color: #606266;
        }
      }

      :deep(.el-table__body) {
        td {
          padding: 8px 0;
          font-size: 12px;
          color: #606266;
        }

        tr:hover > td {
          background-color: #f5f7fa;
        }
      }

      :deep(.el-table__empty-text) {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}
</style>

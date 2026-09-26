<template>
  <div class="knowledge-manage">
    <el-tabs v-model="activeTab">
      <!-- 植物知识 -->
      <el-tab-pane label="植物知识" name="plants">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>植物知识库</span>
              <el-button type="primary" @click="handleCreatePlant">
                <el-icon><Plus /></el-icon>
                新建植物
              </el-button>
            </div>
          </template>

          <el-form :inline="true" :model="plantSearch" class="search-form">
            <el-form-item label="搜索">
              <el-input v-model="plantSearch.search" placeholder="输入植物名称" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchPlants">搜索</el-button>
              <el-button @click="resetPlantSearch">重置</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="plants" v-loading="plantLoading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" width="150" />
            <el-table-column prop="scientific_name" label="学名" width="200" />
            <el-table-column prop="family" label="科属" width="150" />
            <el-table-column prop="care_level" label="养护难度" width="100">
              <template #default="{ row }">
                <el-tag :type="careLevelType(row.care_level)">
                  {{ careLevelText(row.care_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="handleEditPlant(row as KnowledgePlant)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeletePlant(row as KnowledgePlant)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="plantPagination.page"
            v-model:page-size="plantPagination.pageSize"
            :total="plantPagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @change="fetchPlants"
            class="pagination"
          />
        </el-card>
      </el-tab-pane>

      <!-- 病害知识 -->
      <el-tab-pane label="病害知识" name="diseases">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>病害知识库</span>
              <el-button type="primary" @click="handleCreateDisease">
                <el-icon><Plus /></el-icon>
                新建病害
              </el-button>
            </div>
          </template>

          <el-form :inline="true" :model="diseaseSearch" class="search-form">
            <el-form-item label="搜索">
              <el-input v-model="diseaseSearch.search" placeholder="输入病害名称" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchDiseases">搜索</el-button>
              <el-button @click="resetDiseaseSearch">重置</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="diseases" v-loading="diseaseLoading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" width="150" />
            <el-table-column prop="scientific_name" label="学名" width="200" />
            <el-table-column prop="pathogen" label="病原" width="150" />
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag :type="severityType(row.severity)">
                  {{ severityText(row.severity) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="symptoms" label="症状" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="handleEditDisease(row as KnowledgeDisease)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteDisease(row as KnowledgeDisease)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="diseasePagination.page"
            v-model:page-size="diseasePagination.pageSize"
            :total="diseasePagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @change="fetchDiseases"
            class="pagination"
          />
        </el-card>
      </el-tab-pane>

      <!-- 养护技巧 -->
      <el-tab-pane label="养护技巧" name="tips">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>养护技巧库</span>
              <el-button type="primary" @click="handleCreateTip">
                <el-icon><Plus /></el-icon>
                新建技巧
              </el-button>
            </div>
          </template>

          <el-table :data="tips" v-loading="tipLoading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" width="200" />
            <el-table-column prop="category" label="分类" width="120">
              <template #default="{ row }">
                <el-tag>{{ row.category || '通用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="handleEditTip(row as KnowledgeTip)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteTip(row as KnowledgeTip)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="tipPagination.page"
            v-model:page-size="tipPagination.pageSize"
            :total="tipPagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @change="fetchTips"
            class="pagination"
          />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 植物编辑对话框 -->
    <el-dialog v-model="plantDialogVisible" :title="plantDialogTitle" width="700px" destroy-on-close>
      <el-form ref="plantFormRef" :model="plantForm" :rules="plantRules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="植物名称" prop="name">
              <el-input v-model="plantForm.name" placeholder="请输入植物名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学名">
              <el-input v-model="plantForm.scientific_name" placeholder="请输入学名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="科属">
              <el-input v-model="plantForm.family" placeholder="请输入科属" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="养护难度">
              <el-select v-model="plantForm.care_level" placeholder="请选择">
                <el-option label="简单" value="easy" />
                <el-option label="中等" value="medium" />
                <el-option label="困难" value="hard" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="光照需求">
              <el-input v-model="plantForm.light_requirement" placeholder="如：散射光" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="浇水需求">
              <el-input v-model="plantForm.water_requirement" placeholder="如：保持湿润" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="温度范围">
              <el-input v-model="plantForm.temperature_range" placeholder="如：18-28°C" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="湿度范围">
              <el-input v-model="plantForm.humidity_range" placeholder="如：60-80%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="plantForm.description" type="textarea" :rows="3" placeholder="请输入植物描述" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="plantForm.image_url" placeholder="请输入图片URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="plantDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitPlant" :loading="plantSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 病害编辑对话框 -->
    <el-dialog v-model="diseaseDialogVisible" :title="diseaseDialogTitle" width="700px" destroy-on-close>
      <el-form ref="diseaseFormRef" :model="diseaseForm" :rules="diseaseRules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="病害名称" prop="name">
              <el-input v-model="diseaseForm.name" placeholder="请输入病害名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学名">
              <el-input v-model="diseaseForm.scientific_name" placeholder="请输入学名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="病原">
              <el-input v-model="diseaseForm.pathogen" placeholder="如：真菌感染" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="严重程度">
              <el-select v-model="diseaseForm.severity" placeholder="请选择">
                <el-option label="轻度" value="mild" />
                <el-option label="中度" value="moderate" />
                <el-option label="严重" value="severe" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="症状">
          <el-input v-model="diseaseForm.symptoms" type="textarea" :rows="2" placeholder="请输入症状描述" />
        </el-form-item>
        <el-form-item label="治疗方法">
          <el-input v-model="diseaseForm.treatment" type="textarea" :rows="2" placeholder="请输入治疗方法" />
        </el-form-item>
        <el-form-item label="预防措施">
          <el-input v-model="diseaseForm.prevention" type="textarea" :rows="2" placeholder="请输入预防措施" />
        </el-form-item>
        <el-form-item label="影响植物">
          <el-input v-model="diseaseForm.affected_plants" type="textarea" :rows="2" placeholder="多个植物用逗号分隔" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="diseaseForm.image_url" placeholder="请输入图片URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="diseaseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitDisease" :loading="diseaseSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 养护技巧编辑对话框 -->
    <el-dialog v-model="tipDialogVisible" :title="tipDialogTitle" width="600px" destroy-on-close>
      <el-form ref="tipFormRef" :model="tipForm" :rules="tipRules" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="tipForm.title" placeholder="请输入技巧标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="tipForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="浇水" value="watering" />
            <el-option label="施肥" value="fertilizing" />
            <el-option label="修剪" value="pruning" />
            <el-option label="换盆" value="repotting" />
            <el-option label="病虫害防治" value="pest_control" />
            <el-option label="通用" value="general" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="tipForm.content" type="textarea" :rows="5" placeholder="请输入技巧内容" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="tipForm.image_url" placeholder="请输入图片URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitTip" :loading="tipSubmitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { adminApi } from '@/api/modules/admin'
import type { KnowledgePlant, KnowledgeDisease, KnowledgeTip } from '@/types/models'

const activeTab = ref('plants')

// 植物知识
const plantLoading = ref(false)
const plants = ref<KnowledgePlant[]>([])
const plantSearch = ref({ search: '' })
const plantPagination = ref({ page: 1, pageSize: 20, total: 0 })
const plantDialogVisible = ref(false)
const plantDialogTitle = computed(() => plantForm.value.id ? '编辑植物' : '新建植物')
const plantFormRef = ref()
const plantSubmitting = ref(false)
const plantForm = ref<Partial<KnowledgePlant>>({
  care_level: 'easy'
})
const plantRules = {
  name: [{ required: true, message: '请输入植物名称', trigger: 'blur' }]
}

const fetchPlants = async () => {
  plantLoading.value = true
  try {
    const res = await adminApi.getPlantKnowledge({
      page: plantPagination.value.page,
      page_size: plantPagination.value.pageSize,
      search: plantSearch.value.search
    })
    plants.value = res.items
    plantPagination.value.total = res.total
  } catch (error) {
    ElMessage.error('获取植物列表失败')
  } finally {
    plantLoading.value = false
  }
}

const handleCreatePlant = () => {
  plantForm.value = { care_level: 'easy' }
  plantDialogVisible.value = true
}

const handleEditPlant = (row: KnowledgePlant) => {
  plantForm.value = { ...row }
  plantDialogVisible.value = true
}

const handleDeletePlant = async (row: KnowledgePlant) => {
  try {
    await ElMessageBox.confirm(`确定要删除植物"${row.name}"吗？`, '提示', { type: 'warning' })
    await adminApi.deletePlantKnowledge(row.id)
    ElMessage.success('删除成功')
    fetchPlants()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmitPlant = async () => {
  try {
    await plantFormRef.value.validate()
    plantSubmitting.value = true
    if (plantForm.value.id) {
      await adminApi.updatePlantKnowledge(plantForm.value.id, plantForm.value)
      ElMessage.success('更新成功')
    } else {
      await adminApi.createPlantKnowledge(plantForm.value)
      ElMessage.success('创建成功')
    }
    plantDialogVisible.value = false
    fetchPlants()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    plantSubmitting.value = false
  }
}

const resetPlantSearch = () => {
  plantSearch.value = { search: '' }
  plantPagination.value.page = 1
  fetchPlants()
}

const careLevelType = (level?: string) => {
  const map: Record<string, 'success' | 'warning' | 'danger'> = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[level || ''] || 'info'
}

const careLevelText = (level?: string) => {
  const map: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
  return map[level || ''] || '未知'
}

// 病害知识
const diseaseLoading = ref(false)
const diseases = ref<KnowledgeDisease[]>([])
const diseaseSearch = ref({ search: '' })
const diseasePagination = ref({ page: 1, pageSize: 20, total: 0 })
const diseaseDialogVisible = ref(false)
const diseaseDialogTitle = computed(() => diseaseForm.value.id ? '编辑病害' : '新建病害')
const diseaseFormRef = ref()
const diseaseSubmitting = ref(false)
const diseaseForm = ref<Partial<KnowledgeDisease>>({
  severity: 'moderate'
})
const diseaseRules = {
  name: [{ required: true, message: '请输入病害名称', trigger: 'blur' }]
}

const fetchDiseases = async () => {
  diseaseLoading.value = true
  try {
    const res = await adminApi.getDiseaseKnowledge({
      page: diseasePagination.value.page,
      page_size: diseasePagination.value.pageSize,
      search: diseaseSearch.value.search
    })
    diseases.value = res.items
    diseasePagination.value.total = res.total
  } catch (error) {
    ElMessage.error('获取病害列表失败')
  } finally {
    diseaseLoading.value = false
  }
}

const handleCreateDisease = () => {
  diseaseForm.value = { severity: 'moderate' }
  diseaseDialogVisible.value = true
}

const handleEditDisease = (row: KnowledgeDisease) => {
  diseaseForm.value = { ...row }
  diseaseDialogVisible.value = true
}

const handleDeleteDisease = async (row: KnowledgeDisease) => {
  try {
    await ElMessageBox.confirm(`确定要删除病害"${row.name}"吗？`, '提示', { type: 'warning' })
    await adminApi.deleteDiseaseKnowledge(row.id)
    ElMessage.success('删除成功')
    fetchDiseases()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmitDisease = async () => {
  try {
    await diseaseFormRef.value.validate()
    diseaseSubmitting.value = true
    if (diseaseForm.value.id) {
      await adminApi.updateDiseaseKnowledge(diseaseForm.value.id, diseaseForm.value)
      ElMessage.success('更新成功')
    } else {
      await adminApi.createDiseaseKnowledge(diseaseForm.value)
      ElMessage.success('创建成功')
    }
    diseaseDialogVisible.value = false
    fetchDiseases()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    diseaseSubmitting.value = false
  }
}

const resetDiseaseSearch = () => {
  diseaseSearch.value = { search: '' }
  diseasePagination.value.page = 1
  fetchDiseases()
}

const severityType = (severity?: string) => {
  const map: Record<string, 'success' | 'warning' | 'danger'> = { mild: 'success', moderate: 'warning', severe: 'danger' }
  return map[severity || ''] || 'info'
}

const severityText = (severity?: string) => {
  const map: Record<string, string> = { mild: '轻度', moderate: '中度', severe: '严重' }
  return map[severity || ''] || '未知'
}

// 养护技巧
const tipLoading = ref(false)
const tips = ref<KnowledgeTip[]>([])
const tipPagination = ref({ page: 1, pageSize: 20, total: 0 })
const tipDialogVisible = ref(false)
const tipDialogTitle = computed(() => tipForm.value.id ? '编辑技巧' : '新建技巧')
const tipFormRef = ref()
const tipSubmitting = ref(false)
const tipForm = ref<Partial<KnowledgeTip>>({})
const tipRules = {
  title: [{ required: true, message: '请输入技巧标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入技巧内容', trigger: 'blur' }]
}

const fetchTips = async () => {
  tipLoading.value = true
  try {
    const res = await adminApi.getCareTips({
      page: tipPagination.value.page,
      page_size: tipPagination.value.pageSize
    })
    tips.value = res.items
    tipPagination.value.total = res.total
  } catch (error) {
    ElMessage.error('获取养护技巧列表失败')
  } finally {
    tipLoading.value = false
  }
}

const handleCreateTip = () => {
  tipForm.value = {}
  tipDialogVisible.value = true
}

const handleEditTip = (row: KnowledgeTip) => {
  tipForm.value = { ...row }
  tipDialogVisible.value = true
}

const handleDeleteTip = async (row: KnowledgeTip) => {
  try {
    await ElMessageBox.confirm(`确定要删除技巧"${row.title}"吗？`, '提示', { type: 'warning' })
    await adminApi.deleteCareTip(row.id)
    ElMessage.success('删除成功')
    fetchTips()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmitTip = async () => {
  try {
    await tipFormRef.value.validate()
    tipSubmitting.value = true
    if (tipForm.value.id) {
      await adminApi.updateCareTip(tipForm.value.id, tipForm.value)
      ElMessage.success('更新成功')
    } else {
      await adminApi.createCareTip(tipForm.value)
      ElMessage.success('创建成功')
    }
    tipDialogVisible.value = false
    fetchTips()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    tipSubmitting.value = false
  }
}

onMounted(() => {
  fetchPlants()
  fetchDiseases()
  fetchTips()
})
</script>

<style scoped lang="scss">
.knowledge-manage {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
}
</style>

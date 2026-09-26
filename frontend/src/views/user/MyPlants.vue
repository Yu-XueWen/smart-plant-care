<template>
  <div class="my-plants">
    <div class="page-header">
      <h2>我的盆栽</h2>
      <div class="header-actions">
        <el-button type="success" @click="handleBatchWater" :loading="batchWaterLoading">
          💧 一键浇水
        </el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加盆栽
        </el-button>
      </div>
    </div>

    <!-- 盆栽列表 -->
    <el-row :gutter="20" v-loading="loading">
      <el-col 
        v-for="plant in plants" 
        :key="plant.id" 
        :xs="24" 
        :sm="12" 
        :md="8" 
        :xl="6"
      >
        <el-card class="plant-card" shadow="hover">
          <!-- 水滴按钮 -->
          <div class="water-button" @click.stop="handleQuickWater(plant)">
            <el-tooltip content="快速浇水" placement="top">
              <span style="font-size: 20px;">💧</span>
            </el-tooltip>
          </div>
          
          <div class="plant-image" @click="goToDetail(plant.id)">
            <el-image 
              v-if="plant.initial_photos && plant.initial_photos.length > 0" 
              :src="getImageUrl(plant.initial_photos[0])" 
              fit="cover"
              lazy
              @error="(e) => console.error('图片加载失败:', getImageUrl(plant.initial_photos[0]), e)"
              @load="() => console.log('图片加载成功:', getImageUrl(plant.initial_photos[0]))"
            >
              <template #placeholder>
                <div class="image-placeholder">
                  <el-icon class="is-loading" :size="32"><Loading /></el-icon>
                </div>
              </template>
              <template #error>
                <div class="image-placeholder">
                  <el-icon :size="48"><Picture /></el-icon>
                  <span style="font-size: 12px; margin-top: 8px;">加载失败</span>
                </div>
              </template>
            </el-image>
            <div v-else class="image-placeholder">
              <el-icon :size="48"><Picture /></el-icon>
            </div>
          </div>
          
          <div class="plant-info">
            <h3>{{ plant.nickname || plant.plant_name }}</h3>
            <p class="species">{{ plant.plant_name }}</p>
            <div class="plant-meta">
              <el-tag 
                :type="plant.status === 1 ? 'success' : 'info'" 
                size="small"
              >
                {{ plant.status === 1 ? '正常' : '已移除' }}
              </el-tag>
              <span class="date" v-if="plant.planting_date">
                种植于 {{ formatDate(plant.planting_date) }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <el-empty 
      v-if="!loading && plants.length === 0" 
      description="还没有盆栽，快去添加吧！"
    >
      <el-button type="primary" @click="showAddDialog = true">添加盆栽</el-button>
    </el-empty>

    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 36, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 添加盆栽对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加盆栽"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="盆栽名" prop="plant_name">
          <el-input 
            v-model="form.plant_name" 
            placeholder="请输入植物名称（如：玫瑰、吊兰）"
            @blur="handlePlantNameBlur"
          >
            <template #append>
              <el-button @click="handleSearchKG" :loading="kgLoading">查询</el-button>
            </template>
          </el-input>
          <div class="form-tip" v-if="kgInfoLoaded">
            <el-icon color="#67c23a"><SuccessFilled /></el-icon>
            已从知识图谱获取物种信息
          </div>
        </el-form-item>

        <el-form-item label="物种名" prop="species_id">
          <el-input 
            v-model="form.species_id" 
            placeholder="从知识图谱自动填充"
            disabled
          />
          <div class="form-tip" style="color: #909399;">
            物种名将自动从知识图谱中获取
          </div>
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="给盆栽起个昵称（可选）" />
        </el-form-item>

        <el-form-item label="种植日期" prop="planting_date">
          <el-date-picker
            v-model="form.planting_date"
            type="date"
            placeholder="选择种植日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="来源" prop="source">
          <el-input v-model="form.source" placeholder="例如：花店购买、朋友赠送等（可选）" />
        </el-form-item>

        <el-form-item label="初始照片">
          <el-upload
            class="image-uploader"
            :auto-upload="false"
            :on-change="handleImageChange"
            :file-list="fileList"
            list-type="picture-card"
            :limit="5"
            accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">最多上传5张照片，单张不超过5MB</div>
        </el-form-item>

        <el-form-item label="当前状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">已移除</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="添加一些备注信息（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadFile } from 'element-plus'
import { Plus, Picture, SuccessFilled, Loading } from '@element-plus/icons-vue'
import { plantApi, type PlantCreateData } from '@/api/modules/plant'

const router = useRouter()

const plants = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12) // 每页显示12个卡片
const showAddDialog = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const fileList = ref<UploadFile[]>([])
const imageFiles = ref<File[]>([])
const kgLoading = ref(false)
const kgInfoLoaded = ref(false)
const batchWaterLoading = ref(false)

const form = reactive<PlantCreateData>({
  plant_name: '',
  species_id: '',
  nickname: '',
  planting_date: '',
  source: '',
  initial_photos: [],
  status: 1,
  notes: ''
})

const rules: FormRules = {
  plant_name: [
    { required: true, message: '请输入盆栽名', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

// 获取盆栽列表
async function fetchPlants() {
  loading.value = true
  try {
    const res = await plantApi.getMyPlants({
      page: currentPage.value,
      page_size: pageSize.value,
      status: 1
    })
    plants.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('获取盆栽列表失败:', error)
    ElMessage.error('获取盆栽列表失败')
  } finally {
    loading.value = false
  }
}

// 跳转到详情
function goToDetail(id: number) {
  router.push(`/plants/${id}`)
}

// 快速浇水单个盆栽
async function handleQuickWater(plant: any) {
  try {
    await ElMessageBox.confirm(
      `确认给「${plant.nickname || plant.plant_name}」浇水吗？`,
      '快速浇水',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    console.log('开始浇水，植物ID:', plant.id)
    const res = await plantApi.quickWaterPlant(plant.id)
    console.log('浇水响应:', res)
    
    ElMessage.success({
      message: '浇水成功！浇水记录已保存',
      duration: 3000
    })
    
    // 刷新列表以更新数据
    await fetchPlants()
    
    // 询问是否查看详情
    try {
      await ElMessageBox.confirm(
        '是否查看该盆栽的详细信息和浇水记录？',
        '提示',
        {
          confirmButtonText: '查看详情',
          cancelButtonText: '留在当前页',
          type: 'success'
        }
      )
      // 跳转到详情页
      goToDetail(plant.id)
    } catch (error) {
      // 用户选择留在当前页，不做任何操作
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('浇水失败:', error)
      ElMessage.error(error.message || '浇水失败')
    }
  }
}

// 一键浇水所有盆栽
async function handleBatchWater() {
  if (plants.value.length === 0) {
    ElMessage.warning('暂无盆栽')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认为所有 ${plants.value.length} 盆盆栽浇水吗？`,
      '一键浇水',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    batchWaterLoading.value = true
    const res = await plantApi.batchQuickWaterAll()
    
    ElMessage.success((res as any).message || '浇水完成')
    
    // 显示详细结果
    if (res.details && res.details.length > 0) {
      const successCount = res.details.filter((d: any) => d.status === 'success').length
      const partialCount = res.details.filter((d: any) => d.status === 'partial_success').length
      const failedCount = res.details.filter((d: any) => d.status === 'failed').length
      
      if (partialCount > 0 || failedCount > 0) {
        let message = `成功: ${successCount}盆`
        if (partialCount > 0) message += `，部分成功: ${partialCount}盆`
        if (failedCount > 0) message += `，失败: ${failedCount}盆`
        ElMessage.warning(message)
      }
    }
    
    // 刷新列表
    await fetchPlants()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('一键浇水失败:', error)
      ElMessage.error(error.message || '操作失败')
    }
  } finally {
    batchWaterLoading.value = false
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 获取图片URL - 统一转为相对路径，通过 Vite 代理访问后端
function getImageUrl(url: string): string {
  if (!url) return ''
  
  // 如果是Blob URL，返回空
  if (url.startsWith('blob:')) {
    console.warn('无效的Blob URL:', url)
    return ''
  }
  
  // 如果是完整URL（http://...），提取路径部分
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const parsed = new URL(url)
      return parsed.pathname
    } catch {
      return url
    }
  }
  
  // 如果已经是 /uploads 开头的相对路径，直接返回
  if (url.startsWith('/uploads')) {
    return url
  }
  
  // 如果是 uploads 开头（无斜杠），加上前导斜杠
  if (url.startsWith('uploads')) {
    return `/${url}`
  }
  
  // 如果是 /plants 或 plants/ 开头，补上 /uploads 前缀
  if (url.startsWith('/plants') || url.startsWith('plants/')) {
    const normalized = url.startsWith('/') ? url : `/${url}`
    return `/uploads${normalized}`
  }
  
  // 其他情况，尝试作为 /uploads 下的路径
  return `/uploads/${url.startsWith('/') ? url.substring(1) : url}`
}

// 处理图片选择
function handleImageChange(_file: UploadFile, files: UploadFile[]) {
  fileList.value = files
  imageFiles.value = files.map(f => f.raw!).filter(Boolean)
}

// 上传图片
async function uploadImages(): Promise<string[]> {
  const urls: string[] = []
  for (const file of imageFiles.value) {
    try {
      console.log('开始上传图片:', file.name, '大小:', file.size, '类型:', file.type)
      
      // 手动构建 FormData 并发送请求，以便更好地调试
      const formData = new FormData()
      formData.append('file', file)
      
      console.log('FormData 内容:')
      for (const [key, value] of formData.entries()) {
        console.log(`  ${key}:`, value instanceof File ? `${value.name} (${value.size} bytes)` : value)
      }
      
      const res = await plantApi.uploadPlantImage(file)
      console.log('上传成功，URL:', res.url)
      
      // 确保返回的是有效的URL（不是Blob URL）
      if (res.url && !res.url.startsWith('blob:')) {
        urls.push(res.url)
      } else {
        console.error('无效的URL:', res.url)
        ElMessage.error(`图片 ${file.name} 返回无效URL`)
      }
    } catch (error: any) {
      console.error('上传图片失败:', error)
      console.error('错误详情:', JSON.stringify(error.response?.data, null, 2))
      console.error('HTTP状态码:', error.response?.status)
      console.error('完整响应:', error.response)
      ElMessage.error(`图片 ${file.name} 上传失败: ${error.message || '未知错误'}`)
    }
  }
  return urls
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    try {
      // 先上传图片
      let photoUrls: string[] = []
      if (imageFiles.value.length > 0) {
        photoUrls = await uploadImages()
      }
      
      // 创建盆栽
      const data: PlantCreateData = {
        ...form,
        initial_photos: photoUrls.length > 0 ? photoUrls : undefined
      }
      
      await plantApi.createPlant(data)
      ElMessage.success('添加成功')
      
      // 重置表单
      resetForm()
      showAddDialog.value = false
      
      // 刷新列表
      fetchPlants()
    } catch (error: any) {
      console.error('添加盆栽失败:', error)
      ElMessage.error(error.message || '添加失败')
    } finally {
      submitLoading.value = false
    }
  })
}

// 重置表单
function resetForm() {
  form.plant_name = ''
  form.species_id = ''
  form.nickname = ''
  form.planting_date = ''
  form.source = ''
  form.initial_photos = []
  form.status = 1
  form.notes = ''
  fileList.value = []
  imageFiles.value = []
  kgInfoLoaded.value = false
  formRef.value?.clearValidate()
}

// 处理植物名称失焦
async function handlePlantNameBlur() {
  if (form.plant_name && form.plant_name.trim()) {
    // 可以选择自动查询或等待用户点击查询按钮
    // await handleSearchKG()
  }
}

// 从知识图谱查询植物信息
async function handleSearchKG() {
  if (!form.plant_name || !form.plant_name.trim()) {
    ElMessage.warning('请先输入植物名称')
    return
  }
  
  kgLoading.value = true
  try {
    // 由于请求拦截器已经解包了 data 字段，这里直接就是后端返回的 data 内容
    const result: any = await plantApi.searchPlantFromKG(form.plant_name.trim())
    
    console.log('知识图谱查询结果:', result)
    console.log('查询前的 species_id:', form.species_id)
    
    if (result && result.scientific_name) {
      // 自动填充物种名（使用学名）
      form.species_id = result.scientific_name
      console.log('查询后的 species_id:', form.species_id)
      console.log('form 完整对象:', JSON.parse(JSON.stringify(form)))
      
      kgInfoLoaded.value = true
      ElMessage.success(`已找到「${result.plant_name || form.plant_name}」的信息`)
      
      // 手动触发表单验证更新
      await new Promise(resolve => setTimeout(resolve, 100))
      formRef.value?.validateField('species_id')
    } else {
      kgInfoLoaded.value = false
      ElMessage.warning(`未找到「${form.plant_name}」的物种信息，请检查名称是否正确`)
    }
  } catch (error: any) {
    kgInfoLoaded.value = false
    console.error('查询知识图谱失败:', error)
    ElMessage.error(error.message || '查询失败')
  } finally {
    kgLoading.value = false
  }
}

// 页码变化
function handlePageChange(page: number) {
  currentPage.value = page
  fetchPlants()
}

// 每页数量变化
function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  fetchPlants()
}

onMounted(() => {
  fetchPlants()
})
</script>

<style scoped lang="scss">
.my-plants {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h2 {
      margin: 0;
      font-size: 24px;
      color: #303133;
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .plant-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: transform 0.3s;
    position: relative;

    &:hover {
      transform: translateY(-4px);
    }

    // 水滴按钮 - 始终可见
    .water-button {
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 10;
      width: 40px;
      height: 40px;
      background: rgba(64, 158, 255, 0.9);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      cursor: pointer;
      transition: all 0.3s;
      opacity: 1;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

      &:hover {
        background: #409eff;
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
      }

      &:active {
        transform: scale(0.95);
      }
    }

    .plant-image {
      width: 100%;
      height: 200px;
      margin-bottom: 12px;
      border-radius: 8px;
      overflow: hidden;

      .el-image {
        width: 100%;
        height: 100%;
      }

      .image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f5f7fa;
        color: #909399;

        .el-icon {
          font-size: inherit;
        }

        &.is-loading {
          animation: rotating 2s linear infinite;
        }
      }
    }

    .plant-info {
      h3 {
        margin: 0 0 8px 0;
        font-size: 16px;
        color: #303133;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .species {
        margin: 0 0 8px 0;
        font-size: 14px;
        color: #909399;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .plant-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;

        .date {
          font-size: 12px;
          color: #c0c4cc;
        }
      }
    }
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 24px;
    
    // 分页选择器调整为适合12个卡片的选项
    :deep(.el-pagination) {
      .el-select {
        width: 110px;
      }
    }
  }

  // 图片上传器样式
  .image-uploader {
    :deep(.el-upload--picture-card) {
      width: 100px;
      height: 100px;
    }

    :deep(.el-upload-list--picture-card) {
      .el-upload-list__item {
        width: 100px;
        height: 100px;
      }
    }
  }

  .upload-tip {
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
  }

  .form-tip {
    margin-top: 4px;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

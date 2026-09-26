<template>
  <div class="identify-page">
    <div class="page-header">
      <h2>看图识花</h2>
      <p class="subtitle">上传图片、粘贴截图或使用摄像头拍摄植物照片进行识别</p>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：图片上传区 -->
      <el-col :xs="24" :md="12">
        <el-card class="upload-card">
          <template #header>
            <div class="card-header">
              <h3>上传图片</h3>
              <el-radio-group v-model="uploadMode" size="small">
                <el-radio-button value="file">
                  <el-icon><Upload /></el-icon>
                  上传
                </el-radio-button>
                <el-radio-button value="paste">
                  <el-icon><DocumentCopy /></el-icon>
                  粘贴
                </el-radio-button>
                <el-radio-button value="camera">
                  <el-icon><Camera /></el-icon>
                  拍照
                </el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <!-- 文件上传模式 -->
          <div v-if="uploadMode === 'file'" class="upload-area">
            <el-upload
              class="image-uploader"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :before-upload="beforeUpload"
              :limit="1"
              accept="image/*"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽图片到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 JPG/PNG/GIF/WEBP 格式，单张不超过 10MB
                </div>
              </template>
            </el-upload>
          </div>

          <!-- 粘贴模式 -->
          <div v-if="uploadMode === 'paste'" class="paste-area" @paste="handlePaste">
            <div class="paste-hint">
              <el-icon :size="48"><DocumentCopy /></el-icon>
              <p>在此处按 Ctrl+V 粘贴图片</p>
              <p class="tip">支持从截图工具、网页等复制的图片</p>
            </div>
          </div>

          <!-- 摄像头模式 -->
          <div v-if="uploadMode === 'camera'" class="camera-area">
            <video
              v-if="!capturedImage"
              ref="videoRef"
              autoplay
              playsinline
              class="camera-video"
            />
            <img
              v-else
              :src="capturedImage"
              alt="Captured"
              class="captured-image"
            />
            <div class="camera-controls">
              <el-button
                v-if="!capturedImage"
                type="primary"
                :icon="Camera"
                @click="capturePhoto"
                :disabled="!cameraActive"
              >
                拍照
              </el-button>
              <el-button
                v-else
                @click="retakePhoto"
              >
                重拍
              </el-button>
              <el-button
                v-if="!cameraActive && uploadMode === 'camera'"
                type="success"
                @click="startCamera"
              >
                开启摄像头
              </el-button>
            </div>
          </div>

          <!-- 预览区域 -->
          <div v-if="previewImage" class="preview-section">
            <h4>图片预览</h4>
            <el-image
              :src="previewImage"
              fit="contain"
              class="preview-image"
            />
            <el-button
              type="primary"
              size="large"
              :loading="identifying"
              @click="handleIdentify"
              style="width: 100%; margin-top: 16px"
            >
              <el-icon><Search /></el-icon>
              开始识别
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：识别结果 -->
      <el-col :xs="24" :md="12">
        <el-card class="result-card" v-if="identifyResult">
          <template #header>
            <h3>识别结果</h3>
          </template>

          <!-- 主要结果 -->
          <div class="main-result">
            <div class="plant-name">
              <h2>{{ identifyResult.top1.plant_name }}</h2>
              <el-tag type="success" size="large">
                置信度: {{ (identifyResult.top1.confidence * 100).toFixed(1) }}%
              </el-tag>
            </div>
            
            <!-- 基本信息 -->
            <div class="plant-basic-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="学名">
                  {{ identifyResult.top1.scientific_name || '待补充' }}
                </el-descriptions-item>
                <el-descriptions-item label="养护难度">
                  {{ identifyResult.top1.difficulty_level || '待补充' }}
                </el-descriptions-item>
                <el-descriptions-item label="生长速度" :span="2">
                  {{ identifyResult.top1.growth_rate || '待补充' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 植物简介 -->
            <div class="plant-description">
              <h4><el-icon><InfoFilled /></el-icon> 植物简介</h4>
              <div class="info-content">
                <p v-if="identifyResult.top1.description">{{ identifyResult.top1.description }}</p>
                <p v-else class="placeholder-text">暂无详细介绍</p>
              </div>
            </div>
          </div>

          <!-- 生长习性 -->
          <div class="growth-habits">
            <h4><el-icon><Sunny /></el-icon> 生长习性</h4>
            <div class="info-content">
              <el-row :gutter="16">
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="habit-item">
                    <div class="habit-label">光照需求</div>
                    <div class="habit-value">{{ identifyResult.top1.care_guide?.light_requirement || '待补充' }}</div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="habit-item">
                    <div class="habit-label">温度范围</div>
                    <div class="habit-value">{{ identifyResult.top1.care_guide?.temperature_range || '待补充' }}</div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="habit-item">
                    <div class="habit-label">湿度要求</div>
                    <div class="habit-value">{{ identifyResult.top1.care_guide?.humidity_requirement || '待补充' }}</div>
                  </div>
                </el-col>
              </el-row>
              <el-row :gutter="16" style="margin-top: 12px">
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="habit-item">
                    <div class="habit-label">土壤类型</div>
                    <div class="habit-value">{{ identifyResult.top1.care_guide?.soil_type || '待补充' }}</div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="habit-item">
                    <div class="habit-label">生长速度</div>
                    <div class="habit-value">{{ identifyResult.top1.growth_rate || '待补充' }}</div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="habit-item">
                    <div class="habit-label">难易程度</div>
                    <div class="habit-value">{{ identifyResult.top1.difficulty_level || '待补充' }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>

          <!-- 养护建议 -->
          <div class="care-guide">
            <h4><el-icon><Watermelon /></el-icon> 养护指南</h4>
            
            <!-- 浇水 -->
            <div class="care-section">
              <h5><el-icon><Watermelon /></el-icon> 浇水管理</h5>
              <div class="care-content">
                <p v-if="identifyResult.top1.care_guide?.water_frequency">{{ identifyResult.top1.care_guide.water_frequency }}</p>
                <p v-else class="placeholder-text">暂无浇水建议</p>
              </div>
            </div>

            <!-- 施肥 -->
            <div class="care-section">
              <h5><el-icon><Food /></el-icon> 施肥方案</h5>
              <div class="care-content">
                <p v-if="identifyResult.top1.care_guide?.fertilization">{{ identifyResult.top1.care_guide.fertilization }}</p>
                <p v-else class="placeholder-text">暂无施肥建议</p>
              </div>
            </div>

            <!-- 修剪 -->
            <div class="care-section">
              <h5><el-icon><Scissor /></el-icon> 修剪整形</h5>
              <div class="care-content">
                <p v-if="identifyResult.top1.care_guide?.pruning_guide">{{ identifyResult.top1.care_guide.pruning_guide }}</p>
                <p v-else class="placeholder-text">暂无修剪建议</p>
              </div>
            </div>

            <!-- 繁殖 -->
            <div class="care-section">
              <h5><el-icon><Postcard /></el-icon> 繁殖方法</h5>
              <div class="care-content">
                <p v-if="identifyResult.top1.care_guide?.propagation_methods">{{ identifyResult.top1.care_guide.propagation_methods }}</p>
                <p v-else class="placeholder-text">暂无繁殖建议</p>
              </div>
            </div>
          </div>

          <!-- 病虫害防治 -->
          <div class="pest-control">
            <h4><el-icon><Warning /></el-icon> 常见病虫害</h4>
            <div class="info-content">
              <div v-if="identifyResult.top1.common_diseases && identifyResult.top1.common_diseases.length > 0">
                <el-alert
                  v-for="(disease, index) in identifyResult.top1.common_diseases"
                  :key="index"
                  :title="disease"
                  type="warning"
                  :closable="false"
                  show-icon
                  style="margin-bottom: 12px"
                />
              </div>
              <div v-if="identifyResult.top1.common_pests && identifyResult.top1.common_pests.length > 0">
                <el-alert
                  v-for="(pest, index) in identifyResult.top1.common_pests"
                  :key="index"
                  :title="pest"
                  type="error"
                  :closable="false"
                  show-icon
                  style="margin-bottom: 12px"
                />
              </div>
              <p v-if="!identifyResult.top1.common_diseases?.length && !identifyResult.top1.common_pests?.length" class="placeholder-text">
                暂无病虫害记录
              </p>
            </div>
          </div>



          <!-- Top 5 结果 -->
          <div class="top-results">
            <h4>其他可能</h4>
            <el-table :data="identifyResult.top5" style="width: 100%">
              <el-table-column prop="plant_name" label="植物名称" />
              <el-table-column prop="confidence" label="置信度" width="120">
                <template #default="{ row }">
                  {{ (row.confidence * 100).toFixed(1) }}%
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button type="primary" @click="saveToPlant">
              <el-icon><Plus /></el-icon>
              保存到我的盆栽
            </el-button>
            <el-button @click="resetIdentify">
              <el-icon><Refresh /></el-icon>
              重新识别
            </el-button>
          </div>
        </el-card>

        <!-- 空状态 -->
        <el-card v-else class="empty-result">
          <el-empty description="上传植物图片开始识别" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 保存到盆栽对话框 -->
    <el-dialog v-model="showSaveDialog" title="保存到我的盆栽" width="500px">
      <el-form label-width="100px">
        <el-form-item label="盆栽名称">
          <el-input v-model="saveForm.plant_name" placeholder="默认使用识别结果" />
        </el-form-item>
        <el-form-item label="物种ID">
          <el-input v-model="saveForm.species_id" disabled />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSaveDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmSaveToPlant" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  UploadFilled, Upload, DocumentCopy, Camera, Search, Plus, Refresh,
  InfoFilled, Sunny, Watermelon, Food, Scissor, Postcard,
  Warning
} from '@element-plus/icons-vue'
import { identifyApi } from '@/api/modules/identify'
import { plantApi } from '@/api/modules/plant'

// 上传模式
const uploadMode = ref<'file' | 'paste' | 'camera'>('file')

// 图片相关
const previewImage = ref<string>('')
const selectedFile = ref<File | null>(null)
const capturedImage = ref<string>('')

// 摄像头相关
const videoRef = ref<HTMLVideoElement | null>(null)
const cameraActive = ref(false)
let stream: MediaStream | null = null

// 识别相关
const identifying = ref(false)
const identifyResult = ref<any>(null)

// 保存对话框
const showSaveDialog = ref(false)
const saving = ref(false)
const saveForm = reactive({
  plant_name: '',
  species_id: ''
})

// 文件选择处理
function handleFileChange(file: any) {
  selectedFile.value = file.raw
  previewImage.value = URL.createObjectURL(file.raw)
  identifyResult.value = null
}

// 上传前验证
function beforeUpload(file: File) {
  const isValidType = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  const isValidSize = file.size / 1024 / 1024 < 10
  
  if (!isValidType) {
    ElMessage.error('只支持 JPG/PNG/GIF/WEBP 格式')
    return false
  }
  if (!isValidSize) {
    ElMessage.error('图片大小不能超过 10MB')
    return false
  }
  return true
}

// 粘贴处理
function handlePaste(event: ClipboardEvent) {
  const items = event.clipboardData?.items
  if (!items) return
  
  for (let i = 0; i < items.length; i++) {
    if (items[i].type.indexOf('image') !== -1) {
      const file = items[i].getAsFile()
      if (file) {
        selectedFile.value = file
        previewImage.value = URL.createObjectURL(file)
        identifyResult.value = null
        ElMessage.success('图片粘贴成功')
      }
      break
    }
  }
}

// 开启摄像头
async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } 
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      cameraActive.value = true
    }
  } catch (error) {
    ElMessage.error('无法访问摄像头，请检查权限设置')
    console.error('Camera error:', error)
  }
}

// 拍照
function capturePhoto() {
  if (!videoRef.value) return
  
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  
  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.drawImage(videoRef.value, 0, 0)
    capturedImage.value = canvas.toDataURL('image/jpeg')
    
    // 转换为 File 对象
    canvas.toBlob((blob) => {
      if (blob) {
        selectedFile.value = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' })
        previewImage.value = capturedImage.value
        identifyResult.value = null
      }
    }, 'image/jpeg')
  }
}

// 重拍
function retakePhoto() {
  capturedImage.value = ''
  previewImage.value = ''
  selectedFile.value = null
}

// 停止摄像头
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
    cameraActive.value = false
  }
}

// 识别植物
async function handleIdentify() {
  console.log('=== 开始识别 ===')
  console.log('selectedFile:', selectedFile.value)
  console.log('previewImage:', previewImage.value)
  
  if (!selectedFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }
  
  console.log('准备调用 API...')
  identifying.value = true
  try {
    const result = await identifyApi.identifyPlant(selectedFile.value)
    console.log('识别结果:', result)
    identifyResult.value = result
    ElMessage.success('识别成功')
  } catch (error: any) {
    console.error('识别错误:', error)
    ElMessage.error(error.message || '识别失败，请重试')
  } finally {
    identifying.value = false
  }
}

// 重置识别
function resetIdentify() {
  identifyResult.value = null
  previewImage.value = ''
  selectedFile.value = null
  capturedImage.value = ''
  stopCamera()
}

// 保存到盆栽
function saveToPlant() {
  if (!identifyResult.value) return
  
  saveForm.plant_name = identifyResult.value.top1.plant_name
  saveForm.species_id = identifyResult.value.top1.species_id || ''
  showSaveDialog.value = true
}

// 确认保存
async function confirmSaveToPlant() {
  saving.value = true
  try {
    await plantApi.createPlant({
      plant_name: saveForm.plant_name,
      species_id: saveForm.species_id,
      initial_photos: previewImage.value ? [previewImage.value] : undefined,
      notes: `通过看图识花功能识别添加`
    })
    ElMessage.success('保存成功')
    showSaveDialog.value = false
    resetIdentify()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 生命周期
onMounted(() => {
  // 监听全局粘贴事件
  window.addEventListener('paste', handlePaste as any)
})

onUnmounted(() => {
  window.removeEventListener('paste', handlePaste as any)
  stopCamera()
})
</script>

<style scoped lang="scss">
.identify-page {
  .page-header {
    margin-bottom: 24px;
    
    h2 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #303133;
    }
    
    .subtitle {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }

  .upload-card,
  .result-card,
  .empty-result {
    min-height: 500px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 18px;
      color: #303133;
    }
  }

  // 上传区域
  .upload-area {
    :deep(.el-upload) {
      width: 100%;
    }

    :deep(.el-upload-dragger) {
      padding: 40px 20px;
    }
  }

  // 粘贴区域
  .paste-area {
    min-height: 300px;
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.3s;

    &:focus {
      border-color: #409eff;
    }

    .paste-hint {
      text-align: center;
      color: #909399;

      .el-icon {
        margin-bottom: 16px;
      }

      p {
        margin: 8px 0;
        font-size: 16px;

        &.tip {
          font-size: 12px;
          color: #c0c4cc;
        }
      }
    }
  }

  // 摄像头区域
  .camera-area {
    .camera-video {
      width: 100%;
      max-height: 400px;
      border-radius: 8px;
      background-color: #000;
    }

    .captured-image {
      width: 100%;
      max-height: 400px;
      border-radius: 8px;
      object-fit: contain;
    }

    .camera-controls {
      margin-top: 16px;
      display: flex;
      gap: 12px;
      justify-content: center;
    }
  }

  // 预览区域
  .preview-section {
    margin-top: 24px;

    h4 {
      margin: 0 0 12px 0;
      font-size: 16px;
      color: #303133;
    }

    .preview-image {
      width: 100%;
      max-height: 300px;
      border-radius: 8px;
    }
  }

  // 结果卡片
  .main-result {
    margin-bottom: 24px;

    .plant-name {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      h2 {
        margin: 0;
        font-size: 24px;
        color: #409eff;
      }
    }

    .plant-basic-info {
      margin-bottom: 16px;
    }

    .plant-description {
      h4 {
        margin: 16px 0 8px 0;
        font-size: 16px;
        color: #303133;
        display: flex;
        align-items: center;
        gap: 6px;

        .el-icon {
          font-size: 18px;
          color: #409eff;
        }
      }
    }
  }

  // 通用信息内容区
  .info-content {
    p {
      margin: 0;
      line-height: 1.8;
      color: #606266;

      &.placeholder-text {
        color: #c0c4cc;
        font-style: italic;
        padding: 12px;
        background-color: #f5f7fa;
        border-radius: 4px;
        border-left: 3px solid #dcdfe6;
      }
    }
  }

  // 生长习性
  .growth-habits {
    margin-bottom: 24px;

    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      color: #303133;
      display: flex;
      align-items: center;
      gap: 6px;

      .el-icon {
        font-size: 18px;
        color: #e6a23c;
      }
    }

    .habit-item {
      padding: 12px;
      background-color: #fafafa;
      border-radius: 6px;
      text-align: center;
      transition: all 0.3s;

      &:hover {
        background-color: #f0f0f0;
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }

      .habit-label {
        font-size: 12px;
        color: #909399;
        margin-bottom: 6px;
      }

      .habit-value {
        font-size: 14px;
        color: #303133;
        font-weight: 500;
      }
    }
  }

  // 养护指南
  .care-guide {
    margin-bottom: 24px;

    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      color: #303133;
      display: flex;
      align-items: center;
      gap: 6px;

      .el-icon {
        font-size: 18px;
        color: #67c23a;
      }
    }

    .care-section {
      margin-bottom: 16px;
      padding: 16px;
      background-color: #f9fafb;
      border-radius: 8px;
      border-left: 4px solid #67c23a;

      &:last-child {
        margin-bottom: 0;
      }

      h5 {
        margin: 0 0 10px 0;
        font-size: 15px;
        color: #303133;
        display: flex;
        align-items: center;
        gap: 6px;

        .el-icon {
          font-size: 16px;
          color: #67c23a;
        }
      }

      .care-content {
        p {
          margin: 0;
          line-height: 1.8;
          color: #606266;

          &.placeholder-text {
            color: #c0c4cc;
            font-style: italic;
            font-size: 13px;
          }
        }
      }
    }
  }

  // 病虫害防治
  .pest-control {
    margin-bottom: 24px;

    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      color: #303133;
      display: flex;
      align-items: center;
      gap: 6px;

      .el-icon {
        font-size: 18px;
        color: #f56c6c;
      }
    }
  }



  .top-results {
    margin-bottom: 24px;

    h4 {
      margin: 0 0 12px 0;
      font-size: 16px;
      color: #303133;
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
  }
}
</style>

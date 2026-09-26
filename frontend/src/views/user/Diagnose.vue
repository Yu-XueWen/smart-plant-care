<template>
  <div class="diagnose-page">
    <div class="page-header">
      <h2>病害诊断</h2>
      <p class="subtitle">上传植物叶片或病灶照片，AI智能识别病虫害并提供防治方案</p>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：图片上传区 -->
      <el-col :xs="24" :md="12">
        <el-card class="upload-card">
          <template #header>
            <div class="card-header">
              <h3>上传病害照片</h3>
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
                  支持 JPG/PNG/GIF/WEBP 格式，单张不超过 10MB<br>
                  <strong>提示：</strong>请拍摄清晰的叶片或病灶部位照片
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
              muted
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
              type="danger"
              size="large"
              :loading="diagnosing"
              @click="handleDiagnose"
              style="width: 100%; margin-top: 16px"
            >
              <el-icon><Search /></el-icon>
              开始诊断
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：诊断结果 -->
      <el-col :xs="24" :md="12">
        <el-card class="result-card" v-if="diagnoseResult">
          <template #header>
            <h3>诊断结果</h3>
          </template>

          <!-- 主要病害 -->
          <div class="main-result">
            <div class="disease-name">
              <h2>{{ diagnoseResult.primary_disease }}</h2>
              <el-tag type="danger" size="large">
                置信度: {{ (diagnoseResult.confidence * 100).toFixed(1) }}%
              </el-tag>
            </div>

            <!-- 症状描述 -->
            <div class="symptoms-section">
              <h4><el-icon><Warning /></el-icon> 症状特征</h4>
              <div class="info-content">
                <p>{{ diagnoseResult.symptoms }}</p>
              </div>
            </div>

            <!-- 防治方案 -->
            <div class="treatment-section">
              <h4><el-icon><FirstAidKit /></el-icon> 防治方案</h4>
              
              <!-- 化学防治 -->
              <div class="treatment-item chemical">
                <h5><el-icon><Medal /></el-icon> 化学防治</h5>
                <div class="treatment-content">
                  <p>{{ diagnoseResult.treatment.chemical }}</p>
                </div>
              </div>

              <!-- 有机防治 -->
              <div class="treatment-item organic">
                <h5><el-icon><Star /></el-icon> 有机防治</h5>
                <div class="treatment-content">
                  <p>{{ diagnoseResult.treatment.organic }}</p>
                </div>
              </div>

              <!-- 预防措施 -->
              <div class="treatment-item prevention">
                <h5><el-icon><CircleCheck /></el-icon> 预防措施</h5>
                <div class="treatment-content">
                  <p>{{ diagnoseResult.treatment.prevention }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button type="primary" @click="saveToHistory">
              <el-icon><Document /></el-icon>
              保存到历史记录
            </el-button>
            <el-button @click="resetDiagnose">
              <el-icon><Refresh /></el-icon>
              重新诊断
            </el-button>
          </div>
        </el-card>

        <!-- 空状态 -->
        <el-card v-else class="empty-result">
          <el-empty description="上传病害图片开始诊断" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  UploadFilled, Upload, DocumentCopy, Camera, Search, Refresh,
  Warning, FirstAidKit, Medal, CircleCheck, Document
} from '@element-plus/icons-vue'
import { diagnoseApi } from '@/api/modules/diagnose'

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

// 诊断相关
const diagnosing = ref(false)
const diagnoseResult = ref<any>(null)

// 文件选择处理
function handleFileChange(file: any) {
  selectedFile.value = file.raw
  previewImage.value = URL.createObjectURL(file.raw)
  diagnoseResult.value = null
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
        diagnoseResult.value = null
        ElMessage.success('图片粘贴成功')
      }
      break
    }
  }
}

// 开启摄像头
async function startCamera() {
  // 检查安全上下文（getUserMedia 仅在 HTTPS 或 localhost 下可用）
  if (!window.isSecureContext) {
    ElMessage.error('摄像头仅在 HTTPS 环境下可用，请使用 HTTPS 访问本页面')
    return
  }
  // 检查浏览器是否支持
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    ElMessage.error('当前浏览器不支持摄像头访问，请更换浏览器或使用 HTTPS 访问')
    return
  }

  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' },
      audio: false
    })
    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      await videoRef.value.play()
      cameraActive.value = true
    }
  } catch (error: any) {
    cameraActive.value = false
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
      ElMessage.error('摄像头权限被拒绝，请在浏览器设置中允许访问摄像头')
    } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
      ElMessage.error('未检测到摄像头设备')
    } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
      ElMessage.error('摄像头被其他应用占用，请关闭后重试')
    } else if (error.name === 'OverconstrainedError') {
      // 后置摄像头不可用时回退为默认摄像头
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        await nextTick()
        if (videoRef.value) {
          videoRef.value.srcObject = stream
          await videoRef.value.play()
          cameraActive.value = true
        }
      } catch {
        ElMessage.error('无法访问摄像头，请检查权限设置')
      }
    } else {
      ElMessage.error('无法访问摄像头，请检查权限设置')
    }
    console.error('Camera error:', error)
  }
}

// 切换上传模式时自动管理摄像头
watch(uploadMode, (mode, oldMode) => {
  if (mode === 'camera') {
    capturedImage.value = ''
    nextTick(() => startCamera())
  } else if (oldMode === 'camera') {
    stopCamera()
  }
})

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
        diagnoseResult.value = null
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

// 诊断病害
async function handleDiagnose() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }
  
  diagnosing.value = true
  try {
    const result = await diagnoseApi.diagnoseDisease(selectedFile.value)
    diagnoseResult.value = result
    ElMessage.success('诊断完成')
  } catch (error: any) {
    ElMessage.error(error.message || '诊断失败，请重试')
    console.error('Diagnose error:', error)
  } finally {
    diagnosing.value = false
  }
}

// 重置诊断
function resetDiagnose() {
  diagnoseResult.value = null
  previewImage.value = ''
  selectedFile.value = null
  capturedImage.value = ''
  stopCamera()
}

// 保存到历史
function saveToHistory() {
  ElMessage.success('诊断结果已自动保存至历史记录')
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
.diagnose-page {
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
      border-color: #f56c6c;
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

    .disease-name {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      h2 {
        margin: 0;
        font-size: 24px;
        color: #f56c6c;
      }
    }

    .symptoms-section {
      margin-bottom: 24px;

      h4 {
        margin: 0 0 12px 0;
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
    }

    .treatment-section {
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

      .treatment-item {
        margin-bottom: 16px;
        padding: 16px;
        border-radius: 8px;
        border-left: 4px solid;

        &.chemical {
          background-color: #fef0f0;
          border-left-color: #f56c6c;

          h5 {
            color: #f56c6c;
          }
        }

        &.organic {
          background-color: #f0f9ff;
          border-left-color: #409eff;

          h5 {
            color: #409eff;
          }
        }

        &.prevention {
          background-color: #f0f9eb;
          border-left-color: #67c23a;

          h5 {
            color: #67c23a;
          }
        }

        h5 {
          margin: 0 0 10px 0;
          font-size: 15px;
          display: flex;
          align-items: center;
          gap: 6px;

          .el-icon {
            font-size: 16px;
          }
        }

        .treatment-content {
          p {
            margin: 0;
            line-height: 1.8;
            color: #606266;
          }
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
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
  }
}
</style>

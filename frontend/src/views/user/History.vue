<template>
  <div class="history-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon><Clock /></el-icon> 历史记录</h2>
      <p class="subtitle">查看您的识花和诊断记录</p>
    </div>

    <!-- 类型选择标签页 -->
    <el-card class="history-card">
      <el-tabs v-model="activeTab" @tab-change="(name: any) => handleTabChange(name)">
        <!-- 识花记录 -->
        <el-tab-pane label="识花记录" name="identify">
          <div v-loading="loading" class="history-list">
            <el-empty v-if="!loading && identifyList.length === 0" description="暂无识花记录" />
            
            <div v-else class="record-grid">
              <el-card 
                v-for="record in identifyList" 
                :key="record.id" 
                class="record-item"
                shadow="hover"
                @click="viewDetail('identify', record.id)"
              >
                <div class="record-image">
                  <el-image 
                    :src="getImageUrl(record.image_url)" 
                    fit="cover"
                    lazy
                    :preview-src-list="[getImageUrl(record.image_url)]"
                    preview-teleported
                  >
                    <template #placeholder>
                      <div class="image-placeholder">
                        <el-icon class="is-loading"><Loading /></el-icon>
                        <span>加载中...</span>
                      </div>
                    </template>
                    <template #error>
                      <div class="image-error">
                        <el-icon><Picture /></el-icon>
                        <span>图片加载失败</span>
                      </div>
                    </template>
                  </el-image>
                </div>
                
                <div class="record-info">
                  <h4 class="plant-name">{{ record.plant_name }}</h4>
                  <el-tag v-if="record.confidence" size="small" type="success">
                    置信度: {{ (record.confidence * 100).toFixed(1) }}%
                  </el-tag>
                  <p class="record-time">{{ formatTime(record.created_at) }}</p>
                </div>
                
                <div class="record-actions">
                  <el-button 
                    size="small" 
                    type="primary" 
                    link
                    @click.stop="viewDetail('identify', record.id)"
                  >
                    查看详情
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    link
                    @click.stop="handleDelete('identify', record.id)"
                  >
                    删除
                  </el-button>
                </div>
              </el-card>
            </div>

            <!-- 分页 -->
            <div v-if="identifyTotal > 0" class="pagination-container">
              <el-pagination
                v-model:current-page="identifyPage"
                v-model:page-size="identifyPageSize"
                :total="identifyTotal"
                :page-sizes="[12, 24, 36, 48]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="loadIdentifyHistory"
                @current-change="loadIdentifyHistory"
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 诊断记录 -->
        <el-tab-pane label="诊断记录" name="diagnose">
          <div v-loading="loading" class="history-list">
            <el-empty v-if="!loading && diagnoseList.length === 0" description="暂无诊断记录" />
            
            <div v-else class="record-grid">
              <el-card 
                v-for="record in diagnoseList" 
                :key="record.id" 
                class="record-item"
                shadow="hover"
                @click="viewDetail('diagnose', record.id)"
              >
                <div class="record-image">
                  <el-image 
                    :src="getImageUrl(record.image_url)" 
                    fit="cover"
                    lazy
                    :preview-src-list="[getImageUrl(record.image_url)]"
                    preview-teleported
                  >
                    <template #placeholder>
                      <div class="image-placeholder">
                        <el-icon class="is-loading"><Loading /></el-icon>
                        <span>加载中...</span>
                      </div>
                    </template>
                    <template #error>
                      <div class="image-error">
                        <el-icon><Picture /></el-icon>
                        <span>图片加载失败</span>
                      </div>
                    </template>
                  </el-image>
                </div>
                
                <div class="record-info">
                  <h4 class="disease-name">{{ record.disease_name }}</h4>
                  <el-tag v-if="record.confidence" size="small" type="danger">
                    置信度: {{ (record.confidence * 100).toFixed(1) }}%
                  </el-tag>
                  <p class="record-time">{{ formatTime(record.created_at) }}</p>
                </div>
                
                <div class="record-actions">
                  <el-button 
                    size="small" 
                    type="primary" 
                    link
                    @click.stop="viewDetail('diagnose', record.id)"
                  >
                    查看详情
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    link
                    @click.stop="handleDelete('diagnose', record.id)"
                  >
                    删除
                  </el-button>
                </div>
              </el-card>
            </div>

            <!-- 分页 -->
            <div v-if="diagnoseTotal > 0" class="pagination-container">
              <el-pagination
                v-model:current-page="diagnosePage"
                v-model:page-size="diagnosePageSize"
                :total="diagnoseTotal"
                :page-sizes="[12, 24, 36, 48]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="loadDiagnoseHistory"
                @current-change="loadDiagnoseHistory"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="detailType === 'identify' ? '识花记录详情' : '诊断记录详情'"
      width="700px"
      destroy-on-close
    >
      <div v-loading="detailLoading" class="detail-content">
        <template v-if="detailData">
          <!-- 图片展示 -->
          <div class="detail-image">
            <el-image 
              :src="getImageUrl(detailData.image_url)" 
              fit="contain"
              :preview-src-list="[getImageUrl(detailData.image_url)]"
              preview-teleported
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                  <span>图片加载失败</span>
                </div>
              </template>
            </el-image>
          </div>

          <!-- 识花详情 -->
          <template v-if="detailType === 'identify'">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="植物名称">
                <strong>{{ detailData.plant_name }}</strong>
              </el-descriptions-item>
              <el-descriptions-item label="置信度">
                <el-tag type="success">
                  {{ detailData.confidence ? (detailData.confidence * 100).toFixed(1) + '%' : 'N/A' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="识别时间" :span="2">
                {{ formatTime(detailData.created_at) }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 详细信息（如果有） -->
            <div v-if="detailData.result_detail" class="detail-section">
              <h4>详细信息</h4>
              <el-card shadow="never">
                <pre class="json-display">{{ JSON.stringify(detailData.result_detail, null, 2) }}</pre>
              </el-card>
            </div>
          </template>

          <!-- 诊断详情 -->
          <template v-else>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="病害名称">
                <strong>{{ detailData.disease_name }}</strong>
              </el-descriptions-item>
              <el-descriptions-item label="置信度">
                <el-tag type="danger">
                  {{ detailData.confidence ? (detailData.confidence * 100).toFixed(1) + '%' : 'N/A' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="诊断时间" :span="2">
                {{ formatTime(detailData.created_at) }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 症状描述 -->
            <div v-if="detailData.symptoms" class="detail-section">
              <h4>症状描述</h4>
              <el-alert 
                :title="detailData.symptoms" 
                type="warning" 
                :closable="false"
                show-icon
              />
            </div>

            <!-- 防治方案 -->
            <div v-if="detailData.treatment" class="detail-section">
              <h4>防治方案</h4>
              <el-card shadow="never">
                <div v-if="typeof detailData.treatment === 'object'">
                  <p v-if="detailData.treatment.chemical"><strong>化学防治：</strong>{{ detailData.treatment.chemical }}</p>
                  <p v-if="detailData.treatment.organic"><strong>有机防治：</strong>{{ detailData.treatment.organic }}</p>
                  <p v-if="detailData.treatment.prevention"><strong>预防措施：</strong>{{ detailData.treatment.prevention }}</p>
                </div>
                <pre v-else class="json-display">{{ typeof detailData.treatment === 'string' ? detailData.treatment : JSON.stringify(detailData.treatment, null, 2) }}</pre>
              </el-card>
            </div>
          </template>
        </template>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="danger" @click="handleDeleteFromDetail">删除记录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Picture, Loading } from '@element-plus/icons-vue'
import { historyApi } from '@/api/modules/history'
import type { IdentifyHistoryItem, DiagnoseHistoryItem } from '@/types/models'

// 当前激活的标签页
const activeTab = ref<'identify' | 'diagnose'>('identify')
const loading = ref(false)

// 识花记录相关
const identifyList = ref<IdentifyHistoryItem[]>([])
const identifyTotal = ref(0)
const identifyPage = ref(1)
const identifyPageSize = ref(12) // 每页显示12个卡片

// 诊断记录相关
const diagnoseList = ref<DiagnoseHistoryItem[]>([])
const diagnoseTotal = ref(0)
const diagnosePage = ref(1)
const diagnosePageSize = ref(12) // 每页显示12个卡片

// 详情对话框相关
const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const detailType = ref<'identify' | 'diagnose'>('identify')
const detailData = ref<any>(null)
const currentDetailId = ref<number | null>(null)

// 加载识花历史
async function loadIdentifyHistory() {
  try {
    loading.value = true
    const response = await historyApi.getIdentifyHistory({
      page: identifyPage.value,
      page_size: identifyPageSize.value
    })
    
    // 响应拦截器已经返回了 data，所以直接使用 response
    identifyList.value = response.items || []
    identifyTotal.value = response.total || 0
  } catch (error: any) {
    console.error('加载识花历史失败:', error)
    ElMessage.error(error.message || '加载识花历史失败')
  } finally {
    loading.value = false
  }
}

// 加载诊断历史
async function loadDiagnoseHistory() {
  try {
    loading.value = true
    const response = await historyApi.getDiagnoseHistory({
      page: diagnosePage.value,
      page_size: diagnosePageSize.value
    })
    
    // 响应拦截器已经返回了 data，所以直接使用 response
    diagnoseList.value = response.items || []
    diagnoseTotal.value = response.total || 0
  } catch (error: any) {
    console.error('加载诊断历史失败:', error)
    ElMessage.error(error.message || '加载诊断历史失败')
  } finally {
    loading.value = false
  }
}

// 标签页切换
function handleTabChange(tab: string) {
  if (tab === 'identify' && identifyList.value.length === 0) {
    loadIdentifyHistory()
  } else if (tab === 'diagnose' && diagnoseList.value.length === 0) {
    loadDiagnoseHistory()
  }
}

// 查看详情
async function viewDetail(type: 'identify' | 'diagnose', id: number) {
  try {
    detailLoading.value = true
    detailDialogVisible.value = true
    detailType.value = type
    currentDetailId.value = id
    
    const response = await historyApi.getHistoryDetail(type, id)
    
    // 响应拦截器已经返回了 data，所以直接使用 response
    detailData.value = response
  } catch (error: any) {
    console.error('加载详情失败:', error)
    ElMessage.error(error.message || '加载详情失败')
    detailDialogVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

// 从详情页删除
async function handleDeleteFromDetail() {
  if (!currentDetailId.value) return
  
  try {
    await ElMessageBox.confirm(
      '确定要删除这条记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await historyApi.deleteHistory(detailType.value, currentDetailId.value)
    ElMessage.success('删除成功')
    
    // 关闭对话框
    detailDialogVisible.value = false
    
    // 重新加载列表
    if (detailType.value === 'identify') {
      loadIdentifyHistory()
    } else {
      loadDiagnoseHistory()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 删除记录
async function handleDelete(type: 'identify' | 'diagnose', id: number) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await historyApi.deleteHistory(type, id)
    ElMessage.success('删除成功')
    
    // 重新加载列表
    if (type === 'identify') {
      loadIdentifyHistory()
    } else {
      loadDiagnoseHistory()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}
function formatTime(timeStr: string): string {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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
  
  // 其他情况，尝试作为 /uploads 下的路径
  return `/uploads/${url.startsWith('/') ? url.substring(1) : url}`
}

// 初始化加载
onMounted(() => {
  loadIdentifyHistory()
})
</script>

<style scoped lang="scss">
.history-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 24px;
    
    h2 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #303133;
      display: flex;
      align-items: center;
      gap: 8px;

      .el-icon {
        font-size: 28px;
        color: #409eff;
      }
    }
    
    .subtitle {
      margin: 0;
      font-size: 14px;
      color: #909399;
    }
  }

  .history-card {
    :deep(.el-tabs__header) {
      margin-bottom: 20px;
    }

    :deep(.el-tabs__item) {
      font-size: 16px;
      font-weight: 500;
    }
  }

  .history-list {
    min-height: 300px;
  }

  .record-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
    
    // 大屏幕显示4列
    @media (min-width: 1200px) {
      grid-template-columns: repeat(4, 1fr);
    }
  }

  .record-item {
    transition: all 0.3s;
    cursor: pointer;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .record-image {
      width: 100%;
      height: 200px;
      overflow: hidden;
      border-radius: 8px;
      margin-bottom: 12px;

      .el-image {
        width: 100%;
        height: 100%;
      }

      .image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background-color: #f5f7fa;
        color: #909399;
        font-size: 12px;

        .el-icon {
          font-size: 32px;
        }
      }

      .image-error {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background-color: #f5f7fa;
        color: #c0c4cc;
        font-size: 12px;

        .el-icon {
          font-size: 48px;
        }
      }
    }

    .record-info {
      margin-bottom: 12px;

      .plant-name,
      .disease-name {
        margin: 0 0 8px 0;
        font-size: 16px;
        color: #303133;
        font-weight: 600;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .record-time {
        margin: 8px 0 0 0;
        font-size: 12px;
        color: #909399;
      }
    }

    .record-actions {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid #ebeef5;
    }
  }

  .pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
  }
}

// 详情对话框样式
.detail-content {
  .detail-image {
    width: 100%;
    max-height: 400px;
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
    background-color: #f5f7fa;

    .el-image {
      width: 100%;
      height: 100%;
    }

    .image-error {
      width: 100%;
      height: 300px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
      color: #c0c4cc;

      .el-icon {
        font-size: 64px;
      }

      span {
        font-size: 14px;
      }
    }
  }

  .detail-section {
    margin-top: 20px;

    h4 {
      margin: 0 0 12px 0;
      font-size: 16px;
      color: #303133;
      font-weight: 600;
    }

    .json-display {
      margin: 0;
      padding: 12px;
      background-color: #f5f7fa;
      border-radius: 4px;
      font-size: 13px;
      line-height: 1.6;
      overflow-x: auto;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    p {
      margin: 8px 0;
      line-height: 1.6;
      color: #606266;

      strong {
        color: #303133;
      }
    }
  }

  :deep(.el-descriptions) {
    margin-bottom: 20px;
  }

  :deep(.el-alert) {
    margin-top: 8px;
  }
}
</style>

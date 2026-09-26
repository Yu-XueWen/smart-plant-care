<template>
  <div class="recommend-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Star /></el-icon>
        智能养花推荐
      </h1>
      <p class="page-subtitle">填写问卷，为您量身定制最适合的植物推荐</p>
    </div>

    <!-- 问卷区域 -->
    <div v-if="!showResults" class="questionnaire-section">
      <Questionnaire @submit="handleQuestionnaireSubmit" />
    </div>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-section">
      <el-card>
        <div class="loading-content">
          <el-icon class="is-loading" :size="60"><Loading /></el-icon>
          <p class="loading-text">正在分析您的偏好，为您推荐最合适的植物...</p>
          <el-progress :percentage="progress" :stroke-width="8" />
        </div>
      </el-card>
    </div>

    <!-- 推荐结果 -->
    <div v-else class="results-section">
      <!-- 问卷摘要 -->
      <el-card class="summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>您的养护偏好</span>
            <el-button type="primary" text @click="resetQuestionnaire">
              <el-icon><Refresh /></el-icon>
              重新填写
            </el-button>
          </div>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="经验水平">
            {{ questionnaireSummary.experience_level }}
          </el-descriptions-item>
          <el-descriptions-item label="光照条件">
            {{ questionnaireSummary.light_condition }}
          </el-descriptions-item>
          <el-descriptions-item label="空间大小">
            {{ questionnaireSummary.space_size }}
          </el-descriptions-item>
          <el-descriptions-item label="可用时间">
            {{ questionnaireSummary.time_availability }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="preferences-summary">
          <span class="label">偏好标签：</span>
          <span class="value">{{ questionnaireSummary.preferences }}</span>
        </div>
        <div class="match-stats">
          <el-statistic title="匹配植物总数" :value="totalMatches" />
        </div>
      </el-card>

      <!-- 推荐列表 -->
      <div class="recommendations-grid">
        <RecommendCard
          v-for="(item, index) in paginatedRecommendations"
          :key="index"
          :recommendation="item"
          :rank="(currentPage - 1) * pageSize + index + 1"
        />
      </div>

      <!-- 分页 -->
      <div v-if="recommendations.length > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 36, 48]"
          :total="recommendations.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="recommendations.length === 0"
        description="暂无推荐结果，请尝试调整问卷答案"
      >
        <el-button type="primary" @click="resetQuestionnaire">
          重新填写问卷
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, Loading, Document, Refresh } from '@element-plus/icons-vue'
import Questionnaire from '@/components/recommend/Questionnaire.vue'
import RecommendCard from '@/components/recommend/RecommendCard.vue'
import { recommendApi } from '@/api/modules/recommend'
import type { QuestionnaireAnswers, Recommendation } from '@/types/models'

const showResults = ref(false)
const loading = ref(false)
const progress = ref(0)
const recommendations = ref<Recommendation[]>([])
const totalMatches = ref(0)
const questionnaireSummary = reactive({
  experience_level: '',
  light_condition: '',
  space_size: '',
  time_availability: '',
  preferences: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(12)

// 计算当前页的推荐列表
const paginatedRecommendations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return recommendations.value.slice(start, end)
})

// 处理问卷提交
const handleQuestionnaireSubmit = async (answers: QuestionnaireAnswers) => {
  loading.value = true
  showResults.value = false
  
  // 模拟进度条
  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += 10
    }
  }, 200)

  try {
    const result = await recommendApi.getRecommendation(answers)
    
    clearInterval(progressInterval)
    progress.value = 100
    
    // 延迟一下显示结果，让用户看到100%
    setTimeout(() => {
      recommendations.value = (result as any).recommendations || []
      totalMatches.value = (result as any).total_matches || 0
      Object.assign(questionnaireSummary, (result as any).questionnaire_summary || {})
      showResults.value = true
      loading.value = false
      progress.value = 0
      
      ElMessage.success(`为您找到 ${(result as any).total_matches} 种匹配的植物`)
    }, 500)
  } catch (error) {
    clearInterval(progressInterval)
    loading.value = false
    progress.value = 0
    ElMessage.error('获取推荐失败，请稍后重试')
    console.error('推荐错误:', error)
  }
}

// 重置问卷
const resetQuestionnaire = () => {
  showResults.value = false
  recommendations.value = []
  totalMatches.value = 0
  progress.value = 0
  currentPage.value = 1
  pageSize.value = 12
}

// 分页大小变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1 // 重置到第一页
}

// 当前页变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped lang="scss">
// ========== 设计系统变量 ==========
$primary-green: #2d6a4f;
$primary-green-light: #40916c;
$primary-green-pale: #d8f3dc;
$accent-lime: #95d5b2;
$text-primary: #1b4332;
$text-secondary: #52796f;
$border-light: #b7e4c7;
$shadow-soft: 0 2px 12px rgba(45, 106, 79, 0.08);
$shadow-medium: 0 4px 20px rgba(45, 106, 79, 0.12);
$radius-md: 16px;
$radius-lg: 24px;

.recommend-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 40%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 48px 24px 44px;
  background: linear-gradient(135deg, $primary-green 0%, $primary-green-light 50%, $accent-lime 100%);
  border-radius: $radius-lg;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(45, 106, 79, 0.25);

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
  }

  &::after {
    content: '🌿';
    position: absolute;
    bottom: -10px;
    left: -10px;
    font-size: 120px;
    opacity: 0.08;
    transform: rotate(-15deg);
  }

  .page-title {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    font-size: 34px;
    font-weight: 800;
    margin: 0 0 14px 0;
    position: relative;
    z-index: 1;
    letter-spacing: -0.5px;

    .el-icon {
      font-size: 38px;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15));
    }
  }

  .page-subtitle {
    font-size: 17px;
    opacity: 0.92;
    margin: 0;
    position: relative;
    z-index: 1;
    font-weight: 400;
  }
}

.questionnaire-section {
  animation: fadeIn 0.6s ease-out;
}

.loading-section {
  animation: fadeIn 0.5s ease-in;

  .loading-content {
    text-align: center;
    padding: 60px 20px;

    .el-icon {
      color: $primary-green;
      margin-bottom: 20px;
    }

    .loading-text {
      font-size: 18px;
      color: $text-secondary;
      margin: 20px 0 30px;
    }

    .el-progress {
      max-width: 400px;
      margin: 0 auto;
    }
  }
}

.results-section {
  animation: fadeIn 0.5s ease-in;
}

.summary-card {
  margin-bottom: 30px;
  border-radius: $radius-md;
  overflow: hidden;

  :deep(.el-card__header) {
    background: linear-gradient(135deg, $primary-green-pale, #ffffff);
    border-bottom: 1px solid $border-light;
    padding: 18px 24px;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;

    .el-icon {
      font-size: 20px;
      color: $primary-green;
    }
  }

  .preferences-summary {
    margin-top: 16px;
    padding: 14px 18px;
    background: linear-gradient(135deg, $primary-green-pale, #f0fdf4);
    border-radius: 10px;
    border: 1px solid rgba(183, 228, 199, 0.5);

    .label {
      font-weight: 600;
      color: $text-secondary;
      margin-right: 8px;
    }

    .value {
      color: $text-primary;
    }
  }

  .match-stats {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  padding: 20px 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .recommend-page {
    padding: 12px;
  }

  .page-header {
    padding: 32px 18px;
    border-radius: $radius-md;

    .page-title {
      font-size: 24px;

      .el-icon {
        font-size: 28px;
      }
    }

    .page-subtitle {
      font-size: 14px;
    }
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .summary-card {
    :deep(.el-descriptions) {
      .el-descriptions__body {
        .el-descriptions__table {
          .el-descriptions__cell {
            padding: 8px 12px;
          }
        }
      }
    }
  }
}
</style>

<template>
  <el-card class="recommend-card" :body-style="{ padding: '20px' }">
    <!-- 排名徽章 -->
    <div class="card-header">
      <div class="rank-badge" :class="getRankClass(rank)">
        #{{ rank }}
      </div>
      <h3 class="plant-name">{{ recommendation.plant_name }}</h3>
      <p v-if="recommendation.scientific_name" class="scientific-name">
        {{ recommendation.scientific_name }}
      </p>
    </div>

    <!-- 匹配度进度条 -->
    <div class="match-score-section">
      <div class="score-label">匹配度</div>
      <el-progress
        :percentage="recommendation.match_score"
        :stroke-width="12"
        :color="getScoreColor(recommendation.match_score)"
      >
        <template #default="{ percentage }">
          <span class="score-text">{{ percentage }}%</span>
        </template>
      </el-progress>
    </div>

    <!-- 植物信息 -->
    <div class="plant-info">
      <div class="plant-header">
        <h3 class="plant-name">{{ recommendation.plant_name }}</h3>
        <p v-if="recommendation.scientific_name" class="scientific-name">
          {{ recommendation.scientific_name }}
        </p>
      </div>

      <!-- 标签 -->
      <div class="tags-container">
        <el-tag
          v-for="tag in (recommendation.tags || []).slice(0, 3)"
          :key="tag"
          size="small"
          type="info"
          class="tag-item"
        >
          {{ tag }}
        </el-tag>
      </div>

      <!-- 养护难度 -->
      <div class="care-difficulty">
        <span class="label">养护难度：</span>
        <el-tag :type="getDifficultyType(recommendation.care_difficulty)" size="small">
          {{ getDifficultyText(recommendation.care_difficulty) }}
        </el-tag>
      </div>

      <!-- 养护信息 -->
      <el-descriptions :column="1" size="small" border class="care-info">
        <el-descriptions-item label="光照">
          {{ getLightText(recommendation.light_requirement) }}
        </el-descriptions-item>
        <el-descriptions-item label="浇水">
          {{ getWaterText(recommendation.water_frequency || '') }}
        </el-descriptions-item>
        <el-descriptions-item label="温度">
          {{ recommendation.temperature_range }}
        </el-descriptions-item>
        <el-descriptions-item label="湿度">
          {{ recommendation.humidity_range }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 推荐理由 -->
      <div class="reasons-section">
        <h4 class="section-title">
          <el-icon><Star /></el-icon>
          推荐理由
        </h4>
        <ul class="reasons-list">
          <li v-for="(reason, index) in recommendation.reasons" :key="index">
            <el-icon color="#67c23a"><Check /></el-icon>
            <span>{{ reason }}</span>
          </li>
        </ul>
      </div>

      <!-- 功效 -->
      <div v-if="recommendation.benefits && recommendation.benefits.length > 0" class="benefits-section">
        <h4 class="section-title">
          <el-icon><Medal /></el-icon>
          植物功效
        </h4>
        <div class="benefits-tags">
          <el-tag
            v-for="benefit in recommendation.benefits"
            :key="benefit"
            type="success"
            size="small"
            effect="plain"
          >
            {{ benefit }}
          </el-tag>
        </div>
      </div>

      <!-- 描述 -->
      <div v-if="recommendation.description" class="description-section">
        <h4 class="section-title">
          <el-icon><InfoFilled /></el-icon>
          植物简介
        </h4>
        <p class="description-text">{{ recommendation.description }}</p>
      </div>

      <!-- 养护技巧 -->
      <div v-if="recommendation.care_tips" class="tips-section">
        <h4 class="section-title">
          <el-icon><Tools /></el-icon>
          养护技巧
        </h4>
        <p class="tips-text">{{ recommendation.care_tips }}</p>
      </div>


    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Star, Check, InfoFilled, Tools, Medal } from '@element-plus/icons-vue'
import type { Recommendation } from '@/types/models'

defineProps<{
  recommendation: Recommendation
  rank: number
}>()

// 获取排名样式类
const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return 'rank-normal'
}

// 获取分数颜色
const getScoreColor = (score: number) => {
  if (score >= 90) return '#67c23a'
  if (score >= 75) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#909399'
}

// 获取难度类型
const getDifficultyType = (difficulty: string): 'success' | 'warning' | 'danger' | 'info' => {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return map[difficulty] || 'info'
}

// 获取难度文本
const getDifficultyText = (difficulty: string) => {
  const map: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[difficulty] || difficulty
}

// 获取光照文本
const getLightText = (light: string) => {
  const map: Record<string, string> = {
    low: '弱光',
    medium: '中等光照',
    high: '强光',
    full_sun: '全日照'
  }
  return map[light] || light
}

// 获取浇水文本
const getWaterText = (frequency: string) => {
  const map: Record<string, string> = {
    daily: '每天',
    every_2_days: '每2天',
    weekly: '每周',
    biweekly: '每两周',
    monthly: '每月'
  }
  return map[frequency] || frequency
}


</script>

<style scoped lang="scss">
.recommend-card {
  border-radius: 12px;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;

  .rank-badge {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 16px;
    color: white;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

    &.rank-gold {
      background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
    }

    &.rank-silver {
      background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
    }

    &.rank-bronze {
      background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
    }

    &.rank-normal {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
  }

  .plant-name {
    margin: 0;
    font-size: 22px;
    font-weight: bold;
    color: #303133;
    flex: 1;
  }

  .scientific-name {
    margin: 0;
    font-size: 14px;
    color: #909399;
    font-style: italic;
  }
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;

  .tag-item {
    border-radius: 12px;
  }
}

.care-difficulty {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;

  .label {
    font-size: 14px;
    color: #606266;
  }
}

.care-info {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;

  :deep(.el-descriptions__label) {
    font-weight: 600;
    width: 80px;
  }
}

.match-score-section {
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf0 100%);
  border-radius: 8px;

  .score-label {
    font-size: 14px;
    font-weight: 600;
    color: #606266;
    margin-bottom: 8px;
  }

  .el-progress {
    .score-text {
      font-size: 16px;
      font-weight: bold;
      color: #303133;
    }
  }
}

.reasons-section,
.benefits-section,
.description-section,
.tips-section {
  margin-bottom: 16px;

  .section-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 15px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 10px 0;

    .el-icon {
      color: #667eea;
    }
  }
}

.reasons-list {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 6px 0;
    font-size: 14px;
    color: #606266;
    line-height: 1.6;

    .el-icon {
      margin-top: 2px;
      flex-shrink: 0;
    }
  }
}

.benefits-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.description-text,
.tips-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin: 0;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
}
</style>

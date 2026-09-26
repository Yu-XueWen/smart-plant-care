import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Recommendation, QuestionnaireAnswers } from '@/types/models'
import { recommendApi } from '@/api/modules/recommend'

export const useRecommendStore = defineStore('recommend', () => {
  const recommendations = ref<Recommendation[]>([])
  const loading = ref(false)

  // 获取推荐
  async function getRecommendations(answers: QuestionnaireAnswers) {
    loading.value = true
    try {
      const result = await recommendApi.getRecommendation(answers)
      recommendations.value = result
      return result
    } catch (error) {
      console.error('获取推荐失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 清除推荐结果
  function clearRecommendations() {
    recommendations.value = []
  }

  return {
    recommendations,
    loading,
    getRecommendations,
    clearRecommendations,
  }
})

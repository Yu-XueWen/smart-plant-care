import request from '../request'
import type { Recommendation, QuestionnaireAnswers } from '@/types/models'

export const recommendApi = {
  // 获取推荐（默认返回所有符合条件的植物）
  getRecommendation(answers: QuestionnaireAnswers, topN: number = 0) {
    return request.post<Recommendation[]>('/recommend', answers, {
      params: { top_n: topN }
    })
  },
}

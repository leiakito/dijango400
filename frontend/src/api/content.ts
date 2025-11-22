/**
 * 内容创作相关 API
 */
import { request } from '@/utils/request'
import type { Strategy, StrategyForm } from '@/types/content'

/**
 * 获取攻略列表
 */
export function getStrategyList(params?: any) {
  return request.get('/content/strategies/', { params })
}

/**
 * 获取攻略详情
 */
export function getStrategyDetail(id: number) {
  return request.get(`/content/strategies/${id}/`)
}

/**
 * 创建攻略
 */
export function createStrategy(data: StrategyForm) {
  return request.post('/content/strategies/', data)
}

/**
 * 更新攻略
 */
export function updateStrategy(id: number, data: Partial<StrategyForm>) {
  return request.patch(`/content/strategies/${id}/`, data)
}

/**
 * 删除攻略
 */
export function deleteStrategy(id: number) {
  return request.delete(`/content/strategies/${id}/`)
}

/**
 * 上传媒体资源
 */
export function uploadMedia(file: File, type: 'image' | 'video', strategy: number) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('media_type', type)
  formData.append('strategy', String(strategy))
  return request.post('/content/media/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除媒体资源
 */
export function deleteMedia(id: number) {
  return request.delete(`/content/media/${id}/`)
}

/**
 * 收藏/取消收藏攻略
 */
export function toggleStrategyCollection(strategyId: number) {
  return request.post(`/content/strategies/${strategyId}/collect/`)
}

/**
 * 点赞/取消点赞攻略
 */
export function toggleStrategyLike(strategyId: number) {
  return request.post(`/content/strategies/${strategyId}/like/`)
}

/**
 * 获取单篇攻略创作数据
 */
export function getStrategyStats(strategyId: number, params?: { days?: number }) {
  return request.get(`/content/strategies/${strategyId}/stats/`, { params })
}

/**
 * 获取攻略评论
 */
export function getStrategyComments(strategyId: number) {
  return request.get(`/content/strategies/${strategyId}/comments/`)
}

/**
 * 新增攻略评论
 */
export function createStrategyComment(strategyId: number, content: string) {
  return request.post(`/content/strategies/${strategyId}/comments/`, { content })
}

/**
 * 获取我的攻略
 */
export function getMyStrategies(params?: any) {
  return request.get('/content/strategies/mine/', { params })
}

/**
 * 获取待审核攻略（管理员/审核员）
 */
export function getPendingStrategies(params?: any) {
  return request.get('/content/strategies/pending/', { params })
}

/**
 * 审核攻略
 */
export function reviewStrategy(id: number, data: { status: string; feedback?: string }) {
  return request.post(`/content/strategies/${id}/review/`, data)
}

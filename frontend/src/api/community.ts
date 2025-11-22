/**
 * 社区相关 API
 */
import { request } from '@/utils/request'
import type { Post, PostForm, Comment, CommentForm } from '@/types/community'

/**
 * 获取动态列表
 */
export function getPostList(params?: any) {
  return request.get('/community/posts/', { params })
}

/**
 * 获取动态详情
 */
export function getPostDetail(id: number) {
  return request.get(`/community/posts/${id}/`)
}

/**
 * 发布动态
 */
export function createPost(data: PostForm) {
  return request.post('/community/posts/', data)
}

/**
 * 更新动态
 */
export function updatePost(id: number, data: Partial<PostForm>) {
  return request.patch(`/community/posts/${id}/`, data)
}

/**
 * 删除动态
 */
export function deletePost(id: number) {
  return request.delete(`/community/posts/${id}/`)
}

/**
 * 获取评论列表
 */
export function getComments(params: { post?: number; game?: number; strategy?: number; target?: string; target_id?: number; ordering?: string }) {
  return request.get('/community/comments/', { params })
}

/**
 * 发表评论
 */
export function createComment(data: CommentForm) {
  return request.post('/community/comments/', data)
}

/**
 * 删除评论
 */
export function deleteComment(id: number) {
  return request.delete(`/community/comments/${id}/`)
}

/**
 * 点赞/取消点赞
 */
export function toggleReaction(data: { content_type: string; object_id: number; reaction_type: string }) {
  return request.post('/community/reactions/', {
    target_type: data.content_type || data.target_type,
    target_id: data.object_id || data.target_id,
    type: data.reaction_type || data.type
  })
}

/**
 * 获取话题列表
 */
export function getTopics(params?: any) {
  return request.get('/community/topics/', { params })
}

/**
 * 获取话题列表（别名，用于列表页）
 */
export function getTopicList(params?: any) {
  return request.get('/community/topics/', { params })
}

export function getHotTopics() {
  return request.get('/community/topics/hot/')
}

export function createTopic(data: { name: string; description?: string }) {
  return request.post('/community/topics/', data)
}

/**
 * 关注/取消关注话题
 */
export function toggleTopicFollow(topicId: number) {
  return request.post(`/community/topics/${topicId}/follow/`)
}

/**
 * 举报内容
 */
export function reportContent(data: { content_type: string; object_id: number; reason: string }) {
  return request.post('/community/reports/', {
    target_type: data.content_type || data.target_type,
    target_id: data.object_id || data.target_id,
    reason: data.reason,
    content: data.reason
  })
}

/**
 * 提交反馈
 */
export function submitFeedback(data: { type: string; content: string }) {
  return request.post('/community/feedback/', data)
}

/**
 * 举报列表（管理员）
 */
export function getReports(params?: any) {
  return request.get('/community/reports/', { params })
}

export function updateReport(id: number, data: any) {
  return request.patch(`/community/reports/${id}/`, data)
}

export function deleteReport(id: number) {
  return request.delete(`/community/reports/${id}/`)
}

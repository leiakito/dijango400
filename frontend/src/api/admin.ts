/**
 * 管理员API接口
 */
import request from '@/utils/request'

// ==================== 用户管理 ====================

/**
 * 获取用户列表
 */
export function getUserList(params?: {
  page?: number
  page_size?: number
  role?: string
  status?: number
  search?: string
  ordering?: string
}) {
  return request({
    url: '/users/',
    method: 'get',
    params
  })
}

/**
 * 获取用户详情
 */
export function getUserDetail(id: number) {
  return request({
    url: `/users/${id}/`,
    method: 'get'
  })
}

/**
 * 更新用户信息
 */
export function updateUser(id: number, data: any) {
  return request({
    url: `/users/${id}/`,
    method: 'patch',
    data
  })
}

/**
 * 修改用户状态（封禁/解封）
 */
export function updateUserStatus(id: number, status: number, reason?: string) {
  return request({
    url: `/users/${id}/status/`,
    method: 'patch',
    data: { status, reason }
  })
}

/**
 * 修改用户角色
 */
export function updateUserRole(id: number, role: string) {
  return request({
    url: `/users/${id}/role/`,
    method: 'patch',
    data: { role }
  })
}

/**
 * 获取用户操作记录
 */
export function getUserOperations(id: number) {
  return request({
    url: `/users/${id}/operations/`,
    method: 'get'
  })
}

/**
 * 获取用户统计信息
 */
export function getUserStatistics() {
  return request({
    url: '/users/statistics/',
    method: 'get'
  })
}

/**
 * 获取所有用户操作记录
 */
export function getAllUserOperations(params?: {
  page?: number
  page_size?: number
  user?: number
}) {
  return request({
    url: '/users/operations/',
    method: 'get',
    params
  })
}

// ==================== 内容审核 ====================

/**
 * 获取待审核内容列表
 */
export function getReviewList(params?: {
  page?: number
  page_size?: number
  status?: string
  search?: string
  ordering?: string
}) {
  return request({
    url: '/content/review/',
    method: 'get',
    params
  })
}

/**
 * 获取审核统计信息
 */
export function getReviewStatistics() {
  return request({
    url: '/content/review/statistics/',
    method: 'get'
  })
}

/**
 * 通过审核
 */
export function approveContent(id: number) {
  return request({
    url: `/content/review/${id}/approve/`,
    method: 'post'
  })
}

/**
 * 拒绝审核
 */
export function rejectContent(id: number, reason: string) {
  return request({
    url: `/content/review/${id}/reject/`,
    method: 'post',
    data: { reason }
  })
}

/**
 * 获取内容审核历史
 */
export function getReviewHistory(id: number) {
  return request({
    url: `/content/review/${id}/review_history/`,
    method: 'get'
  })
}

// ==================== 系统配置 ====================

/**
 * 获取系统配置列表
 */
export function getSystemConfigs(params?: {
  page?: number
  page_size?: number
  search?: string
}) {
  return request({
    url: '/system/config/',
    method: 'get',
    params
  })
}

/**
 * 获取单个配置
 */
export function getSystemConfig(id: number) {
  return request({
    url: `/system/config/${id}/`,
    method: 'get'
  })
}

/**
 * 更新配置
 */
export function updateSystemConfig(id: number, data: any) {
  return request({
    url: `/system/config/${id}/`,
    method: 'patch',
    data
  })
}

/**
 * 批量更新配置
 */
export function batchUpdateConfigs(configs: any[]) {
  return request({
    url: '/system/config/batch_update/',
    method: 'post',
    data: { configs }
  })
}

/**
 * 获取系统日志
 */
export function getSystemLogs(params?: {
  page?: number
  page_size?: number
  level?: string
  module?: string
  search?: string
}) {
  return request({
    url: '/system/logs/',
    method: 'get',
    params
  })
}

/**
 * 获取日志统计
 */
export function getLogStatistics() {
  return request({
    url: '/system/logs/statistics/',
    method: 'get'
  })
}

/**
 * 清理旧日志
 */
export function cleanupLogs(days: number) {
  return request({
    url: '/system/logs/cleanup/',
    method: 'post',
    data: { days }
  })
}

/**
 * 获取备份任务列表
 */
export function getBackupJobs(params?: {
  page?: number
  page_size?: number
}) {
  return request({
    url: '/system/backup/',
    method: 'get',
    params
  })
}

/**
 * 创建备份任务
 */
export function createBackup() {
  return request({
    url: '/system/backup/create_backup/',
    method: 'post'
  })
}

/**
 * 获取系统健康状态
 */
export function getSystemHealth() {
  return request({
    url: '/system/health/',
    method: 'get'
  })
}


/**
 * 管理员相关类型定义
 */

// 用户角色
export enum UserRole {
  PLAYER = 'player',
  CREATOR = 'creator',
  PUBLISHER = 'publisher',
  ADMIN = 'admin'
}

// 用户状态
export enum UserStatus {
  BANNED = 0,
  NORMAL = 1
}

// 用户角色显示文本
export const UserRoleLabels = {
  [UserRole.PLAYER]: '普通玩家',
  [UserRole.CREATOR]: '内容创作者',
  [UserRole.PUBLISHER]: '发行商',
  [UserRole.ADMIN]: '系统管理员'
}

// 用户状态显示文本
export const UserStatusLabels = {
  [UserStatus.BANNED]: '封禁',
  [UserStatus.NORMAL]: '正常'
}

// 用户信息
export interface AdminUser {
  id: number
  username: string
  email?: string
  phone?: string
  role: UserRole
  status: UserStatus
  avatar?: string
  bio?: string
  register_time: string
  last_login_time?: string
}

// 用户操作记录
export interface UserOperation {
  id: number
  user: number
  user_name: string
  content: string
  ip_address?: string
  user_agent?: string
  created_at: string
}

// 用户统计信息
export interface UserStatistics {
  total: number
  by_role: Record<string, number>
  by_status: Record<string, number>
  recent_registrations: number
}

// 列表查询参数
export interface UserListParams {
  page?: number
  page_size?: number
  role?: UserRole
  status?: UserStatus
  search?: string
  ordering?: string
}


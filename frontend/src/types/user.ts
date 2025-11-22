/**
 * 用户相关类型定义
 */

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
  password_confirm: string
  role?: 'player' | 'creator' | 'publisher'
}

export interface UserInfo {
  id: number
  username: string
  email: string
  phone?: string
  avatar?: string
  role: 'player' | 'creator' | 'publisher' | 'admin'
  status: 'active' | 'banned' | 'deleted'
  register_time: string
  last_login?: string
  last_login_time?: string
  bio?: string
  verified: boolean
}

export interface UserProfile {
  username: string
  email: string
  avatar?: string
  bio?: string
  phone?: string
}

export interface UserOperation {
  id: number
  action: string
  target_type: string
  target_id: number
  description: string
  created_at: string
}


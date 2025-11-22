/**
 * 社区相关类型定义
 */
import type { UserInfo } from './user'
import type { Game } from './game'

export interface Post {
  id: number
  author: UserInfo
  game?: Game
  text: string
  images?: string[]
  mentions?: UserInfo[]
  topics?: Topic[]
  like_count: number
  comment_count: number
  is_deleted: boolean
  is_liked?: boolean
  created_at: string
  updated_at: string
}

export interface PostForm {
  game?: number
  text: string
  images?: string[]
  mentions?: number[]
  topics?: number[]
}

export interface Comment {
  id: number
  user: UserInfo
  game?: Game
  post?: number
  strategy?: number
  parent?: number
  content: string
  like_count: number
  is_deleted: boolean
  is_liked?: boolean
  created_at: string
  updated_at: string
}

export interface CommentForm {
  game?: number
  post?: number
  strategy?: number
  parent?: number
  content: string
}

export interface Reaction {
  id: number
  user: number
  target_type: string
  target_id: number
  type: 'like' | 'dislike'
  created_at: string
}

export interface Topic {
  id: number
  name: string
  description?: string
  cover_image?: string
  post_count: number
  heat: number
  is_followed?: boolean
  created_at: string
}

export interface Report {
  id: number
  reporter: UserInfo
  content_type: string
  object_id: number
  reason: string
  status: 'pending' | 'resolved' | 'rejected'
  handler?: UserInfo
  created_at: string
  resolved_at?: string
}

export interface Feedback {
  id: number
  user: UserInfo
  type: 'bug' | 'feature' | 'other'
  content: string
  status: 'pending' | 'processing' | 'resolved'
  created_at: string
}




















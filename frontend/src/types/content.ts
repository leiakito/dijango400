/**
 * 内容创作相关类型定义
 */
import type { UserInfo } from './user'
import type { Game } from './game'

export interface Strategy {
  id: number
  author: UserInfo
  game: Game
  title: string
  content: string
  cover_image?: string
  media_assets?: MediaAsset[]
  status: 'pending' | 'approved' | 'rejected'
  view_count: number
  like_count: number
  collect_count: number
  comment_count?: number
  is_collected?: boolean
  is_liked?: boolean
  publish_date?: string
  created_at: string
  updated_at: string
}

export interface StrategyForm {
  game: number
  title: string
  content: string
  cover_image?: string
  media_assets?: number[]
  status?: 'pending'
}

export interface MediaAsset {
  id: number
  strategy: number
  type: 'image' | 'video'
  url: string
  meta?: Record<string, any>
  order?: number
  created_at: string
}

export interface ContentReview {
  id: number
  strategy: Strategy
  reviewer: UserInfo
  status: 'approved' | 'rejected'
  feedback?: string
  reviewed_at: string
}

export interface StrategyCollection {
  id: number
  user: number
  strategy: Strategy
  created_at: string
}

export interface StrategyTrendPoint {
  date: string
  views: number
  likes: number
  collects: number
  comments?: number
}

export interface StrategyStats {
  id: number
  title: string
  view_count: number
  like_count: number
  collect_count: number
  comment_count: number
  trend: StrategyTrendPoint[]
}

export interface StrategyComment {
  id: number
  strategy: number
  user: UserInfo
  content: string
  created_at: string
  updated_at: string
}





















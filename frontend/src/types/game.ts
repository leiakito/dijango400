/**
 * 游戏相关类型定义
 */

export interface Tag {
  id: number
  name: string
  description?: string
}

export interface Publisher {
  id: number
  name: string
  logo?: string
  description?: string
  website?: string
  contact_info?: string
}

export interface Game {
  id: number
  name: string
  category: string
  publisher: number | Publisher
  publisher_name?: string
  tags?: Tag[]
  rating: number
  download_count: number
  follow_count: number
  review_count: number
  cover_image?: string | null
  name_en?: string | null
  heat_total: number
  release_date?: string | null
  is_collected?: boolean
}

export interface GameScreenshot {
  id: number
  image: string
  image_url?: string
  title?: string
  description?: string
  order?: number
}

export interface GameDetail extends Game {
  publisher: Publisher
  tags: Tag[]
  screenshots?: GameScreenshot[] | string[]
  description?: string
  heat_static?: number
  heat_dynamic?: number
  online_time?: string | null
  version?: string | null
  created_at?: string
  updated_at?: string
}

export interface GameQuery {
  page?: number
  page_size?: number
  search?: string
  category?: string
  ordering?: string
}

export interface SinglePlayerRanking {
  id?: number
  source: string
  rank: number
  name: string
  english_name?: string
  developer?: string
  publisher_name?: string
  genre?: string
  platforms?: string
  language?: string
  release_date?: string | null
  score?: number | null
  rating_count?: number
  tags?: string[]
  cover_url?: string
  detail_url?: string
  game?: number | Game | null
  fetched_at?: string
}

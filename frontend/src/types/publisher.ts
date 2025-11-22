import type { Publisher } from './game'

export interface PublisherAnalytics {
  publisher: Pick<Publisher, 'id' | 'name'>
  summary: {
    total_games: number
    total_downloads: number
    total_follows: number
    avg_rating: number
    avg_heat: number
  }
  games: Array<{
    name: string
    downloads: number
    follows: number
    rating: number
    heat: number
  }>
}

export interface HeatmapData {
  categories: string[]
  values: number[]
}

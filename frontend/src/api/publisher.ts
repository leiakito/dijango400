/**
 * 发行商相关 API
 */
import { request } from '@/utils/request'
import type { Game, GameDetail } from '@/types/game'
import type { PublisherAnalytics, HeatmapData } from '@/types/publisher'

export interface Paginated<T> {
  count?: number
  results: T[]
}

export function getPublisherAnalytics(params: { publisher: number | string }) {
  return request.get<PublisherAnalytics>('/analytics/publisher/', { params })
}

export function getHeatmapData() {
  return request.get<HeatmapData>('/analytics/heatmap/')
}

export function getPublisherGames(params?: any) {
  return request.get<Paginated<Game>>('/games/', { params })
}

export function updatePublisherGame(gameId: number, data: any) {
  return request.patch<GameDetail>(`/games/${gameId}/`, data)
}

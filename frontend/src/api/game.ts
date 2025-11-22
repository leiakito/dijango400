/**
 * 游戏相关 API
 */
import { request } from '@/utils/request'
import type { Game, GameDetail, GameQuery, SinglePlayerRanking } from '@/types/game'

/**
 * 获取游戏列表
 */
export function getGameList(params?: GameQuery) {
  return request.get('/games/', { params })
}

/**
 * 获取游戏详情
 */
export function getGameDetail(id: number): Promise<GameDetail> {
  return request.get(`/games/${id}/`)
}

/**
 * 获取推荐游戏（个性化推荐）
 */
export function getRecommendedGames(params?: any) {
  return request.get('/recommend/personal/', { params })
}

/**
 * 获取热门游戏
 */
export function getHotGames(params?: any) {
  return request.get('/recommend/hot/', { params })
}

/**
 * 获取最新游戏
 */
export function getLatestGames(params?: any) {
  return request.get('/games/', { params: { ...params, ordering: '-release_date' } })
}

/**
 * 收藏/取消收藏游戏
 */
export function toggleGameCollection(gameId: number) {
  return request.post(`/games/${gameId}/collect/`)
}

/**
 * 获取单机游戏排行榜（3DM）
 */
export function getSinglePlayerRanking(params?: { limit?: number; source?: string }): Promise<SinglePlayerRanking[]> {
  return request.get('/games/single-player-rankings/', { params })
}

/**
 * 获取用户收藏的游戏
 */
export function getUserCollections(params?: any) {
  return request.get('/games/collections/', { params })
}

/**
 * 获取游戏标签
 */
export function getGameTags() {
  return request.get('/games/tags/')
}

/**
 * 获取游戏发行商
 */
export function getPublishers() {
  return request.get('/games/publishers/')
}

/**
 * 搜索游戏
 */
export function searchGames(keyword: string, params?: any) {
  return request.get('/games/', { params: { ...params, search: keyword } })
}


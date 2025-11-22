/**
 * 游戏状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Game, Tag, Publisher } from '@/types/game'
import { getGameList, getGameTags, getPublishers } from '@/api/game'

export const useGameStore = defineStore('game', () => {
  // 状态
  const games = ref<Game[]>([])
  const currentGame = ref<Game | null>(null)
  const tags = ref<Tag[]>([])
  const publishers = ref<Publisher[]>([])
  const isLoading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 获取游戏列表
  const fetchGames = async (params?: any) => {
    try {
      isLoading.value = true
      const response = await getGameList({
        page: currentPage.value,
        page_size: pageSize.value,
        ...params
      })
      games.value = response.results
      total.value = response.count
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.message }
    } finally {
      isLoading.value = false
    }
  }

  // 获取标签列表
  const fetchTags = async () => {
    try {
      const data = await getGameTags()
      tags.value = data
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message }
    }
  }

  // 获取发行商列表
  const fetchPublishers = async () => {
    try {
      const data = await getPublishers()
      // 兼容分页结构
      publishers.value = Array.isArray(data) ? data : (data as any)?.results || []
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message }
    }
  }

  // 设置当前游戏
  const setCurrentGame = (game: Game) => {
    currentGame.value = game
  }

  // 清空当前游戏
  const clearCurrentGame = () => {
    currentGame.value = null
  }

  // 更新分页
  const updatePage = (page: number) => {
    currentPage.value = page
  }

  return {
    // 状态
    games,
    currentGame,
    tags,
    publishers,
    isLoading,
    total,
    currentPage,
    pageSize,
    // 方法
    fetchGames,
    fetchTags,
    fetchPublishers,
    setCurrentGame,
    clearCurrentGame,
    updatePage
  }
})




















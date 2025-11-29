<template>
  <div class="recommend-view">
    <el-page-header @back="router.back()" title="返回">
      <template #content>
        <h2>个性化推荐</h2>
      </template>
    </el-page-header>
    
    <el-divider />
    
    <!-- 推荐说明 -->
    <el-alert
      title="个性化推荐说明"
      type="info"
      :closable="false"
      style="margin-bottom: 20px"
    >
      基于您的兴趣标签和浏览历史，为您推荐最适合的游戏
    </el-alert>
    
    <!-- 推荐游戏列表 -->
    <section class="module-block" v-loading="loading">
      <el-row :gutter="20">
        <el-col
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          v-for="game in recommendedGames"
          :key="game.id"
        >
          <el-card :body-style="{ padding: '0px' }" class="game-card">
            <div class="game-cover-wrapper" @click="goToDetail(game.game.id)">
              <img 
                :src="getGameCoverUrl(game.game.cover_image)" 
                class="game-cover"
                @error="handleImageError"
              />
              <div class="recommend-score">
                <span>推荐度</span>
                <div class="score">{{ (game.score * 100).toFixed(0) }}%</div>
              </div>
            </div>
            
            <div class="game-info">
              <h4 @click="goToDetail(game.game.id)">{{ game.game.name }}</h4>
              
              <div class="game-meta">
                <el-tag size="small">{{ getCategoryLabel(game.game.category) }}</el-tag>
                <div class="rating">
                  <el-icon color="#f59e0b"><StarFilled /></el-icon>
                  <span>{{ game.game.rating }}</span>
                </div>
              </div>
              
              <div class="game-tags">
                <el-tag
                  v-for="tag in game.game.tags.slice(0, 3)"
                  :key="tag.id"
                  size="small"
                  effect="plain"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
              
              <div class="recommend-reason">
                <el-icon><InfoFilled /></el-icon>
                <span>{{ getRecommendReason(game) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 空状态提示 -->
      <el-empty 
        v-if="!loading && recommendedGames.length === 0" 
        description="暂无个性化推荐"
        :image-size="200"
      >
        <template #description>
          <div style="color: #909399; margin-bottom: 20px;">
            <p>为了获得更好的推荐体验，您可以：</p>
            <ul style="text-align: left; display: inline-block; margin-top: 10px;">
              <li>收藏感兴趣的游戏</li>
              <li>阅读并收藏游戏攻略</li>
              <li>在社区中点赞游戏相关的帖子</li>
            </ul>
          </div>
        </template>
        <el-button type="primary" @click="router.push('/games')">
          浏览游戏
        </el-button>
      </el-empty>
    </section>

    <!-- 最热榜单 -->
    <section class="module-block extra-block" v-loading="hotLoading">
      <div class="section-header">
        <div class="section-title">
          <el-icon><Sunny /></el-icon>
          <h3>最热游戏榜</h3>
        </div>
        <el-link type="primary" :underline="false" @click="router.push('/games/list')">
          查看更多
        </el-link>
      </div>
      <div class="compact-list">
        <div
          v-for="(game, index) in hotGames"
          :key="game.id"
          class="compact-game-card"
          @click="goToDetail(game.id)"
        >
          <span class="rank-badge">TOP {{ index + 1 }}</span>
          <div class="compact-cover">
            <img
              :src="getGameCoverUrl(game.cover_image)"
              :alt="game.name"
              @error="handleImageError"
            />
          </div>
          <div class="compact-info">
            <div class="compact-title" :title="game.name">{{ game.name }}</div>
            <div class="compact-meta">
              <el-tag size="small">{{ getCategoryLabel(game.category) }}</el-tag>
              <span class="stat">
                <el-icon><TrendCharts /></el-icon>
                {{ formatNumber(game.heat_total || 0) }}
              </span>
            </div>
            <div class="compact-stats">
              <span>
                <el-icon><StarFilled /></el-icon>
                {{ game.rating === null || game.rating === undefined ? 'N/A' : Number(game.rating).toFixed(1) }}
              </span>
              <span>
                <el-icon><InfoFilled /></el-icon>
                静态热度 {{ formatNumber(game.download_count || 0) }}
              </span>
            </div>
          </div>
        </div>
        <el-empty 
          v-if="!hotLoading && hotGames.length === 0" 
          description="暂无最热游戏数据"
        />
      </div>
    </section>

    <!-- 最新上架 -->
    <section class="module-block extra-block" v-loading="latestLoading">
      <div class="section-header">
        <div class="section-title">
          <el-icon><Clock /></el-icon>
          <h3>最新上架</h3>
        </div>
        <el-link type="primary" :underline="false" @click="router.push('/games/list')">
          查看更多
        </el-link>
      </div>
      <div class="compact-list">
        <div
          v-for="game in latestGames"
          :key="game.id"
          class="compact-game-card"
          @click="goToDetail(game.id)"
        >
          <div class="compact-cover">
            <img
              :src="getGameCoverUrl(game.cover_image)"
              :alt="game.name"
              @error="handleImageError"
            />
          </div>
          <div class="compact-info">
            <div class="compact-title" :title="game.name">{{ game.name }}</div>
            <div class="compact-meta">
              <el-tag size="small">{{ getCategoryLabel(game.category) }}</el-tag>
              <span class="stat">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(game.release_date) }}
              </span>
            </div>
            <div class="compact-stats">
              <span>
                <el-icon><StarFilled /></el-icon>
                {{ game.rating === null || game.rating === undefined ? 'N/A' : Number(game.rating).toFixed(1) }}
              </span>
              <span>
                <el-icon><TrendCharts /></el-icon>
                {{ formatNumber(game.follow_count || 0) }}
              </span>
            </div>
          </div>
        </div>
        <el-empty 
          v-if="!latestLoading && latestGames.length === 0" 
          description="暂无最新游戏数据"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRecommendedGames, getHotGames, getLatestGames } from '@/api/game'
import { StarFilled, InfoFilled, Sunny, Clock, TrendCharts, Calendar } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getGameCoverUrl, handleImageError } from '@/utils/image'
import type { Game, GameDetail } from '@/types/game'

interface PersonalizedRecommendation {
  id: number
  score: number
  game: GameDetail
  reason?: string
}

const router = useRouter()

const loading = ref(false)
const recommendedGames = ref<PersonalizedRecommendation[]>([])
const hotGames = ref<Game[]>([])
const latestGames = ref<Game[]>([])
const hotLoading = ref(false)
const latestLoading = ref(false)

const getCategoryLabel = (category: string) => {
  const map: Record<string, string> = {
    action: '动作',
    adventure: '冒险',
    rpg: '角色扮演',
    strategy: '策略',
    simulation: '模拟',
    sports: '体育'
  }
  return map[category] || category
}

const getRecommendReason = (item: PersonalizedRecommendation) => {
  if (item.score > 0.8) {
    return '强烈推荐！非常符合您的兴趣'
  } else if (item.score > 0.6) {
    return '推荐尝试，可能会喜欢'
  } else {
    return '或许您会感兴趣'
  }
}

const fetchRecommendations = async () => {
  loading.value = true
  
  try {
    const response = await getRecommendedGames({ top: 12 }) as { results?: PersonalizedRecommendation[] }
    recommendedGames.value = response.results || []
    
    if (recommendedGames.value.length === 0) {
      console.log('暂无推荐数据，建议先与游戏互动（收藏、点赞等）')
    }
  } catch (error) {
    console.error('获取推荐失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '获取推荐失败')
  } finally {
    loading.value = false
  }
}

const goToDetail = (id: number) => {
  router.push(`/games/${id}`)
}

const fetchHotList = async () => {
  hotLoading.value = true
  try {
    const response = await getHotGames({ top: 6 })
    hotGames.value = extractResults<Game>(response)
  } catch (error) {
    console.error('获取最热游戏失败:', error)
    hotGames.value = []
  } finally {
    hotLoading.value = false
  }
}

const fetchLatestList = async () => {
  latestLoading.value = true
  try {
    const response = await getLatestGames({ page_size: 6 })
    latestGames.value = extractResults<Game>(response)
  } catch (error) {
    console.error('获取最新游戏失败:', error)
    latestGames.value = []
  } finally {
    latestLoading.value = false
  }
}

const formatNumber = (num?: number | null) => {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const formatDate = (dateStr?: string | null) => {
  if (!dateStr) return '未公开'
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return '待定'
  return date.toLocaleDateString()
}

const extractResults = <T>(payload: unknown): T[] => {
  if (!payload) return []
  if (Array.isArray(payload)) return payload as T[]
  if (typeof payload === 'object' && payload !== null) {
    const listPayload = payload as { results?: unknown }
    if (Array.isArray(listPayload.results)) {
      return listPayload.results as T[]
    }
  }
  return []
}

onMounted(() => {
  fetchRecommendations()
  fetchHotList()
  fetchLatestList()
})
</script>

<style scoped lang="scss">
.recommend-view {
  .module-block {
    margin-bottom: 40px;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;

      h3 {
        margin: 0;
      }
    }
  }

  .game-card {
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    margin-bottom: 20px;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .game-cover-wrapper {
      position: relative;
      
      .game-cover {
        width: 100%;
        height: 240px;
        object-fit: cover;
      }
      
      .recommend-score {
        position: absolute;
        top: 12px;
        right: 12px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        text-align: center;
        
        span {
          font-size: 12px;
          display: block;
          margin-bottom: 4px;
        }
        
        .score {
          font-size: 20px;
          font-weight: bold;
          color: #67c23a;
        }
      }
    }
    
    .game-info {
      padding: 16px;
      
      h4 {
        margin: 0 0 12px;
        font-size: 16px;
        cursor: pointer;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        
        &:hover {
          color: var(--el-color-primary);
        }
      }
      
      .game-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        
        .rating {
          display: flex;
          align-items: center;
          gap: 4px;
          font-weight: bold;
        }
      }
      
      .game-tags {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
        min-height: 24px;
      }
      
      .recommend-reason {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px;
        background: var(--el-fill-color-light);
        border-radius: 4px;
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }
  }

  .extra-block {
    .compact-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }

    .compact-game-card {
      position: relative;
      display: flex;
      gap: 16px;
      padding: 16px;
      border: 1px solid var(--el-border-color-light);
      border-radius: 12px;
      background: var(--el-bg-color);
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
      }

      .rank-badge {
        position: absolute;
        top: 12px;
        left: 12px;
        font-size: 12px;
        font-weight: bold;
        color: var(--el-color-primary);
      }

      .compact-cover {
        width: 96px;
        height: 120px;
        border-radius: 8px;
        overflow: hidden;
        flex-shrink: 0;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }

      .compact-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 8px;

        .compact-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .compact-meta {
          display: flex;
          align-items: center;
          gap: 12px;

          .stat {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }

        .compact-stats {
          display: flex;
          gap: 16px;
          font-size: 13px;
          color: var(--el-text-color-regular);

          span {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }
  }
}
</style>







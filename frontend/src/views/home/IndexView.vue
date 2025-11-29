<template>
  <div class="home-view">
    <!-- 顶部横幅 -->
    <div class="page-banner">
      <div class="banner-overlay">
        <h1 class="banner-title">游戏推荐社区平台</h1>
        <p class="banner-subtitle">发现精彩游戏 · 分享游戏体验 · 交流游戏心得</p>
        <div class="banner-actions">
          <el-button type="primary" size="large" round @click="router.push('/games/list')">
            <el-icon><TrophyBase /></el-icon>
            探索游戏
          </el-button>
          <el-button size="large" round @click="router.push('/strategies/list')">
            <el-icon><Document /></el-icon>
            浏览攻略
          </el-button>
      
        </div>
      </div>
    </div>

    <!-- 热门游戏 -->
    <section class="content-section">
      <div class="section-header">
        <div class="section-title">
          <el-icon class="section-icon"><TrophyBase /></el-icon>
          <h2>热门游戏</h2>
        </div>
        <el-link type="primary" @click="router.push('/games/list')" :underline="false">
          查看更多 <el-icon><ArrowRight /></el-icon>
        </el-link>
      </div>

      <div class="games-container" v-loading="hotGamesLoading">
        <div class="games-grid">
          <div
            v-for="game in hotGames.slice(0, 8)"
            :key="game.id"
            class="game-card"
            @click="goToGameDetail(game.id)"
          >
            <!-- 游戏封面 -->
            <div class="game-cover">
              <img 
                :src="getGameCoverUrl(game.cover_image)" 
                :alt="game.name"
                @error="handleImageError"
              />
              <div class="game-overlay">
                <el-button type="primary" size="large" round>
                  <el-icon><View /></el-icon>
                  查看详情
                </el-button>
              </div>
              <!-- 评分标签 -->
              <div class="rating-badge">
                <el-icon><StarFilled /></el-icon>
                <span>{{ game.rating === null || game.rating === undefined ? 'N/A' : Number(game.rating).toFixed(1) }}</span>
              </div>
              <!-- 分类标签 -->
              <div class="category-badge">
                {{ getCategoryLabel(game.category) }}
              </div>
            </div>

            <!-- 游戏信息 -->
            <div class="game-info">
              <h3 class="game-title" :title="game.name">{{ game.name }}</h3>
              
              <!-- 统计信息 -->
              <div class="game-stats">
                <div class="stat-item">
                  <el-icon class="stat-icon"><Download /></el-icon>
                  <span>{{ formatNumber(game.download_count || 0) }}</span>
                </div>
                <div class="stat-item">
                  <el-icon class="stat-icon"><User /></el-icon>
                  <span>{{ formatNumber(game.follow_count || 0) }}</span>
                </div>
                <div class="stat-item">
                  <el-icon class="stat-icon"><TrendCharts /></el-icon>
                  <span>{{ formatNumber(game.heat_total || 0) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 最新攻略 -->
    <section class="content-section strategies-section">
      <div class="section-header">
        <div class="section-title">
          <el-icon class="section-icon"><Document /></el-icon>
          <h2>最新攻略</h2>
        </div>
        <el-link type="primary" @click="router.push('/strategies/list')" :underline="false">
          查看更多 <el-icon><ArrowRight /></el-icon>
        </el-link>
      </div>

      <div class="strategies-container" v-loading="strategiesLoading">
        <div class="strategies-grid">
          <div
            v-for="strategy in latestStrategies.slice(0, 6)"
            :key="strategy.id"
            class="strategy-card"
            @click="goToStrategyDetail(strategy.id)"
          >
            <div class="strategy-header">
              <el-avatar :src="strategy.author?.avatar" :size="48">
                {{ strategy.author?.username?.[0] || 'U' }}
              </el-avatar>
              <div class="author-info">
                <span class="author-name">{{ strategy.author?.username || '匿名用户' }}</span>
                <span class="publish-time">{{ formatTime(strategy.created_at) }}</span>
              </div>
            </div>

            <h3 class="strategy-title">{{ strategy.title }}</h3>

            <div class="strategy-footer">
              <el-tag size="small" v-if="strategy.game" type="info" effect="plain">
                {{ strategy.game.name }}
              </el-tag>
              <div class="strategy-stats">
                <span><el-icon><View /></el-icon> {{ formatNumber(strategy.view_count || 0) }}</span>
                <span><el-icon><Star /></el-icon> {{ formatNumber(strategy.like_count || 0) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 社区动态 -->
    <section class="content-section posts-section">
      <div class="section-header">
        <div class="section-title">
          <el-icon class="section-icon"><ChatDotRound /></el-icon>
          <h2>社区动态</h2>
        </div>
        <el-link type="primary" @click="router.push('/community/posts')" :underline="false">
          查看更多 <el-icon><ArrowRight /></el-icon>
        </el-link>
      </div>

      <div class="posts-container" v-loading="postsLoading">
        <div class="posts-list">
          <div
            v-for="post in recentPosts.slice(0, 5)"
            :key="post.id"
            class="post-card"
            @click="goToPostDetail(post.id)"
          >
            <div class="post-header">
              <el-avatar :src="post.author?.avatar" :size="48">
                {{ post.author?.username?.[0] || 'U' }}
              </el-avatar>
              <div class="post-author">
                <span class="author-name">{{ post.author?.username || '匿名用户' }}</span>
                <span class="post-time">{{ formatTime(post.created_at) }}</span>
              </div>
            </div>

            <div class="post-content">{{ post.text || '暂无内容' }}</div>

            <div class="post-footer">
              <div class="post-stats">
                <span><el-icon><Star /></el-icon> {{ formatNumber(post.like_count || 0) }}</span>
                <span><el-icon><ChatLineRound /></el-icon> {{ formatNumber(post.comment_count || 0) }}</span>
                <span><el-icon><Share /></el-icon> {{ formatNumber(post.share_count || 0) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getHotGames } from '@/api/game'
import { getStrategyList } from '@/api/content'
import { getPostList } from '@/api/community'
import { getGameCoverUrl, handleImageError, getPlaceholderImage } from '@/utils/image'
import { getCategoryLabel } from '@/constants/categories'
import {
  StarFilled,
  Star,
  Download,
  View,
  ChatDotRound,
  ChatLineRound,
  Document,
  TrophyBase,
  ArrowRight,
  User,
  TrendCharts,
  Share,
  RefreshRight
} from '@element-plus/icons-vue'

const router = useRouter()

const hotGames = ref<any[]>([])
const hotGamesLoading = ref(false)

const latestStrategies = ref<any[]>([])
const strategiesLoading = ref(false)

const recentPosts = ref<any[]>([])
const postsLoading = ref(false)
const refreshing = ref(false)

// 延迟辅助（用于模拟慢速抓取和二次加载）
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))


// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString()
}

// 获取热门游戏（可选慢速模式）
const fetchHotGames = async (slow = false) => {
  hotGamesLoading.value = true
  try {
    const response = await getHotGames({ top: 8 })
    hotGames.value = response.results || []
  } catch (error: any) {
    console.warn('获取热门游戏失败:', error)
    hotGames.value = []
  } finally {
    if (slow) await delay(2400)
    hotGamesLoading.value = false
  }
}

// 获取最新攻略（可选慢速模式）
const fetchLatestStrategies = async (slow = false) => {
  strategiesLoading.value = true
  try {
    const response = await getStrategyList({ page_size: 6, ordering: '-created_at' })
    latestStrategies.value = response.results || []
  } catch (error: any) {
    console.warn('获取最新攻略失败:', error)
    latestStrategies.value = []
  } finally {
    if (slow) await delay(2400)
    strategiesLoading.value = false
  }
}

// 获取最新动态（可选慢速模式）
const fetchRecentPosts = async (slow = false) => {
  postsLoading.value = true
  try {
    const response = await getPostList({ page_size: 5, ordering: '-created_at' })
    recentPosts.value = response.results || []
  } catch (error: any) {
    console.warn('获取社区动态失败:', error)
    recentPosts.value = []
  } finally {
    if (slow) await delay(2400)
    postsLoading.value = false
  }
}

// 跳转函数
const goToGameDetail = (id: number) => router.push(`/games/${id}`)
const goToStrategyDetail = (id: number) => router.push(`/strategies/${id}`)
const goToPostDetail = (id: number) => router.push(`/community/posts/${id}`)


onMounted(() => {
  // 首次加载依旧快速
  fetchHotGames(false)
  fetchLatestStrategies(false)
  fetchRecentPosts(false)
})
</script>

<style scoped lang="scss">
.home-view {
  // 顶部横幅
  .page-banner {
    margin: -20px -20px 32px;
    height: 400px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 0 0 24px 24px;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
    position: relative;

    &::before {
      content: '';
      position: absolute;
      inset: 0;
      background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff" fill-opacity="0.1" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom;
      background-size: cover;
    }

    .banner-overlay {
      position: relative;
      z-index: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: white;
      text-align: center;
      padding: 0 20px;

      .banner-title {
        font-size: 48px;
        font-weight: 900;
        margin: 0 0 16px;
        text-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        line-height: 1.2;
      }

      .banner-subtitle {
        font-size: 18px;
        margin: 0 0 32px;
        opacity: 0.95;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      }

      .banner-actions {
        display: flex;
        gap: 16px;

        :deep(.el-button) {
          font-size: 16px;
          padding: 16px 32px;
          font-weight: 600;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
          }
        }
        .spinning {
          animation: spin 0.8s linear infinite;
        }
      }
    }
  }

  // 内容区域
  .content-section {
    margin-bottom: 48px;

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;

      .section-title {
        display: flex;
        align-items: center;
        gap: 12px;

        .section-icon {
          font-size: 28px;
          color: var(--el-color-primary);
        }

        h2 {
          font-size: 28px;
          font-weight: 800;
          margin: 0;
          color: var(--el-text-color-primary);
        }
      }

      .el-link {
        font-size: 16px;
        font-weight: 600;
      }
    }

    // 游戏网格
    .games-container {
      .games-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 24px;

        .game-card {
          cursor: pointer;
          transition: all 0.3s ease;
          background: var(--el-bg-color);
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

          &:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);

            .game-cover img {
              transform: scale(1.1);
            }

            .game-overlay {
              opacity: 1;
            }
          }

          .game-cover {
            position: relative;
            height: 320px;
            overflow: hidden;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

            img {
              width: 100%;
              height: 100%;
              object-fit: cover;
              transition: transform 0.5s ease;
            }

            .game-overlay {
              position: absolute;
              inset: 0;
              background: rgba(0, 0, 0, 0.7);
              display: flex;
              align-items: center;
              justify-content: center;
              opacity: 0;
              transition: opacity 0.3s ease;

              :deep(.el-button) {
                font-weight: 600;
              }
            }

            .rating-badge {
              position: absolute;
              top: 12px;
              right: 12px;
              background: rgba(0, 0, 0, 0.85);
              backdrop-filter: blur(10px);
              color: #fbbf24;
              padding: 6px 12px;
              border-radius: 20px;
              font-size: 14px;
              font-weight: 700;
              display: flex;
              align-items: center;
              gap: 4px;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }

            .category-badge {
              position: absolute;
              top: 12px;
              left: 12px;
              background: rgba(102, 126, 234, 0.9);
              backdrop-filter: blur(10px);
              color: white;
              padding: 6px 12px;
              border-radius: 20px;
              font-size: 13px;
              font-weight: 600;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }
          }

          .game-info {
            padding: 16px;

            .game-title {
              font-size: 18px;
              font-weight: 700;
              margin: 0 0 12px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
              color: var(--el-text-color-primary);
            }

            .game-stats {
              display: flex;
              justify-content: space-between;
              align-items: center;

              .stat-item {
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 13px;
                color: var(--el-text-color-secondary);

                .stat-icon {
                  font-size: 16px;
                  color: var(--el-color-primary);
                }
              }
            }
          }
        }
      }
    }

    // 攻略网格
    .strategies-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 24px;

      .strategy-card {
        background: var(--el-bg-color);
        padding: 24px;
        border-radius: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }

        .strategy-header {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;

          .author-info {
            display: flex;
            flex-direction: column;
            justify-content: center;

            .author-name {
              font-weight: 700;
              font-size: 15px;
              color: var(--el-text-color-primary);
            }

            .publish-time {
              font-size: 13px;
              color: var(--el-text-color-secondary);
              margin-top: 2px;
            }
          }
        }

        .strategy-title {
          font-size: 18px;
          font-weight: 700;
          margin: 0 0 16px;
          line-height: 1.5;
          color: var(--el-text-color-primary);
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }

        .strategy-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .strategy-stats {
            display: flex;
            gap: 16px;
            font-size: 14px;
            color: var(--el-text-color-secondary);

            span {
              display: flex;
              align-items: center;
              gap: 4px;

              .el-icon {
                font-size: 16px;
              }
            }
          }
        }
      }
    }

    // 动态列表
    .posts-list {
      display: flex;
      flex-direction: column;
      gap: 16px;

      .post-card {
        background: var(--el-bg-color);
        padding: 24px;
        border-radius: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

        &:hover {
          transform: translateX(4px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }

        .post-header {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;

          .post-author {
            display: flex;
            flex-direction: column;
            justify-content: center;

            .author-name {
              font-weight: 700;
              font-size: 15px;
              color: var(--el-text-color-primary);
            }

            .post-time {
              font-size: 13px;
              color: var(--el-text-color-secondary);
              margin-top: 2px;
            }
          }
        }

        .post-content {
          margin-bottom: 16px;
          line-height: 1.6;
          color: var(--el-text-color-regular);
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
        }

        .post-footer {
          .post-stats {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: var(--el-text-color-secondary);

            span {
              display: flex;
              align-items: center;
              gap: 6px;

              .el-icon {
                font-size: 16px;
              }
            }
          }
        }
      }
    }
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 响应式
@media (max-width: 768px) {
  .home-view {
    .page-banner {
      height: 300px;
      margin: -20px -20px 24px;

      .banner-overlay {
        .banner-title {
          font-size: 32px;
        }

        .banner-subtitle {
          font-size: 14px;
        }

        .banner-actions {
          flex-direction: column;
          width: 100%;
          max-width: 300px;

          :deep(.el-button) {
            width: 100%;
          }
        }
      }
    }

    .content-section {
      margin-bottom: 32px;

      .section-header {
        .section-title {
          h2 {
            font-size: 24px;
          }
        }
      }

      .games-container .games-grid {
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 16px;

        .game-card .game-cover {
          height: 220px;
        }
      }

      .strategies-grid {
        grid-template-columns: 1fr;
      }
    }
  }
}
</style>

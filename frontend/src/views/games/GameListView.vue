<template>
  <div class="game-list-view">
    <!-- 顶部横幅 -->
    <div class="page-banner">
      <div class="banner-overlay">
        <h1 class="banner-title">探索游戏世界</h1>
        <p class="banner-subtitle">发现你的下一个最爱游戏</p>
      </div>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="filter-section">
      <el-card class="filter-card" shadow="never">
        <!-- 搜索框 -->
        <div class="search-bar">
          <el-input
            v-model="filters.search"
            placeholder="搜索游戏名称、描述..."
            size="large"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button :icon="Search" @click="handleSearch" type="primary">
                搜索
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- 筛选器 -->
        <div class="filters">
          <div class="filter-group">
            <label>分类</label>
            <el-radio-group v-model="filters.category" @change="handleSearch">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button 
                v-for="cat in GAME_CATEGORIES" 
                :key="cat.value" 
                :label="cat.value"
              >
                {{ cat.label }}
              </el-radio-button>
            </el-radio-group>
          </div>

          <div class="filter-group">
            <label>排序方式</label>
            <el-select 
              v-model="filters.ordering" 
              @change="handleSearch" 
              style="width: 200px"
              placeholder="请选择排序方式"
            >
              <el-option 
                v-for="option in orderingOptions"
                :key="option.value"
                :label="option.label" 
                :value="option.value"
              />
            </el-select>
          </div>
        </div>
      </el-card>
    </div>

    <div class="games-container" v-loading="gameStore.isLoading">
      <div class="games-grid">
        <div
          v-for="game in gameStore.games"
          :key="game.id"
          class="game-card"
          @click="goToDetail(game.id)"
        >
          <!-- 游戏封面 -->
            <div class="game-cover">
              <img 
                :src="getGameCoverUrl(game.cover_image)" 
                :alt="game.name"
                referrerpolicy="no-referrer"
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
              <span>{{ game.rating || 'N/A' }}</span>
            </div>
            <!-- 分类标签 -->
            <div class="category-badge">
              {{ getCategoryLabel(game.category) }}
            </div>
          </div>

          <!-- 游戏信息 -->
          <div class="game-info">
            <h3 class="game-title" :title="game.name">{{ game.name }}</h3>
            
            <!-- 标签 -->
            <div class="game-tags">
              <el-tag
                v-for="tag in game.tags?.slice(0, 3)"
                :key="tag.id"
                size="small"
                effect="plain"
                type="info"
              >
                {{ tag.name }}
              </el-tag>
            </div>

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

            <!-- 操作按钮 -->
            <div class="game-actions">
              <el-button
                :type="game.is_collected ? 'success' : 'primary'"
                :icon="game.is_collected ? StarFilled : Star"
                @click.stop="toggleCollection(game)"
                :loading="collectingIds.has(game.id)"
                round
              >
                {{ game.is_collected ? '已收藏' : '收藏' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!gameStore.isLoading && gameStore.games.length === 0"
        description="暂无游戏数据"
        :image-size="200"
      >
        <el-button type="primary" @click="handleReset">重置筛选</el-button>
      </el-empty>
    </div>

    <!-- 分页器 -->
    <div class="pagination-section" v-if="gameStore.total > 0">
      <el-pagination
        v-model:current-page="gameStore.currentPage"
        v-model:page-size="gameStore.pageSize"
        :total="gameStore.total"
        :page-sizes="[12, 24, 36, 48]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { useUserStore } from '@/stores/user'
import { toggleGameCollection } from '@/api/game'
import { GAME_CATEGORIES, getCategoryLabel } from '@/constants/categories'
import { getGameCoverUrl, handleImageError } from '@/utils/image'
import {
  Search,
  View,
  StarFilled,
  Star,
  Download,
  User,
  TrendCharts
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const gameStore = useGameStore()
const userStore = useUserStore()

// 排序选项
const orderingOptions = [
  { label: '🔥 热度排序', value: '-heat_total' },
  { label: '⭐ 评分最高', value: '-rating' },
  { label: '📥 下载最多', value: '-download_count' },
  { label: '🆕 最新发布', value: '-release_date' }
]

const filters = reactive({
  search: '',
  category: '',
  ordering: '-heat_total'
})

const collectingIds = ref(new Set<number>())

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

// 搜索
const handleSearch = () => {
  gameStore.updatePage(1)
  fetchGames()
}

// 重置
const handleReset = () => {
  filters.search = ''
  filters.category = ''
  filters.ordering = '-heat_total'
  handleSearch()
}

// 分页变化
const handlePageChange = (page: number) => {
  gameStore.updatePage(page)
  fetchGames()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 每页数量变化
const handleSizeChange = (size: number) => {
  gameStore.pageSize = size
  gameStore.updatePage(1)
  fetchGames()
}

// 获取游戏列表
const fetchGames = async () => {
  const params: any = {
    ordering: filters.ordering
  }

  if (filters.search) {
    params.search = filters.search
  }

  if (filters.category) {
    params.category = filters.category
  }

  await gameStore.fetchGames(params)
}

// 收藏/取消收藏
const toggleCollection = async (game: any) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }

  collectingIds.value.add(game.id)

  try {
    const response = await toggleGameCollection(game.id)
    // 使用后端返回的收藏状态
    game.is_collected = response.is_collected
    ElMessage.success(response.message || (response.is_collected ? '收藏成功' : '取消收藏成功'))
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    collectingIds.value.delete(game.id)
  }
}

// 跳转到详情
const goToDetail = (id: number) => {
  router.push(`/games/${id}`)
}

onMounted(async () => {
  // 从路由参数中获取搜索关键词
  if (route.query.search) {
    filters.search = route.query.search as string
  }

  // 获取标签列表
  await gameStore.fetchTags()

  // 获取游戏列表
  fetchGames()
})
</script>

<style scoped lang="scss">
.game-list-view {
  // 顶部横幅
  .page-banner {
    position: relative;
    height: 280px;
    margin: -20px -20px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="rgba(255,255,255,0.1)" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,149.3C960,160,1056,160,1152,138.7C1248,117,1344,75,1392,53.3L1440,32L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom;
      background-size: cover;
      opacity: 0.3;
    }

    .banner-overlay {
      position: relative;
      z-index: 1;
      text-align: center;
      color: white;

      .banner-title {
        font-size: 48px;
        font-weight: 800;
        margin: 0 0 16px;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
      }

      .banner-subtitle {
        font-size: 20px;
        opacity: 0.95;
        margin: 0;
        text-shadow: 0 1px 6px rgba(0, 0, 0, 0.2);
      }
    }
  }

  // 筛选区域
  .filter-section {
    margin-bottom: 24px;

    .filter-card {
      border-radius: 12px;
      border: none;

      .search-bar {
        margin-bottom: 20px;

        :deep(.el-input__wrapper) {
          border-radius: 24px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }
      }

      .filters {
        display: flex;
        flex-direction: column;
        gap: 20px;

        .filter-group {
          label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: var(--el-text-color-primary);
            margin-bottom: 12px;
          }

          :deep(.el-radio-button__inner) {
            border-radius: 20px;
            margin-right: 8px;
            padding: 8px 16px;
          }
        }
      }
    }
  }

  // 游戏容器
  .games-container {
    min-height: 600px;

    .games-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 24px;
      margin-bottom: 32px;

      .game-card {
        background: var(--el-bg-color);
        border-radius: 16px;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

        &:hover {
          transform: translateY(-8px);
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);

          .game-cover {
            img {
              transform: scale(1.1);
            }

            .game-overlay {
              opacity: 1;
            }
          }
        }

        // 游戏封面
        .game-cover {
          position: relative;
          width: 100%;
          height: 360px;
          overflow: hidden;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
          }

          // 悬停遮罩
          .game-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s;
          }

          // 评分标签
          .rating-badge {
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(10px);
            color: #fbbf24;
            padding: 6px 12px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 700;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);

            .el-icon {
              font-size: 16px;
            }
          }

          // 分类标签
          .category-badge {
            position: absolute;
            top: 12px;
            left: 12px;
            background: rgba(102, 126, 234, 0.95);
            backdrop-filter: blur(10px);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
          }
        }

        // 游戏信息
        .game-info {
          padding: 20px;

          .game-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--el-text-color-primary);
            margin: 0 0 12px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            line-height: 1.4;
          }

          .game-tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 16px;
            min-height: 24px;

            :deep(.el-tag) {
              border-radius: 12px;
              border: none;
              background: var(--el-fill-color-light);
            }
          }

          .game-stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 16px;
            padding: 12px;
            background: var(--el-fill-color-lighter);
            border-radius: 12px;

            .stat-item {
              display: flex;
              align-items: center;
              gap: 6px;
              font-size: 13px;
              font-weight: 600;
              color: var(--el-text-color-regular);

              .stat-icon {
                font-size: 16px;
                color: var(--el-color-primary);
              }
            }
          }

          .game-actions {
            .el-button {
              width: 100%;
              font-weight: 600;
            }
          }
        }
      }
    }
  }

  // 分页区域
  .pagination-section {
    display: flex;
    justify-content: center;
    padding: 32px 0;

    :deep(.el-pagination) {
      .btn-prev,
      .btn-next,
      .el-pager li {
        border-radius: 8px;
        font-weight: 600;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .game-list-view {
    .page-banner {
      height: 200px;
      margin: -20px -20px 20px;

      .banner-overlay {
        .banner-title {
          font-size: 32px;
        }

        .banner-subtitle {
          font-size: 16px;
        }
      }
    }

    .filter-section {
      .filter-card {
        .filters {
          .filter-group {
            :deep(.el-radio-group) {
              display: flex;
              flex-wrap: wrap;
              gap: 8px;
            }
          }
        }
      }
    }

    .games-container {
      .games-grid {
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 16px;
      }
    }
  }
}
</style>

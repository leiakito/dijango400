<template>
  <div class="game-detail-view" v-loading="loading">
    <template v-if="game">
      <!-- 游戏头部信息 -->
      <el-card class="game-header">
        <el-row :gutter="24">
          <el-col :xs="24" :sm="8">
            <img :src="game.cover_image" alt="游戏封面" class="game-cover" referrerpolicy="no-referrer" @error="handleImageError" />
          </el-col>
          
          <el-col :xs="24" :sm="16">
            <h1 class="game-name">{{ game.name }}</h1>
            <p v-if="game.name_en" class="game-name-en">{{ game.name_en }}</p>
            
            <div class="game-basic-info">
              <div class="info-item">
                <span class="label">评分:</span>
                <el-rate v-model="game.rating" disabled show-score text-color="#ff9900" />
              </div>
              
              <div class="info-item">
                <span class="label">分类:</span>
                <el-tag>{{ getCategoryLabel(game.category) }}</el-tag>
              </div>
              
              <div class="info-item">
                <span class="label">发行商:</span>
                <el-link type="primary">{{ game.publisher.name }}</el-link>
              </div>
              
              <div class="info-item">
                <span class="label">发布日期:</span>
                <span>{{ formatDate(game.release_date) }}</span>
              </div>
              
              <div class="info-item">
                <span class="label">标签:</span>
                <div class="tags">
                  <el-tag v-for="tag in game.tags" :key="tag.id" effect="plain">
                    {{ tag.name }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <div class="game-stats">
              <div class="stat-item">
                <el-icon><Download /></el-icon>
                <div class="stat-value">{{ formatNumber(game.download_count) }}</div>
                <div class="stat-label">下载量</div>
              </div>
              
              <div class="stat-item">
                <el-icon><User /></el-icon>
                <div class="stat-value">{{ formatNumber(game.follow_count) }}</div>
                <div class="stat-label">关注数</div>
              </div>
              
              <div class="stat-item">
                <el-icon><ChatDotRound /></el-icon>
                <div class="stat-value">{{ formatNumber(game.review_count) }}</div>
                <div class="stat-label">评价数</div>
              </div>
              
              <div class="stat-item">
                <el-icon><TrendCharts /></el-icon>
                <div class="stat-value">{{ formatNumber(game.heat_total) }}</div>
                <div class="stat-label">总热度</div>
              </div>
            </div>
            
            <div class="game-actions">
              <el-button
                type="primary"
                size="large"
                :icon="game.is_collected ? Star : StarFilled"
                @click="toggleCollection"
                :loading="collecting"
              >
                {{ game.is_collected ? '已收藏' : '收藏游戏' }}
              </el-button>
              
              <el-button size="large" :icon="Share">分享</el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 游戏详情标签页 -->
      <el-tabs v-model="activeTab" class="game-tabs">
        <!-- 游戏介绍 -->
        <el-tab-pane label="游戏介绍" name="description">
          <el-card>
            <div class="game-description" v-html="game.description"></div>
            
            <el-divider />
            
            <h3>游戏截图</h3>
            <div class="screenshots" v-if="game.screenshots && game.screenshots.length > 0">
              <el-image
                v-for="(screenshot, index) in game.screenshots"
                :key="index"
                :src="screenshot"
                :preview-src-list="game.screenshots"
                :initial-index="index"
                fit="cover"
                class="screenshot-img"
              />
            </div>
          </el-card>
        </el-tab-pane>
        
        <!-- 攻略 -->
        <el-tab-pane label="相关攻略" name="strategies">
          <el-card>
            <div v-loading="strategiesLoading">
              <div v-if="strategies.length > 0">
                <div
                  v-for="strategy in strategies"
                  :key="strategy.id"
                  class="strategy-item"
                  @click="goToStrategy(strategy.id)"
                >
                  <div class="strategy-header">
                    <el-avatar :src="strategy.author.avatar" :size="40">
                      {{ strategy.author.username[0] }}
                    </el-avatar>
                    <div class="author-info">
                      <div class="author-name">{{ strategy.author.username }}</div>
                      <div class="publish-time">{{ formatTime(strategy.created_at) }}</div>
                    </div>
                  </div>
                  
                  <h4 class="strategy-title">{{ strategy.title }}</h4>
                  <p class="strategy-excerpt">{{ (strategy.content || '').substring(0, 150) }}...</p>
                  
                  <div class="strategy-footer">
                    <span><el-icon><View /></el-icon> {{ strategy.view_count }}</span>
                    <span><el-icon><Star /></el-icon> {{ strategy.like_count }}</span>
                    <span><el-icon><ChatDotRound /></el-icon> {{ strategy.comment_count }}</span>
                  </div>
                </div>
              </div>
              
              <el-empty v-else description="暂无攻略" />
            </div>
          </el-card>
        </el-tab-pane>
        
        <!-- 热度分析 -->
        <el-tab-pane label="热度分析" name="analytics">
          <el-card>
            <div class="heat-charts">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-title">静态热度构成</div>
                  <div ref="staticHeatChartRef" style="height: 300px"></div>
                </el-col>
                
                <el-col :span="12">
                  <div class="chart-title">热度趋势</div>
                  <div ref="heatTrendChartRef" style="height: 300px"></div>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getGameDetail, toggleGameCollection } from '@/api/game'
import { getStrategyList } from '@/api/content'
import { getCategoryLabel } from '@/constants/categories'
import { getGameCoverUrl, handleImageError } from '@/utils/image'
import { Download, User, ChatDotRound, TrendCharts, Star, StarFilled, Share, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const game = ref<any>(null)
const loading = ref(false)
const collecting = ref(false)
const activeTab = ref('description')

const strategies = ref<any[]>([])
const strategiesLoading = ref(false)

const staticHeatChartRef = ref<HTMLElement>()
const heatTrendChartRef = ref<HTMLElement>()

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  return num.toString()
}

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

// 格式化时间
const formatTime = (time: string) => {
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

// 获取游戏详情
const fetchGameDetail = async () => {
  const gameId = Number(route.params.id)
  
  if (!gameId) {
    ElMessage.error('游戏 ID 无效')
    router.back()
    return
  }
  
  loading.value = true
  
  try {
    game.value = await getGameDetail(gameId)
  } catch (error: any) {
    ElMessage.error(error.message || '获取游戏详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 获取相关攻略
const fetchStrategies = async () => {
  if (!game.value) return
  
  strategiesLoading.value = true
  
  try {
    const response = await getStrategyList({
      game: game.value.id,
      page_size: 5,
      ordering: '-created_at'
    })
    strategies.value = response.results || []
  } catch (error: any) {
    console.error('获取攻略失败:', error)
  } finally {
    strategiesLoading.value = false
  }
}

// 收藏/取消收藏
const toggleCollection = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  if (!game.value) return
  
  collecting.value = true
  
  try {
    const response = await toggleGameCollection(game.value.id)
    // 使用后端返回的收藏状态
    game.value.is_collected = response.is_collected
    ElMessage.success(response.message || (response.is_collected ? '收藏成功' : '取消收藏成功'))
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    collecting.value = false
  }
}

// 跳转到攻略详情
const goToStrategy = (id: number) => {
  router.push(`/strategies/${id}`)
}

// 初始化静态热度图表
const initStaticHeatChart = () => {
  if (!staticHeatChartRef.value || !game.value) return
  
  const chart = echarts.init(staticHeatChartRef.value)
  
  chart.setOption({
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '70%',
        data: [
          { value: game.value.download_count * 0.5, name: '下载量' },
          { value: game.value.follow_count * 0.3, name: '关注数' },
          { value: game.value.review_count * 0.2, name: '评价数' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  })
}

// 初始化热度趋势图表
const initHeatTrendChart = () => {
  if (!heatTrendChartRef.value || !game.value) return
  
  const chart = echarts.init(heatTrendChartRef.value)
  
  // 模拟趋势数据
  const dates = Array.from({ length: 30 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - 29 + i)
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  })
  
  chart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '总热度',
        type: 'line',
        data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 1000 + game.value.heat_total * 0.8)),
        smooth: true,
        areaStyle: {
          opacity: 0.3
        }
      }
    ]
  })
}

onMounted(async () => {
  await fetchGameDetail()
  await fetchStrategies()
  
  await nextTick()
  initStaticHeatChart()
  initHeatTrendChart()
})
</script>

<style scoped lang="scss">
.game-detail-view {
  .game-header {
    margin-bottom: 20px;
    
    .game-cover {
      width: 100%;
      border-radius: 8px;
    }
    
    .game-name {
      margin: 0 0 8px;
      font-size: 32px;
    }
    
    .game-name-en {
      color: var(--el-text-color-secondary);
      margin-bottom: 16px;
    }
    
    .game-basic-info {
      margin-bottom: 24px;
      
      .info-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        
        .label {
          font-weight: bold;
          min-width: 80px;
        }
        
        .tags {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
      }
    }
    
    .game-stats {
      display: flex;
      gap: 24px;
      margin-bottom: 24px;
      padding: 16px;
      background: var(--el-fill-color-light);
      border-radius: 8px;
      
      .stat-item {
        flex: 1;
        text-align: center;
        
        .el-icon {
          font-size: 24px;
          color: var(--el-color-primary);
        }
        
        .stat-value {
          font-size: 24px;
          font-weight: bold;
          margin: 8px 0 4px;
        }
        
        .stat-label {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }
    
    .game-actions {
      display: flex;
      gap: 16px;
    }
  }
  
  .game-tabs {
    .game-description {
      line-height: 1.8;
      font-size: 14px;
    }
    
    .screenshots {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;
      
      .screenshot-img {
        width: 100%;
        height: 150px;
        border-radius: 8px;
        cursor: pointer;
      }
    }
    
    .strategy-item {
      padding: 16px;
      border-bottom: 1px solid var(--el-border-color);
      cursor: pointer;
      transition: background-color 0.3s;
      
      &:hover {
        background-color: var(--el-fill-color-light);
      }
      
      &:last-child {
        border-bottom: none;
      }
      
      .strategy-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        
        .author-info {
          .author-name {
            font-weight: bold;
          }
          
          .publish-time {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
      }
      
      .strategy-title {
        margin: 0 0 8px;
        font-size: 16px;
      }
      
      .strategy-excerpt {
        color: var(--el-text-color-secondary);
        line-height: 1.6;
        margin-bottom: 12px;
      }
      
      .strategy-footer {
        display: flex;
        gap: 16px;
        font-size: 14px;
        color: var(--el-text-color-secondary);
        
        span {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
    
    .heat-charts {
      .chart-title {
        text-align: center;
        font-weight: bold;
        margin-bottom: 16px;
      }
    }
  }
}
</style>








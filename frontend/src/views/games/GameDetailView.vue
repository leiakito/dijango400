<template>
  <div class="game-detail-view" v-loading="loading">
    <template v-if="game">
      <!-- 游戏头部信息 -->
      <el-card class="game-header">
        <el-row :gutter="24">
          <el-col :xs="24" :sm="8">
            <img 
              :src="game.cover_image" 
              alt="游戏封面" 
              class="game-cover" 
              referrerpolicy="no-referrer" 
              @error="(e) => handleImageError(e)"
              loading="lazy"
            />
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
                <el-icon><StarFilled /></el-icon>
                <div class="stat-value">{{ formatNumber(game.like_count || 0) }}</div>
                <div class="stat-label">点赞数</div>
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
              
              <el-button
                size="large"
                :type="game.is_liked ? 'success' : 'default'"
                :icon="game.is_liked ? StarFilled : Star"
                @click="toggleLike"
                :loading="liking"
              >
                {{ game.is_liked ? '已点赞' : '点赞游戏' }} ({{ formatNumber(game.like_count || 0) }})
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
                v-for="(screenshot, index) in screenshotUrls"
                :key="index"
                :src="screenshot.image_url"
                :preview-src-list="screenshotUrls.map(s => s.image_url)"
                :initial-index="index"
                fit="cover"
                class="screenshot-img"
              />
            </div>
            <el-empty v-else description="暂无截图" />
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
        <!-- 角色评论 -->
        <el-tab-pane label="角色评论" name="comments">
          <el-card class="comment-card">
            <div class="comment-header">
              <div class="comment-title">
                <el-icon><ChatDotRound /></el-icon>
                <h3>角色评论区</h3>
              </div>
              <div class="comment-controls">
                <el-select
                  v-model="commentOrdering"
                  placeholder="排序"
                  size="small"
                  @change="fetchComments"
                  style="width: 140px"
                >
                  <el-option label="按时间" value="time" />
                  <el-option label="按热度" value="hot" />
                </el-select>
                <el-radio-group v-model="commentRoleFilter" size="small">
                  <el-radio-button label="all">全部</el-radio-button>
                  <el-radio-button label="player">玩家</el-radio-button>
                  <el-radio-button label="creator">创作者</el-radio-button>
                  <el-radio-button label="publisher">发行商</el-radio-button>
                  <el-radio-button label="admin">管理员</el-radio-button>
                </el-radio-group>
              </div>
            </div>
            
            <div class="comment-editor" v-if="userStore.isLoggedIn">
              <div class="editor-meta">
                以 <strong>{{ getRoleLabel(userStore.userInfo?.role) }}</strong> 身份发表评论
              </div>
              <el-input
                ref="commentInputRef"
                v-model="commentContent"
                type="textarea"
                :rows="4"
                maxlength="500"
                show-word-limit
                placeholder="分享您的体验或专业观点..."
              />
              <div class="reply-hint" v-if="replyTo">
                回复 <strong>{{ replyTo.user?.username }}</strong>
                <el-button text type="primary" size="small" @click="clearReply">取消</el-button>
              </div>
              <div class="comment-actions">
                <el-button type="primary" :loading="commentSubmitting" @click="submitComment">
                  发布评论
                </el-button>
              </div>
            </div>
            <div v-else class="login-tip">
              <el-button type="primary" @click="router.push('/auth/login')">登录后发表评论</el-button>
            </div>
            
            <el-skeleton :loading="commentLoading" animated :rows="4">
              <div v-if="filteredComments.length === 0" class="empty">
                当前筛选下暂无评论，成为第一位分享观点的{{ commentRoleFilter === 'all' ? '用户' : getRoleLabel(commentRoleFilter) }}吧！
              </div>
              <div v-else class="comment-list">
                <CommentNode
                  v-for="item in filteredComments"
                  :key="item.id"
                  :comment="item"
                  :depth="1"
                  :current-user-id="userStore.userInfo?.id"
                  :is-admin="userStore.isAdmin"
                  @reply="setReply"
                  @delete="deleteCommentItem"
                />
              </div>
            </el-skeleton>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getGameDetail, toggleGameCollection, getGameScreenshots } from '@/api/game'
import { getStrategyList } from '@/api/content'
import { getComments, createComment, deleteComment as deleteCommentApi, toggleReaction } from '@/api/community'
import { getCategoryLabel } from '@/constants/categories'
import { handleImageError } from '@/utils/image'
import { Download, User, ChatDotRound, TrendCharts, Star, StarFilled, Share, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'
import CommentNode from '@/components/CommentNode.vue'
import type { Comment } from '@/types/community'
import type { GameDetail } from '@/types/game'
import type { Strategy } from '@/types/content'

type RoleFilter = 'all' | 'player' | 'creator' | 'publisher' | 'admin'
type WithResults<T> = { results?: T[]; count?: number }

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const game = ref<GameDetail | null>(null)
const loading = ref(false)
const collecting = ref(false)
const activeTab = ref('description')

const strategies = ref<Strategy[]>([])
const strategiesLoading = ref(false)
const screenshotUrls = ref<any[]>([])

const staticHeatChartRef = ref<HTMLElement>()
const heatTrendChartRef = ref<HTMLElement>()

const comments = ref<Comment[]>([])
const commentLoading = ref(false)
const commentSubmitting = ref(false)
const commentsLoaded = ref(false)
const commentContent = ref('')
const commentOrdering = ref<'time' | 'hot'>('time')
const commentRoleFilter = ref<RoleFilter>('all')
const replyTo = ref<Comment | null>(null)
const commentInputRef = ref<{ focus?: () => void } | null>(null)
const liking = ref(false)

const filteredComments = computed(() => {
  if (commentRoleFilter.value === 'all') {
    return comments.value
  }
  return filterCommentTree(comments.value, commentRoleFilter.value)
})

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

const roleLabelMap: Record<string, string> = {
  player: '玩家',
  creator: '创作者',
  publisher: '发行商',
  admin: '管理员'
}

const getRoleLabel = (role?: string | null) => {
  if (!role) return '用户'
  return roleLabelMap[role] || '用户'
}

const filterCommentTree = (nodes: Comment[], role: RoleFilter): Comment[] => {
  return nodes.reduce<Comment[]>((acc, item) => {
    const replies = item.replies ? filterCommentTree(item.replies, role) : []
    const matches = item.user?.role === role
    if (matches || replies.length > 0) {
      acc.push({
        ...item,
        replies
      })
    }
    return acc
  }, [])
}

const resolveErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback
  }
  return fallback
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
  } catch (error: unknown) {
    ElMessage.error(resolveErrorMessage(error, '获取游戏详情失败'))
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
    }) as WithResults<Strategy> | Strategy[]
    strategies.value = extractResults<Strategy>(response)
  } catch (error: unknown) {
    console.error('获取攻略失败:', error)
  } finally {
    strategiesLoading.value = false
  }
}

// 获取游戏截图
const fetchScreenshots = async () => {
  if (!game.value) return
  
  try {
    const response = await getGameScreenshots(game.value.id)
    screenshotUrls.value = Array.isArray(response) ? response : response.results || []
  } catch (error: unknown) {
    console.error('获取截图失败:', error)
  }
}

const extractResults = <T>(payload: WithResults<T> | T[] | undefined): T[] => {
  if (!payload) return []
  if (Array.isArray(payload)) return payload
  return Array.isArray(payload.results) ? payload.results : []
}

const fetchComments = async () => {
  if (!game.value) return
  commentLoading.value = true
  try {
    const response = await getComments({
      target: 'game',
      target_id: game.value.id,
      ordering: commentOrdering.value === 'hot' ? 'hot' : undefined
    }) as WithResults<Comment> | Comment[]
    const list = extractResults<Comment>(response)
    comments.value = list
    commentsLoaded.value = true
    if (game.value) {
      const total = Array.isArray(response)
        ? response.length
        : typeof response.count === 'number'
          ? response.count
          : list.length
      game.value.review_count = total
    }
  } catch (error: unknown) {
    ElMessage.error(resolveErrorMessage(error, '获取评论失败'))
  } finally {
    commentLoading.value = false
  }
}

const submitComment = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  if (!commentContent.value.trim() || !game.value) {
    ElMessage.warning('请输入评论内容')
    return
  }
  commentSubmitting.value = true
  try {
    await createComment({
      content: commentContent.value.trim(),
      target: 'game',
      target_id: game.value.id,
      parent: replyTo.value?.id
    })
    commentContent.value = ''
    replyTo.value = null
    ElMessage.success('评论成功')
    if (game.value) {
      game.value.review_count = (game.value.review_count || 0) + 1
    }
    fetchComments()
  } catch (error: unknown) {
    ElMessage.error(resolveErrorMessage(error, '评论失败'))
  } finally {
    commentSubmitting.value = false
  }
}

const setReply = (comment: Comment) => {
  replyTo.value = comment
  nextTick(() => {
    commentInputRef.value?.focus?.()
  })
}

const clearReply = () => {
  replyTo.value = null
}

const deleteCommentItem = async (comment: Comment) => {
  try {
    await deleteCommentApi(comment.id)
    ElMessage.success('已删除')
    if (game.value && game.value.review_count) {
      game.value.review_count = Math.max(0, game.value.review_count - 1)
    }
    fetchComments()
  } catch (error: unknown) {
    ElMessage.error(resolveErrorMessage(error, '删除失败'))
  }
}

const toggleLike = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  if (!game.value || liking.value) return
  liking.value = true
  try {
    const response = await toggleReaction({
      content_type: 'game',
      object_id: game.value.id,
      reaction_type: 'like'
    })
    const result = response as { is_liked?: boolean; like_count?: number; message?: string }
    if (typeof result.is_liked === 'boolean') {
      game.value.is_liked = result.is_liked
    }
    if (typeof result.like_count === 'number') {
      game.value.like_count = result.like_count
    } else if (game.value.is_liked) {
      game.value.like_count = (game.value.like_count || 0) + 1
    } else if (game.value.like_count) {
      game.value.like_count = Math.max(0, game.value.like_count - 1)
    }
    ElMessage.success(result.message || (game.value.is_liked ? '点赞成功' : '已取消点赞'))
  } catch (error: unknown) {
    ElMessage.error(resolveErrorMessage(error, '操作失败'))
  } finally {
    liking.value = false
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
    const response = await toggleGameCollection(game.value.id) as { is_collected: boolean; message?: string }
    // 使用后端返回的收藏状态
    game.value.is_collected = response.is_collected
    ElMessage.success(response.message || (response.is_collected ? '收藏成功' : '取消收藏成功'))
  } catch (error: unknown) {
    ElMessage.error(resolveErrorMessage(error, '操作失败'))
  } finally {
    collecting.value = false
  }
}

// 跳转到攻略详情
const goToStrategy = (id: number) => {
  router.push(`/strategies/${id}`)
}

watch(activeTab, (tab) => {
  if (tab === 'comments' && !commentsLoaded.value) {
    fetchComments()
  }
})

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
  await fetchScreenshots()
  
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

    .comment-card {
      .comment-header {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 16px;

        .comment-title {
          display: flex;
          align-items: center;
          gap: 8px;

          h3 {
            margin: 0;
          }
        }

        .comment-controls {
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
          justify-content: flex-end;
        }
      }

      .comment-editor {
        margin-bottom: 20px;
        .editor-meta {
          margin-bottom: 8px;
          color: var(--el-text-color-secondary);
        }
      }

      .reply-hint {
        margin: 8px 0;
        font-size: 13px;
        color: var(--el-text-color-secondary);
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .comment-actions {
        display: flex;
        justify-content: flex-end;
        margin-top: 12px;
      }

      .login-tip {
        text-align: center;
        margin: 20px 0;
      }

      .comment-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .empty {
        text-align: center;
        color: var(--el-text-color-secondary);
        padding: 24px 0;
      }
    }
  }
}
</style>

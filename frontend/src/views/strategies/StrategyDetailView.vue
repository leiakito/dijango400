<template>
  <div class="strategy-detail-view" v-loading="loading">
    <section v-if="strategy" class="hero" :style="heroStyle">
      <div class="hero-mask"></div>
      <div class="hero-content">
        <el-breadcrumb separator="/" class="hero-crumbs">
          <el-breadcrumb-item :to="{ path: '/strategies/list' }">攻略广场</el-breadcrumb-item>
          <el-breadcrumb-item v-if="strategy.game">{{ strategy.game.name }}</el-breadcrumb-item>
          <el-breadcrumb-item>正文</el-breadcrumb-item>
        </el-breadcrumb>

        <div class="hero-main">
          <div class="tags-row">
            <el-tag v-if="statusLabel" type="warning" effect="dark" round>{{ statusLabel }}</el-tag>
            <el-tag v-if="strategy.game" type="primary" effect="light" round>{{ strategy.game.name }}</el-tag>
          </div>
          <h1 class="hero-title">{{ strategy.title }}</h1>
          
          <div class="hero-meta">
            <div class="author-info">
              <el-avatar :src="strategy.author?.avatar" :size="40" class="avatar-hover">
                {{ strategy.author?.username?.[0]?.toUpperCase() || 'U' }}
              </el-avatar>
              <div class="text-info">
                <span class="name">{{ strategy.author?.username || '匿名玩家' }}</span>
                <span class="date">{{ formatTime(strategy.created_at) }}</span>
              </div>
            </div>
            
            <div class="stats-row">
              <span title="阅读量"><el-icon><View /></el-icon> {{ formatNumber(strategy.view_count) }}</span>
              <span title="点赞数"><el-icon><Star /></el-icon> {{ formatNumber(strategy.like_count) }}</span>
              <span title="收藏数"><el-icon><Collection /></el-icon> {{ formatNumber(strategy.collect_count) }}</span>
              <span title="评论数"><el-icon><ChatLineRound /></el-icon> {{ formatNumber(strategy.comment_count || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="main-container" v-if="strategy">
      <main class="content-column">
        <el-alert
          v-if="strategy.status === 'rejected'"
          type="error"
          show-icon
          :title="`审核未通过: ${latestRejectReason || '内容不合规'}`"
          class="status-alert"
        />
        <el-alert
          v-else-if="strategy.status === 'pending'"
          type="warning"
          show-icon
          title="当前内容正在审核中，仅作者可见"
          class="status-alert"
        />

        <el-card v-if="isOwn" class="creator-stats-card" shadow="never">
          <div class="creator-stats-header">
            <div>
              <p class="eyebrow">创作者数据面板</p>
              <h3>攻略表现</h3>
            </div>
            <el-tag effect="plain" type="success">仅作者可见</el-tag>
          </div>
          <el-row :gutter="16" class="metrics-row">
            <el-col :xs="12" :sm="6" :md="6">
              <div class="metric">
                <span class="label">阅读量</span>
                <div class="value">{{ stats?.view_count ?? strategy.view_count }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6">
              <div class="metric">
                <span class="label">点赞数</span>
                <div class="value">{{ stats?.like_count ?? strategy.like_count }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6">
              <div class="metric">
                <span class="label">收藏数</span>
                <div class="value">{{ stats?.collect_count ?? strategy.collect_count }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6">
              <div class="metric">
                <span class="label">评论数</span>
                <div class="value">{{ stats?.comment_count ?? strategy.comment_count ?? 0 }}</div>
              </div>
            </el-col>
          </el-row>
          <div class="trend-chart-wrapper" v-loading="statsLoading">
            <div ref="trendChartRef" class="trend-chart"></div>
          </div>
        </el-card>

        <el-card class="article-card" shadow="never">
          <div class="article-content typography" v-html="strategy.content"></div>

          <div v-if="images.length" class="media-block">
            <h3 class="section-title">📸 精彩截图</h3>
            <div class="gallery-grid">
              <el-image
                v-for="img in images"
                :key="img.id"
                :src="img.url"
                fit="cover"
                :preview-src-list="images.map((i) => i.url)"
                loading="lazy"
                class="gallery-item"
              />
            </div>
          </div>

          <div v-if="videos.length" class="media-block">
            <h3 class="section-title">🎬 演示视频</h3>
            <div class="video-grid">
              <div v-for="video in videos" :key="video.id" class="video-wrapper">
                <video controls :src="video.url" preload="metadata"></video>
              </div>
            </div>
          </div>
          
          <div class="comments-section">
            <h3 class="section-title">💬 评论区</h3>
            <div class="comment-form" v-if="isLoggedIn">
              <el-input
                v-model="commentContent"
                type="textarea"
                :rows="3"
                maxlength="500"
                show-word-limit
                placeholder="分享你的看法..."
              />
              <div class="comment-actions">
                <el-button type="primary" @click="submitComment">发表评论</el-button>
              </div>
            </div>
            <div v-else class="comment-login-tip">
              <el-button type="primary" @click="router.push('/login')">登录后参与讨论</el-button>
            </div>
            
            <el-skeleton :loading="commentsLoading" animated :rows="3">
              <div class="comment-list">
                <div v-if="comments.length === 0" class="comment-empty">还没有评论，来抢沙发吧～</div>
                <div v-for="item in comments" :key="item.id" class="comment-item">
                  <el-avatar :src="item.user?.avatar" :size="36">
                    {{ item.user?.username?.[0] || 'U' }}
                  </el-avatar>
                  <div class="comment-body">
                    <div class="comment-meta">
                      <span class="comment-name">{{ item.user?.username }}</span>
                      <span class="comment-time">{{ formatTime(item.created_at) }}</span>
                    </div>
                    <div class="comment-content">{{ item.content }}</div>
                  </div>
                </div>
              </div>
            </el-skeleton>
          </div>
          
          <div class="article-footer">
             <span class="copyright">© 著作权归作者所有</span>
          </div>
        </el-card>
      </main>

      <aside class="sidebar-column">
        <el-affix :offset="80">
          <div class="sidebar-stack">
            <el-card class="author-card" shadow="hover">
              <div class="author-header">
                <el-avatar :src="strategy.author?.avatar" :size="64">
                  {{ strategy.author?.username?.[0] || 'U' }}
                </el-avatar>
                <div class="author-details">
                  <div class="name">{{ strategy.author?.username || '匿名用户' }}</div>
                  <div class="bio" :title="strategy.author?.bio">{{ strategy.author?.bio || '这个作者很懒，没有写简介' }}</div>
                </div>
              </div>
              <div class="author-actions">
                 <el-button round size="small">关注作者</el-button>
                 <el-button round size="small">私信</el-button>
              </div>
            </el-card>

            <el-card class="action-card desktop-only" shadow="hover">
              <div class="action-grid">
                <div class="action-item" @click="doLike" :class="{ active: strategy.is_liked }">
                  <div class="icon-box">
                    <el-icon v-if="strategy.is_liked"><StarFilled /></el-icon>
                    <el-icon v-else><Star /></el-icon>
                  </div>
                  <span>{{ strategy.is_liked ? '已赞' : '点赞' }} {{ formatNumber(strategy.like_count) }}</span>
                </div>
                <div class="action-item" @click="doCollect" :class="{ active: strategy.is_collected }">
                   <div class="icon-box">
                    <el-icon v-if="strategy.is_collected"><CollectionTag /></el-icon>
                    <el-icon v-else><Collection /></el-icon>
                  </div>
                  <span>{{ strategy.is_collected ? '已藏' : '收藏' }} {{ formatNumber(strategy.collect_count) }}</span>
                </div>
              </div>
              <div class="divider"></div>
              <div class="manage-actions" v-if="isOwn">
                <el-button type="primary" text bg block :icon="EditPen" @click="goToEdit">编辑攻略</el-button>
              </div>
            </el-card>
            
            <el-card class="toc-card desktop-only" shadow="never">
               <div class="toc-header">目录导读</div>
               <div class="toc-list">
                 <div
                   v-for="item in tocItems"
                   :key="item.id"
                   :class="['toc-item', { active: activeToc === item.id }]"
                   @click="scrollToAnchor(item.id)"
                 >
                   {{ item.text }}
                 </div>
               </div>
             </el-card>
          </div>
        </el-affix>
      </aside>
    </div>

    <div class="mobile-action-bar mobile-only" v-if="strategy">
      <div class="input-fake">
        <el-icon><ChatLineRound /></el-icon> 说点什么...
      </div>
      <div class="actions">
        <div class="icon-btn" @click="doLike" :class="{ active: strategy.is_liked }">
           <el-icon><StarFilled v-if="strategy.is_liked"/><Star v-else/></el-icon>
           <span class="count">{{ formatNumber(strategy.like_count) }}</span>
        </div>
        <div class="icon-btn" @click="doCollect" :class="{ active: strategy.is_collected }">
           <el-icon><CollectionTag v-if="strategy.is_collected"/><Collection v-else/></el-icon>
           <span class="count">{{ formatNumber(strategy.collect_count) }}</span>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && !strategy" description="未找到该攻略" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  View, Star, StarFilled, Collection, CollectionTag, 
  EditPen, ChatLineRound 
} from '@element-plus/icons-vue'
import { getStrategyDetail, toggleStrategyCollection, toggleStrategyLike, getStrategyStats, getStrategyComments, createStrategyComment } from '@/api/content'
import type { Strategy, MediaAsset, StrategyStats, StrategyComment } from '@/types/content'
import { useUserStore } from '@/stores/user'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const strategy = ref<Strategy | null>(null)
const loading = ref(false)
const statsLoading = ref(false)
const tocItems = ref<{ id: string; text: string; level: number }[]>([])
const activeToc = ref<string>('')
const stats = ref<StrategyStats | null>(null)
const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
const comments = ref<StrategyComment[]>([])
const commentsLoading = ref(false)
const commentContent = ref('')

// 数据处理逻辑保持不变
const images = computed<MediaAsset[]>(() =>
  (strategy.value?.media_assets || []).filter((m: any) => m.type === 'image')
)
const videos = computed<MediaAsset[]>(() =>
  (strategy.value?.media_assets || []).filter((m: any) => m.type === 'video')
)

const heroImage = computed(() => {
  if (images.value.length) return images.value[0].url
  if ((strategy.value as any)?.game?.cover_image) return (strategy.value as any).game.cover_image
  return '' // 可以设置一个默认背景图
})

const heroStyle = computed(() => {
  if (!heroImage.value) return { background: '#1f2937' }
  return {
    backgroundImage: `url(${heroImage.value})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center center',
    backgroundRepeat: 'repeat'
  }
})

const statusLabel = computed(() => {
  if (!strategy.value) return ''
  const map: Record<string, string> = {
    approved: '', // 已发布通常不显示标签
    rejected: '未通过',
    pending: '审核中'
  }
  return map[strategy.value.status] || ''
})

const latestRejectReason = computed(() => {
  const reviews = (strategy.value as any)?.reviews || []
  const rejected = reviews.find((r: any) => r.decision === 'rejected' && r.reason)
  return rejected?.reason || ''
})

const isOwn = computed(
  () => !!userStore.userInfo?.id && strategy.value?.author?.id === userStore.userInfo?.id
)
const strategyId = computed(() => Number(route.params.id))
const isLoggedIn = computed(() => userStore.isLoggedIn)

const formatTime = (time: string) => {
  if (!time) return ''
  return new Date(time).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

const formatNumber = (num?: number) => {
  if (!num) return 0
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num
}

const fetchDetail = async () => {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const data = await getStrategyDetail(id)
    const { toc, html } = buildToc(data.content || '')
    tocItems.value = toc
    activeToc.value = toc[0]?.id || ''
    strategy.value = { ...(data as Strategy), content: html }
    if (isOwn.value) {
      fetchStats()
    }
    fetchComments()
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  if (!isOwn.value) return
  statsLoading.value = true
  try {
    const data = await getStrategyStats(strategyId.value, { days: 14 })
    stats.value = data as StrategyStats
    await nextTick()
    renderTrendChart()
  } catch (error: any) {
    ElMessage.error(error?.message || '加载统计数据失败')
  } finally {
    statsLoading.value = false
  }
}

const fetchComments = async () => {
  commentsLoading.value = true
  try {
    const resp = await getStrategyComments(strategyId.value)
    comments.value = resp as StrategyComment[]
  } catch (error: any) {
    ElMessage.error(error?.message || '加载评论失败')
  } finally {
    commentsLoading.value = false
  }
}

const submitComment = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录后再评论')
    return
  }
  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  try {
    const created = await createStrategyComment(strategyId.value, commentContent.value.trim())
    comments.value.unshift(created as StrategyComment)
    commentContent.value = ''
    if (strategy.value) {
      strategy.value.comment_count = (strategy.value.comment_count || 0) + 1
    }
    if (stats.value) {
      stats.value.comment_count += 1
      // 让趋势图刷新
      fetchStats()
    }
    ElMessage.success('评论成功')
  } catch (error: any) {
    ElMessage.error(error?.message || '评论失败')
  }
}

const renderTrendChart = () => {
  if (!trendChartRef.value || !stats.value) return
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  const dates = stats.value.trend.map((item) => item.date)
  trendChart.setOption({
    color: ['#3b82f6', '#f59e0b', '#10b981', '#a855f7'],
    tooltip: { trigger: 'axis' },
    legend: { data: ['阅读', '点赞', '收藏', '评论'] },
    grid: { left: 40, right: 20, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value' },
    series: [
      { name: '阅读', type: 'line', smooth: true, data: stats.value.trend.map((i) => i.views) },
      { name: '点赞', type: 'line', smooth: true, data: stats.value.trend.map((i) => i.likes) },
      { name: '收藏', type: 'line', smooth: true, data: stats.value.trend.map((i) => i.collects) },
      { name: '评论', type: 'line', smooth: true, data: stats.value.trend.map((i) => i.comments || 0) }
    ]
  })
}

const goToEdit = () => {
  if (strategy.value) router.push(`/strategies/edit/${strategy.value.id}`)
}

const buildToc = (html: string) => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html || '', 'text/html')
  const headings = Array.from(doc.querySelectorAll('h1,h2,h3'))
  const toc: { id: string; text: string; level: number }[] = []
  headings.forEach((node, idx) => {
    const id = node.id || `toc-${idx + 1}`
    node.id = id
    toc.push({
      id,
      text: (node.textContent || `段落 ${idx + 1}`).trim(),
      level: Number(node.tagName.substring(1))
    })
  })
  return { toc, html: doc.body.innerHTML }
}

const scrollToAnchor = (id: string) => {
  const el = document.getElementById(id)
  if (el) {
    activeToc.value = id
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const doLike = async () => {
  if (!strategy.value) return
  try {
    const resp = await toggleStrategyLike(strategy.value.id)
    strategy.value.is_liked = resp.is_liked
    // 乐观更新或使用返回的 count
    strategy.value.like_count = resp.like_count ?? (strategy.value.is_liked ? strategy.value.like_count + 1 : strategy.value.like_count - 1)
  } catch (e: any) {
    ElMessage.error('操作失败')
  }
}

const doCollect = async () => {
  if (!strategy.value) return
  try {
    const resp = await toggleStrategyCollection(strategy.value.id)
    strategy.value.is_collected = resp.is_collected
    strategy.value.collect_count = resp.collect_count ?? (strategy.value.is_collected ? strategy.value.collect_count + 1 : strategy.value.collect_count - 1)
  } catch (e: any) {
    ElMessage.error('操作失败')
  }
}

const handleResize = () => {
  if (trendChart) {
    trendChart.resize()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  fetchDetail()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }
})
</script>

<style scoped lang="scss">
/* CSS 变量定义，方便主题切换 */
$primary-color: var(--el-color-primary);
$bg-color: #0b1220;
$card-bg: #0f172a;
$text-main: #e2e8f0;
$text-sub: #94a3b8;

.strategy-detail-view {
  background-color: $bg-color;
  min-height: 100vh;
  padding-bottom: 80px; /* 为移动端底部栏留空 */
}

/* --- Hero Section --- */
.hero {
  position: relative;
  height: 360px;
  display: flex;
  align-items: flex-end;
  margin-bottom: -60px; /* 让内容卡片上浮覆盖一部分Hero */
  z-index: 1;
  
  .hero-mask {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.85));
    backdrop-filter: blur(3px);
  }

  .hero-content {
    position: relative;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px 80px; /* 底部留出空间给上浮的卡片 */
    color: #e2e8f0;
    z-index: 2;
  }

  .hero-crumbs :deep(.el-breadcrumb__inner) {
    color: rgba(255, 255, 255, 0.8);
    font-weight: 400;
  }
  
  .hero-main {
    margin-top: 20px;
  }

  .hero-title {
    font-size: 36px;
    font-weight: 800;
    margin: 12px 0;
    line-height: 1.3;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
  }

  .hero-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;

    .author-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .text-info {
        display: flex;
        flex-direction: column;
        .name { font-weight: 600; font-size: 16px; }
        .date { font-size: 13px; opacity: 0.8; }
      }
    }

    .stats-row {
      display: flex;
      gap: 20px;
      font-size: 14px;
      opacity: 0.9;
      span { display: flex; align-items: center; gap: 6px; color: #cbd5e1; }
    }
  }
}

/* --- Main Layout --- */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
  position: relative;
  z-index: 10;
}

/* --- Content Column --- */
.content-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  color: $text-sub;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.creator-stats-card {
  border-radius: 12px;
  .creator-stats-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }
  .metrics-row {
    margin-bottom: 12px;
  }
  .metric {
    background: var(--el-fill-color-light);
    border-radius: 10px;
    padding: 12px;
    .label {
      font-size: 12px;
      color: $text-sub;
    }
    .value {
      font-size: 20px;
      font-weight: 700;
      margin-top: 4px;
    }
  }
  .trend-chart-wrapper {
    height: 260px;
  }
  .trend-chart {
    width: 100%;
    height: 240px;
  }
}

.status-alert {
  margin-bottom: 8px;
}

.article-card {
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.06);
  background: rgba(15, 23, 42, 0.9);
  box-shadow: 0 12px 30px rgba(0,0,0,0.25);
  padding: 20px;
  min-height: 400px;
}

.comments-section {
  margin-top: 32px;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;

  .comment-form {
    margin-bottom: 16px;
    .comment-actions {
      margin-top: 8px;
      display: flex;
      justify-content: flex-end;
    }
  }

  .comment-login-tip {
    margin: 12px 0;
  }

  .comment-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-top: 8px;
  }

  .comment-item {
    display: flex;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
  }

  .comment-body {
    flex: 1;
    .comment-meta {
      display: flex;
      gap: 8px;
      font-size: 13px;
      color: $text-sub;
    }
    .comment-name {
      font-weight: 600;
      color: $text-main;
    }
    .comment-content {
      margin-top: 4px;
      color: $text-main;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }

  .comment-empty {
    color: $text-sub;
  }
}

/* 排版优化 */
.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: $text-main;

  :deep(h1), :deep(h2) {
    margin-top: 32px;
    margin-bottom: 16px;
    font-weight: 700;
    color: $text-main;
    padding-bottom: 8px;
    border-bottom: 1px solid #f1f5f9;
  }
  
  :deep(h3) {
    margin-top: 24px;
    margin-bottom: 12px;
    font-weight: 600;
    color: $text-main;
  }

  :deep(p) {
    margin-bottom: 16px;
    text-align: justify;
  }

  :deep(img) {
    max-width: 100%;
    border-radius: 8px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  :deep(blockquote) {
    border-left: 4px solid $primary-color;
    background: #f8fafc;
    padding: 12px 16px;
    margin: 16px 0;
    color: $text-sub;
    border-radius: 0 8px 8px 0;
  }
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  margin: 32px 0 16px;
  padding-left: 10px;
  border-left: 4px solid $primary-color;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  
  .gallery-item {
    border-radius: 8px;
    height: 140px;
    cursor: zoom-in;
    transition: transform 0.2s;
    &:hover { transform: scale(1.02); }
  }
}

.video-wrapper {
  border-radius: 12px;
  overflow: hidden;
  background: black;
  margin-bottom: 16px;
  video { width: 100%; aspect-ratio: 16/9; }
}

.article-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px dashed #e2e8f0;
  text-align: center;
  color: $text-sub;
  font-size: 12px;
}

/* --- Sidebar --- */
.sidebar-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.author-card {
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(15, 23, 42, 0.9);
  
  .author-header {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    
    .author-details {
      flex: 1;
      overflow: hidden;
      .name { font-weight: 700; font-size: 16px; margin-bottom: 4px;}
      .bio { font-size: 12px; color: $text-sub; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    }
  }
  
  .author-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    .el-button { width: 100%; }
  }
}

.action-card {
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(15, 23, 42, 0.9);
  
  .action-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px;
    background: #f1f5f9; /* 边框颜色 */
    border: 1px solid #f1f5f9;
    border-radius: 8px;
    overflow: hidden;
  }

  .action-item {
    background: white;
    padding: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    font-size: 13px;
    color: $text-sub;
    transition: all 0.2s;
    
    .icon-box { font-size: 20px; }
    
    &:hover { background: #fafafa; }
    
    &.active {
      color: $primary-color;
      .icon-box { transform: scale(1.1); }
    }
  }
  
  .divider { height: 12px; }
}

.toc-card {
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(15, 23, 42, 0.9);
  .toc-header { font-weight: 700; margin-bottom: 12px; }
  .toc-item {
    padding: 6px 10px;
    font-size: 14px;
    color: $text-main;
    cursor: pointer;
    border-radius: 4px;
    &:hover { background: #f8fafc; color: $primary-color; }
    &.active { background: rgba(255,255,255,0.08); color: $primary-color; }
  }
}

/* --- Mobile Adaptation --- */
.mobile-only { display: none; }
.desktop-only { display: block; }

@media (max-width: 768px) {
  .desktop-only { display: none; }
  .mobile-only { display: flex; }
  
  .hero { height: 280px; }
  .hero .hero-title { font-size: 24px; }
  
  .main-container {
    grid-template-columns: 1fr;
    padding: 0 16px;
  }
  
  .mobile-action-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: white;
    border-top: 1px solid #eee;
    display: flex;
    align-items: center;
    padding: 0 16px;
    z-index: 100;
    gap: 16px;
    
    .input-fake {
      flex: 1;
      background: #f3f4f6;
      border-radius: 18px;
      height: 36px;
      display: flex;
      align-items: center;
      padding: 0 12px;
      font-size: 13px;
      color: #9ca3af;
      gap: 6px;
    }
    
    .actions {
      display: flex;
      gap: 20px;
      
      .icon-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 10px;
        color: #64748b;
        gap: 2px;
        
        .el-icon { font-size: 22px; }
        
        &.active { color: $primary-color; }
      }
    }
  }
}
</style>

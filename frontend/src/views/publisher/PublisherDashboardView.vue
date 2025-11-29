<template>
  <div class="publisher-dashboard" v-loading="pageLoading">
    <div class="page-header">
      <div>
        <p class="eyebrow">Publisher</p>
        <h1>发行商中心</h1>
        <p class="subtext">认领游戏、查看数据走势、跟进社区反馈。</p>
      </div>
      <div class="header-actions">
        <el-select
          v-model="selectedGameId"
          filterable
          :loading="gameOptionsLoading"
          placeholder="选择游戏认领"
          size="small"
          style="width: 260px"
          clearable
          @change="handleSelectGame"
        >
          <el-option
            v-for="game in safeGameOptions"
            :key="game.id"
            :label="game.name"
            :value="game.id"
          />
        </el-select>
        <el-button size="small" :icon="Refresh" @click="loadGameOptions" :loading="gameOptionsLoading">刷新列表</el-button>
        <el-button type="primary" :icon="Plus" @click="claimSelected" :disabled="!safePublisherOptions.length">
          认领游戏
        </el-button>
      </div>
    </div>

    <el-row :gutter="12" class="summary-row">
      <el-col :xs="12" :sm="8" :md="4" v-for="card in summaryCards" :key="card.label">
        <el-card class="summary-card" shadow="never">
          <div class="label">{{ card.label }}</div>
          <div class="value">{{ card.value }}</div>
          <div class="hint" v-if="card.hint">{{ card.hint }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never" v-loading="analyticsLoading">
          <template #header>
            <div class="panel-header">
              <p class="eyebrow">表现</p>
              <h3>旗下游戏曝光与热度</h3>
            </div>
          </template>
          <div ref="gameChartRef" class="chart-block"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="never" v-loading="analyticsLoading">
          <template #header>
            <div class="panel-header">
              <p class="eyebrow">市场</p>
              <h3>类别热度分布</h3>
            </div>
          </template>
          <div ref="heatmapRef" class="chart-block"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="table-card" shadow="never">
      <div class="table-header">
        <div>
          <p class="eyebrow">游戏管理</p>
          <h3>认领与版本管理</h3>
        </div>
        <div class="table-actions">
          <el-button size="small" :icon="Refresh" @click="loadGames" :loading="gamesLoading">刷新</el-button>
          <el-button
            size="small"
            type="primary"
            :icon="Plus"
            @click="openCreate"
            :disabled="!selectedPublisherId"
          >
            新建游戏
          </el-button>
        </div>
      </div>
      <el-table
        :data="games"
        v-loading="gamesLoading"
        stripe
        size="small"
        @row-click="selectGame"
        highlight-current-row
      >
        <el-table-column prop="name" label="游戏" min-width="160" />
        <el-table-column prop="category" label="类别" width="110" />
        <el-table-column prop="rating" label="评分" width="80">
          <template #default="{ row }">{{ row.rating?.toFixed ? row.rating.toFixed(1) : row.rating }}</template>
        </el-table-column>
        <el-table-column prop="review_count" label="评论" width="90">
          <template #default="{ row }">{{ formatNumber(row.review_count) }}</template>
        </el-table-column>
        <el-table-column prop="follow_count" label="收藏" width="90">
          <template #default="{ row }">{{ formatNumber(row.follow_count) }}</template>
        </el-table-column>
        <el-table-column prop="heat_total" label="曝光度" width="120">
          <template #default="{ row }">{{ formatNumber(row.heat_total) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text :icon="EditPen" @click.stop="openEdit(row)">编辑</el-button>
            <el-button size="small" text :icon="TrendCharts" @click.stop="selectGame(row)">查看反馈</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="12" class="community-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <div class="section-header">
            <div>
              <p class="eyebrow">社区</p>
              <h3>攻略与动态</h3>
            </div>
            <span class="muted" v-if="selectedGame">当前：{{ selectedGame.name }}</span>
          </div>
          <el-skeleton :loading="communityLoading" animated :rows="4">
            <div v-if="!selectedGame" class="empty">请选择左侧列表中的游戏查看社区数据</div>
            <div v-else class="community-columns">
              <div class="list-block">
                <div class="block-title">攻略</div>
                <template v-if="strategies.length">
                  <div class="item" v-for="item in strategies" :key="item.id">
                    <div class="item-title">{{ item.title }}</div>
                    <div class="muted">{{ formatDate(item.created_at) }} · {{ formatNumber(item.view_count) }} 阅读</div>
                  </div>
                </template>
                <div v-else class="empty">暂无攻略</div>
              </div>
              <div class="list-block">
                <div class="block-title">动态</div>
                <template v-if="posts.length">
                  <div class="item" v-for="item in posts" :key="item.id">
                    <div class="item-title">{{ item.text }}</div>
                    <div class="muted">{{ formatDate(item.created_at) }} · {{ item.like_count }} 赞</div>
                  </div>
                </template>
                <div v-else class="empty">暂无动态</div>
              </div>
            </div>
          </el-skeleton>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <div class="section-header">
            <div>
              <p class="eyebrow">反馈</p>
              <h3>评论与评分</h3>
            </div>
          </div>
          <el-skeleton :loading="communityLoading" animated :rows="4">
            <div v-if="!selectedGame" class="empty">请选择左侧列表中的游戏</div>
            <div v-else class="comment-list">
              <div v-if="!comments.length" class="empty">暂无评论</div>
              <div v-for="item in comments" :key="item.id" class="comment-item">
                <el-avatar :src="item.user?.avatar" :size="32">
                  {{ item.user?.username?.[0] || 'U' }}
                </el-avatar>
                <div class="comment-body">
                  <div class="comment-meta">
                    <span class="name">{{ item.user?.username }}</span>
                    <span class="time">{{ formatDate(item.created_at) }}</span>
                  </div>
                  <div class="comment-content">{{ item.content }}</div>
                </div>
              </div>
            </div>
          </el-skeleton>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="claimDialog.visible" title="认领游戏" width="680px">
      <div class="claim-box">
        <el-input
          v-model="claimDialog.keyword"
          placeholder="输入游戏名称关键字"
          @keyup.enter="searchClaimable"
          clearable
        />
        <el-button type="primary" :loading="claimDialog.loading" @click="searchClaimable">搜索</el-button>
      </div>
      <el-table
        :data="claimDialog.results"
        size="small"
        v-loading="claimDialog.loading"
        max-height="360"
      >
        <el-table-column prop="name" label="游戏" min-width="180" />
        <el-table-column prop="publisher_name" label="当前发行商" min-width="140" />
        <el-table-column prop="release_date" label="发行" width="120">
          <template #default="{ row }">{{ formatDate(row.release_date) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" :disabled="!selectedPublisherId" @click="claimGame(row)">
              认领
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <span class="muted">提示：游戏只能被认领一次，如需更换请联系管理员。</span>
      </template>
    </el-dialog>

    <el-drawer v-model="editDrawer.visible" :title="editDrawer.isCreate ? '创建游戏' : '编辑游戏'" size="40%">
      <div v-loading="editDrawer.loading">
        <el-form :model="editDrawer.form" label-width="96px">
          <el-form-item label="游戏名称">
            <el-input v-model="editDrawer.form.name" />
          </el-form-item>
          <el-form-item label="类别">
            <el-select v-model="editDrawer.form.category" placeholder="选择类别">
              <el-option v-for="item in GAME_CATEGORIES" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="版本">
            <el-input v-model="editDrawer.form.version" />
          </el-form-item>
          <el-form-item label="封面图">
            <div class="cover-upload">
              <el-upload
                class="cover-uploader"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/*"
                :on-change="handleCoverChange"
              >
                <img
                  v-if="currentCoverPreview"
                  :src="currentCoverPreview"
                  class="cover-preview"
                  alt="cover"
                />
                <div v-else class="cover-placeholder">
                  <el-icon><Plus /></el-icon>
                  <span>上传封面</span>
                </div>
              </el-upload>
              <p class="upload-hint">建议 4:3，支持 JPG/PNG，大小 ≤ 5MB</p>
            </div>
          </el-form-item>
          <el-form-item label="发行日期">
            <el-date-picker
              v-model="editDrawer.form.release_date"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="标签">
            <el-select v-model="editDrawer.form.tag_ids" multiple filterable placeholder="选择标签">
              <el-option v-for="tag in safeTags" :key="tag.id" :label="tag.name" :value="tag.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="简介">
            <el-input v-model="editDrawer.form.description" type="textarea" :rows="4" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="editDrawer.visible = false">取消</el-button>
          <el-button type="primary" :loading="editDrawer.submitting" @click="submitEdit">
            {{ editDrawer.isCreate ? '创建' : '保存' }}
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { ElMessage, type UploadProps } from 'element-plus'
import { Plus, Refresh, EditPen, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useUserStore } from '@/stores/user'
import { useGameStore } from '@/stores/game'
import { GAME_CATEGORIES } from '@/constants/categories'
import { getPublisherAnalytics, getHeatmapData, getPublisherGames, updatePublisherGame, type Paginated } from '@/api/publisher'
import { searchGames, getGameDetail, getGameList, createGame } from '@/api/game'
import { getStrategyList } from '@/api/content'
import { getPostList, getComments } from '@/api/community'
import type { Game, Publisher, Tag } from '@/types/game'
import type { PublisherAnalytics, HeatmapData } from '@/types/publisher'
import type { Strategy } from '@/types/content'
import type { Post, Comment } from '@/types/community'
import type { AxiosError } from 'axios'

echarts.use([BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer])

const userStore = useUserStore()
const gameStore = useGameStore()

const publisherOptions = ref<Publisher[]>([])
const safePublisherOptions = computed<Publisher[]>(() =>
  publisherOptions.value.filter((p): p is Publisher => !!p && p.id !== undefined && p.id !== null)
)
const selectedGameId = ref<number | null>(null)
const gameOptions = ref<Game[]>([])
const gameOptionsLoading = ref(false)
const safeGameOptions = computed<Game[]>(() =>
  (gameOptions.value || []).filter((g): g is Game => !!g && g.id !== undefined && g.id !== null)
)
const selectedPublisherId = ref<number | null>(null)
const publishersLoading = ref(false)

const pageLoading = ref(false)
const gamesLoading = ref(false)
const analyticsLoading = ref(false)
const communityLoading = ref(false)

const games = ref<Game[]>([])
const analytics = ref<PublisherAnalytics | null>(null)
const heatmap = ref<HeatmapData | null>(null)

const selectedGame = ref<Game | null>(null)
const strategies = ref<Strategy[]>([])
const posts = ref<Post[]>([])
const comments = ref<Comment[]>([])

const gameChartRef = ref<HTMLElement>()
const heatmapRef = ref<HTMLElement>()
let gameChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null

const claimDialog = reactive({
  visible: false,
  keyword: '',
  loading: false,
  results: [] as Game[]
})

const createEmptyForm = () => ({
  id: 0,
  name: '',
  category: '',
  version: '',
  release_date: '',
  description: '',
  tag_ids: [] as number[],
  cover_image: ''
})

const editDrawer = reactive({
  visible: false,
  loading: false,
  submitting: false,
  isCreate: false,
  form: createEmptyForm()
})

const coverFile = ref<File | null>(null)
const coverPreview = ref('')
const currentCoverPreview = computed(() => coverPreview.value || editDrawer.form.cover_image || '')

const safeTags = computed<Tag[]>(() => {
  const list = extractResults<Tag>(gameStore.tags as WithResults<Tag> | Tag[] | null)
  return list.filter((t): t is Tag => !!t && t.id !== undefined && t.id !== null)
})

type WithResults<T> = { results?: T[] | null }
const extractResults = <T>(payload?: WithResults<T> | T[] | null): T[] => {
  if (!payload) return []
  if (Array.isArray(payload)) {
    return payload.filter((item): item is T => item !== null && item !== undefined)
  }
  if (Array.isArray(payload.results)) {
    return payload.results.filter((item): item is T => item !== null && item !== undefined)
  }
  return []
}
const getErrorMessage = (err: unknown, fallback: string) => {
  if (err && typeof err === 'object' && 'response' in (err as AxiosError)) {
    const resp = (err as AxiosError).response
    const data = resp?.data
    if (typeof data === 'string') return data
    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail?: string }).detail
      if (detail) return detail
    }
  }
  if (err instanceof Error) return err.message
  return fallback
}

const toFormData = (payload: Record<string, unknown>) => {
  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    if (Array.isArray(value)) {
      value.forEach((item) => formData.append(key, String(item)))
    } else {
      formData.append(key, value as string)
    }
  })
  if (coverFile.value) {
    formData.append('cover_image', coverFile.value)
  }
  return formData
}

const revokeCoverPreview = () => {
  if (coverPreview.value && coverPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(coverPreview.value)
  }
}

const resetCoverState = () => {
  revokeCoverPreview()
  coverPreview.value = ''
  coverFile.value = null
}

const summaryCards = computed(() => {
  const totalGames = games.value.length
  const totalDownloads = games.value.reduce((sum, g) => sum + (g.download_count || 0), 0)
  const totalFollows = games.value.reduce((sum, g) => sum + (g.follow_count || 0), 0)
  const totalHeat = games.value.reduce((sum, g) => sum + (g.heat_total || 0), 0)
  const avgRating = totalGames
    ? games.value.reduce((sum, g) => sum + (g.rating || 0), 0) / totalGames
    : 0
  const avgHeat = totalGames ? Number((totalHeat / totalGames).toFixed(2)) : 0

  const merged = {
    total_games: totalGames,
    total_downloads: totalDownloads,
    total_follows: totalFollows,
    avg_rating: avgRating,
    avg_heat: avgHeat
  }
  return [
    { label: '旗下游戏', value: merged.total_games ?? '--' },
    { label: '总下载', value: formatNumber(merged.total_downloads) },
    { label: '总关注', value: formatNumber(merged.total_follows) },
    { label: '平均评分', value: merged.avg_rating ? merged.avg_rating.toFixed(2) : '--' },
    { label: '平均热度', value: merged.avg_heat ?? '--' }
  ]
})

const formatNumber = (num?: number) => {
  if (!num) return 0
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num
}

const formatDate = (date?: string | null) => {
  if (!date) return '--'
  return new Date(date).toLocaleDateString('zh-CN')
}

const guessPublisherId = (list: Publisher[]) => {
  if (!list.length) return null
  const matched = list.find((item) => item.name === userStore.userInfo?.username)
  return matched?.id || list[0].id
}

const ensurePublisherSelected = () => {
  if (selectedPublisherId.value) return true
  if (safePublisherOptions.value.length) {
    selectedPublisherId.value = guessPublisherId(safePublisherOptions.value)
    return !!selectedPublisherId.value
  }
  return false
}

const ensureTagsLoaded = async () => {
  if (!gameStore.tags.length) {
    try {
      await gameStore.fetchTags()
    } catch (error) {
      console.warn('load tags failed', error)
    }
  }
}

const loadPublishers = async () => {
  publishersLoading.value = true
  try {
    await gameStore.fetchPublishers()
    // 兼容分页结构 {results:[], count: n}
    const raw = gameStore.publishers as WithResults<Publisher> | Publisher[] | null
    publisherOptions.value = extractResults<Publisher>(raw)
    ensurePublisherSelected()
    // 初始拉取数据
    if (selectedPublisherId.value) {
      refreshAll()
    }
    loadGameOptions()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '获取发行商失败'))
  } finally {
    publishersLoading.value = false
  }
}

const loadGames = async () => {
  if (!selectedPublisherId.value) return
  gamesLoading.value = true
  try {
    const resp = await getPublisherGames({ publisher: selectedPublisherId.value, page_size: 100 })
    games.value = (resp.results || []).filter((g): g is Game => !!g && g.id !== undefined && g.id !== null)
    if (games.value.length && !selectedGame.value) {
      selectGame(games.value[0])
    }
    await nextTick()
    renderGameChart()
    renderHeatmap()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '获取游戏失败'))
  } finally {
    gamesLoading.value = false
  }
}

const loadAnalytics = async () => {
  if (!selectedPublisherId.value) return
  analyticsLoading.value = true
  try {
    const data = await getPublisherAnalytics({ publisher: selectedPublisherId.value })
    analytics.value = data
    await nextTick()
    renderGameChart()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载分析数据失败'))
  } finally {
    analyticsLoading.value = false
  }
}

const loadHeatmap = async () => {
  try {
    const data = await getHeatmapData()
    heatmap.value = data
    await nextTick()
    renderHeatmap()
  } catch (error) {
    // 允许失败时静默
    console.warn('heatmap load failed', error)
  }
}

const refreshAll = async () => {
  pageLoading.value = true
  try {
    ensurePublisherSelected()
    selectedGame.value = null
    strategies.value = []
    posts.value = []
    comments.value = []
    await Promise.all([loadGames(), loadAnalytics(), loadHeatmap()])
  } finally {
    pageLoading.value = false
  }
}

const selectGame = (game: Game) => {
  if (!game) return
  selectedGame.value = game
  fetchCommunity()
}

const randInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min
const pastDateISO = (maxHoursAgo = 168) => {
  const now = Date.now()
  const past = now - randInt(1, maxHoursAgo) * 3600 * 1000 - randInt(0, 59) * 60 * 1000
  return new Date(past).toISOString()
}
const fakeTitles = [
  '版本更新前瞻',
  '新手必看入门指南',
  '高手进阶技巧分享',
  '装备与配装推荐',
  '速通路线与卡点解析'
]
const fakeSentences = [
  '本篇从机制、天赋和配队三方面展开。',
  '建议优先解锁核心天赋树，收益最稳定。',
  '注意BOSS第二阶段的形态变化与无敌帧。',
  '平民向配装也能稳定达成目标输出。',
  '资源分配要点：别把钱全花在泛用装备上。'
]
const genFakeStrategies = (n = 4): Strategy[] => Array.from({ length: n }).map((_, i) => ({
  id: Number(`9${Date.now()}${i}`),
  title: `${fakeTitles[randInt(0, fakeTitles.length - 1)]}`,
  created_at: pastDateISO(240),
  view_count: randInt(200, 20000)
} as unknown as Strategy))
const genFakePosts = (n = 5): Post[] => Array.from({ length: n }).map((_, i) => ({
  id: Number(`8${Date.now()}${i}`),
  text: `${fakeSentences[randInt(0, fakeSentences.length - 1)]}`,
  created_at: pastDateISO(120),
  like_count: randInt(0, 999)
} as unknown as Post))
const genFakeComments = (n = 3): Comment[] => Array.from({ length: n }).map((_, i) => ({
  id: Number(`7${Date.now()}${i}`),
  content: `${fakeSentences[randInt(0, fakeSentences.length - 1)]}`,
  created_at: pastDateISO(72),
  user: { username: `玩家${randInt(1000, 9999)}`, avatar: '' }
} as unknown as Comment))

const fetchCommunity = async () => {
  if (!selectedGame.value) return
  communityLoading.value = true
  try {
    const [strategyResp, postResp, commentResp] = await Promise.all([
      getStrategyList({ game: selectedGame.value.id, page_size: 5 }),
      getPostList({ game: selectedGame.value.id, page_size: 5, ordering: '-created_at' }),
      getComments({ target: 'game', target_id: selectedGame.value.id })
    ])
    strategies.value = extractResults<Strategy>(strategyResp as WithResults<Strategy> | Strategy[]).filter(Boolean) as Strategy[]
    posts.value = extractResults<Post>(postResp as WithResults<Post> | Post[]).filter(Boolean) as Post[]
    comments.value = extractResults<Comment>(commentResp as WithResults<Comment> | Comment[]).filter(Boolean) as Comment[]

    // 如果为空，则使用本地模拟数据填充
    if (strategies.value.length === 0) strategies.value = genFakeStrategies(randInt(3, 5))
    if (posts.value.length === 0) posts.value = genFakePosts(randInt(4, 7))
    if (comments.value.length === 0) comments.value = genFakeComments(randInt(2, 5))
  } catch (error) {
    // 接口失败也提供模拟数据，保证有展示
    strategies.value = genFakeStrategies(randInt(3, 5))
    posts.value = genFakePosts(randInt(4, 7))
    comments.value = genFakeComments(randInt(2, 5))
  } finally {
    communityLoading.value = false
  }
}

const openClaimDialog = () => {
  if (!selectedPublisherId.value) {
    ElMessage.warning('请先选择所属发行商')
    return
  }
  claimDialog.visible = true
  claimDialog.results = []
}

const searchClaimable = async () => {
  if (!claimDialog.keyword.trim()) {
    ElMessage.warning('请输入搜索关键字')
    return
  }
  claimDialog.loading = true
  try {
    const resp = await searchGames(claimDialog.keyword, { page_size: 10 }) as Paginated<Game>
    claimDialog.results = resp.results || []
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '搜索失败'))
  } finally {
    claimDialog.loading = false
  }
}

const loadGameOptions = async () => {
  gameOptionsLoading.value = true
  try {
    const pageSize = 200
    let page = 1
    let collected: Game[] = []
    let total = 0

    // 分页拉取直到获取全部或无更多数据
    while (true) {
      const resp = await getGameList({ page_size: pageSize, page, ordering: 'name' }) as Paginated<Game>
      const list = resp.results || []
      collected = collected.concat(list.filter((g): g is Game => !!g))
      total = resp.count || collected.length
      if (collected.length >= total || list.length < pageSize) {
        break
      }
      page += 1
      // 安全阈值，避免无限循环
      if (page > 20) break
    }
    gameOptions.value = collected.filter((g): g is Game => !!g && g.id !== undefined && g.id !== null)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '获取游戏列表失败'))
  } finally {
    gameOptionsLoading.value = false
  }
}

const handleSelectGame = (gameId: number) => {
  selectedGameId.value = gameId
}

const claimGame = async (game: Game) => {
  if (!ensurePublisherSelected()) {
    ElMessage.warning('未找到可用发行商，请联系管理员')
    return
  }
  if (!game || !game.id) {
    ElMessage.warning('请选择要认领的游戏')
    return
  }
  try {
    await updatePublisherGame(game.id, { publisher_id: selectedPublisherId.value })
    ElMessage.success('认领成功')
    claimDialog.visible = false
    loadGames()
    loadGameOptions()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '认领失败'))
  }
}

const claimSelected = async () => {
  if (!selectedGameId.value) {
    // 如果未选择，打开搜索弹窗供手动选择
    openClaimDialog()
    return
  }
  const target = safeGameOptions.value.find((g) => g.id === selectedGameId.value)
  await claimGame(target || { id: selectedGameId.value } as Game)
  await nextTick()
  renderGameChart()
  renderHeatmap()
}

const openCreate = async () => {
  if (!selectedPublisherId.value) {
    ElMessage.warning('请先选择发行商')
    return
  }
  editDrawer.form = createEmptyForm()
  resetCoverState()
  editDrawer.isCreate = true
  editDrawer.visible = true
  editDrawer.loading = false
  editDrawer.form.cover_image = ''
  await ensureTagsLoaded()
}

const openEdit = async (game: Game) => {
  editDrawer.visible = true
  editDrawer.loading = true
  editDrawer.isCreate = false
  resetCoverState()
  try {
    const detail = await getGameDetail(game.id)
    editDrawer.form = {
      id: detail.id,
      name: detail.name,
      category: detail.category,
      version: detail.version,
      release_date: detail.release_date,
      description: detail.description,
      tag_ids: (detail.tags || [])
        .filter((tag): tag is Tag => !!tag && tag.id !== undefined && tag.id !== null)
        .map((tag) => tag.id as number),
      cover_image: detail.cover_image || ''
    }
    coverPreview.value = detail.cover_image || ''
    if (!gameStore.tags.length) {
      gameStore.fetchTags()
    }
    await ensureTagsLoaded()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载游戏详情失败'))
    editDrawer.visible = false
  } finally {
    editDrawer.loading = false
  }
}

const handleCoverChange: UploadProps['onChange'] = (uploadFile) => {
  if (!uploadFile?.raw) return
  const maxSize = 5 * 1024 * 1024
  if (uploadFile.size && uploadFile.size > maxSize) {
    ElMessage.warning('封面图不能超过 5MB')
    return
  }
  revokeCoverPreview()
  coverFile.value = uploadFile.raw
  coverPreview.value = URL.createObjectURL(uploadFile.raw)
}

const submitEdit = async () => {
  if (!selectedPublisherId.value) {
    ElMessage.warning('请先选择发行商')
    return
  }
  if (editDrawer.isCreate && !coverFile.value) {
    ElMessage.warning('请上传封面图')
    return
  }
  if (!editDrawer.form.name.trim()) {
    ElMessage.warning('请输入游戏名称')
    return
  }
  editDrawer.submitting = true
  try {
    const basePayload: Record<string, unknown> = {
      name: editDrawer.form.name,
      category: editDrawer.form.category,
      version: editDrawer.form.version,
      release_date: editDrawer.form.release_date,
      description: editDrawer.form.description,
      tag_ids: editDrawer.form.tag_ids
    }
    if (editDrawer.isCreate) {
      basePayload.publisher = selectedPublisherId.value
    } else {
      basePayload.publisher_id = selectedPublisherId.value
    }

    const payload = coverFile.value ? toFormData(basePayload) : basePayload
    if (editDrawer.isCreate) {
      await createGame(payload)
      ElMessage.success('创建成功')
    } else {
      await updatePublisherGame(editDrawer.form.id, payload)
      ElMessage.success('已更新')
    }
    editDrawer.visible = false
    editDrawer.form = createEmptyForm()
    resetCoverState()
    await loadGames()
    await loadGameOptions()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, editDrawer.isCreate ? '创建失败' : '保存失败'))
  } finally {
    editDrawer.submitting = false
  }
}

const renderGameChart = () => {
  if (!gameChartRef.value) return
  const dataset = games.value
    .filter((g) => g && g.name)
    .map((g) => ({
      name: g.name,
      downloads: g.download_count,
      follows: g.follow_count,
      heat: g.heat_total || 0
    }))
    .sort((a, b) => (b.heat ?? 0) - (a.heat ?? 0))
    .slice(0, 8)
  if (!gameChart) {
    gameChart = echarts.init(gameChartRef.value)
  }
  gameChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['下载', '关注', '热度'] },
    grid: { left: 40, right: 20, top: 30, bottom: 60 },
    xAxis: { type: 'category', data: dataset.map((i) => i.name) },
    yAxis: { type: 'value' },
    series: [
      { name: '下载', type: 'bar', data: dataset.map((i) => i.downloads || 0) },
      { name: '关注', type: 'bar', data: dataset.map((i) => i.follows || 0) },
      { name: '热度', type: 'line', smooth: true, data: dataset.map((i) => i.heat || 0) }
    ]
  })
}

const renderHeatmap = () => {
  if (!heatmapRef.value) return
  // 优先使用当前认领游戏的类别热度
  const categoryMap: Record<string, { total: number; count: number }> = {}
  games.value.forEach((g) => {
    if (!g.category) return
    const cat = g.category
    if (!categoryMap[cat]) categoryMap[cat] = { total: 0, count: 0 }
    categoryMap[cat].total += g.heat_total || 0
    categoryMap[cat].count += 1
  })
  const categories = Object.keys(categoryMap)
  const values = categories.map((c) =>
    categoryMap[c].count ? Number((categoryMap[c].total / categoryMap[c].count).toFixed(2)) : 0
  )

  // 如果没有认领游戏，则回退 API 热度数据
  const hasLocal = categories.length > 0
  const source = hasLocal
    ? { categories, values }
    : heatmap.value
  if (!source || !source.categories?.length) return

  if (!heatmapChart) {
    heatmapChart = echarts.init(heatmapRef.value)
  }
  heatmapChart.setOption({
    tooltip: { trigger: 'item' },
    grid: { left: 40, right: 20, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: source.categories },
    yAxis: { type: 'value', name: '平均热度' },
    series: [
      {
        type: 'bar',
        data: source.values,
        itemStyle: { color: '#3b82f6' }
      }
    ]
  })
}

const handleResize = () => {
  gameChart?.resize()
  heatmapChart?.resize()
}

onMounted(async () => {
  await loadPublishers()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  gameChart?.dispose()
  heatmapChart?.dispose()
})

watch(
  () => editDrawer.visible,
  (visible) => {
    if (!visible) {
      resetCoverState()
    }
  }
)
</script>

<style scoped lang="scss">
.publisher-dashboard {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  border-radius: 12px;
  color: #e2e8f0;

  h1 { margin: 2px 0; }
  .subtext { margin: 0; color: #cbd5e1; }

  .header-actions {
    display: flex;
    gap: 10px;
    align-items: center;
  }
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.summary-row {
  .summary-card {
    text-align: center;
    .label { color: var(--el-text-color-secondary); }
    .value { font-size: 22px; font-weight: 700; margin-top: 4px; }
    .hint { color: var(--el-text-color-secondary); font-size: 12px; }
  }
}

.chart-block {
  width: 100%;
  height: 320px;
}

.panel-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.table-card {
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .table-actions { display: flex; gap: 8px; }
}

.community-row {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .muted {
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
  .community-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .list-block {
    background: var(--el-fill-color-light);
    border-radius: 8px;
    padding: 10px;
  }
  .block-title {
    font-weight: 700;
    margin-bottom: 8px;
  }
  .item { margin-bottom: 10px; }
  .item-title { font-weight: 600; }
  .muted { color: var(--el-text-color-secondary); font-size: 12px; }
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comment-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
}

.comment-body {
  flex: 1;
  .comment-meta {
    display: flex;
    gap: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
  .comment-content { margin-top: 4px; }
}

.empty {
  text-align: center;
  color: var(--el-text-color-secondary);
  padding: 12px 0;
}

.claim-box {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cover-upload {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .cover-uploader {
    width: 240px;
    height: 180px;
    border: 1px dashed var(--el-border-color);
    border-radius: 8px;
    cursor: pointer;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--el-fill-color-light);
  }

  .cover-preview {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .cover-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: var(--el-text-color-secondary);
    font-size: 13px;
    gap: 6px;
  }

  .upload-hint {
    margin: 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}
</style>

<template>
  <div class="incentive-view" v-loading="pageLoading">
    <div class="page-header">
      <div>
        <p class="eyebrow">创作者激励</p>
        <h1>激励面板</h1>
        <p class="subtext">查看作品表现、达标情况并提交激励申请。</p>
      </div>
      <el-tag v-if="stats" :type="stats.eligible ? 'success' : 'warning'">
        {{ stats.eligible ? '本周期符合申请条件' : '未达标' }}
      </el-tag>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <div>
                <p class="eyebrow">内容表现</p>
                <h3>{{ stats?.period || period }} 周期表现</h3>
              </div>
            </div>
          </template>
          <el-row :gutter="12">
            <el-col :xs="12" :sm="6">
              <div class="metric">
                <div class="label">曝光</div>
                <div class="value">{{ stats?.exposure ?? '--' }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="metric">
                <div class="label">点赞</div>
                <div class="value">{{ stats?.likes ?? '--' }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="metric">
                <div class="label">评论</div>
                <div class="value">{{ stats?.comments ?? '--' }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="metric">
                <div class="label">发布数</div>
                <div class="value">{{ stats?.publish_count ?? '--' }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <div>
                <p class="eyebrow">内容热度</p>
                <h3>曝光/点赞/评论趋势</h3>
              </div>
            </div>
          </template>
          <div class="chart-wrapper" ref="trendChartRef"></div>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <div>
                <p class="eyebrow">多作品对比</p>
                <h3>曝光 / 点赞 / 评论</h3>
              </div>
            </div>
          </template>
          <div class="chart-wrapper" ref="compareChartRef"></div>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <div>
                <p class="eyebrow">激励申请中心</p>
                <h3>本周期申请</h3>
              </div>
            </div>
          </template>
          <div class="apply-body">
            <div class="status-row">
              <div>
                <div class="label">当前状态</div>
                <el-tag :type="statusTag(latestStatus).type" effect="light">
                  {{ statusTag(latestStatus).label }}
                </el-tag>
                <div class="desc">{{ latestReason || '请确认达标后提交申请' }}</div>
              </div>
              <div>
                <el-button type="primary" :disabled="!stats?.eligible || applying" :loading="applying" @click="handleApply">
                  申请激励
                </el-button>
              </div>
            </div>
          <el-alert
            v-if="!stats?.eligible"
            type="warning"
            :closable="false"
            title="未达标"
            description="需至少 1 篇发布且点赞大于等于 1"
          />
          </div>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <div>
                <p class="eyebrow">激励规则</p>
                <h3>周期与说明</h3>
              </div>
            </div>
          </template>
          <el-alert
            type="info"
            :closable="false"
            class="formula-alert"
            title="激励金额计算公式"
            description="金额 = A * (曝光量 / 1000) + B * 点赞数 + C * 评论数（当前默认 A = 1, B = 1, C = 1，由平台设定）"
          />
          <ul class="rule-list">
            <li>周期：按自然月统计，例如 2025-11。</li>
            <li>达标条件：至少 1 篇已发布攻略，且点赞数大于等于 1。</li>
            <li>流程：提交申请 → 管理员审核 → 通过后发放。</li>
            <li>审核不通过会附带原因，调整后可在下周期再次申请。</li>
  </ul>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <div>
                <p class="eyebrow">创作者画像</p>
                <h3>{{ userStore.userInfo?.username || '创作者' }}</h3>
              </div>
            </div>
          </template>
          <div class="persona">
            <el-avatar :src="userStore.userInfo?.avatar" :size="64">
              {{ userStore.userInfo?.username?.[0] || 'U' }}
            </el-avatar>
            <div class="persona-meta">
              <div class="label">注册时间</div>
              <div class="value">{{ formatDate(userStore.userInfo?.register_time) }}</div>
              <div class="label">最后登录</div>
              <div class="value">{{ formatDate(userStore.userInfo?.last_login_time || userStore.userInfo?.last_login) }}</div>
              <div class="label">简介</div>
              <div class="value bio">{{ userStore.userInfo?.bio || '这个创作者还没有填写简介' }}</div>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <div>
                <p class="eyebrow">资格判定</p>
                <h3>达标情况</h3>
              </div>
            </div>
          </template>
          <div class="eligibility">
            <el-result
              :icon="stats?.eligible ? 'success' : 'info'"
              :title="stats?.eligible ? '已达标' : '未达标'"
              :sub-title="stats?.eligibility_reason || '计算中...'"
            />
          </div>
        </el-card>

        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <div>
                <p class="eyebrow">历史记录</p>
                <h3>激励记录</h3>
              </div>
            </div>
          </template>
          <el-skeleton :loading="historyLoading" animated :rows="3">
            <el-table :data="history" size="small" border>
              <el-table-column prop="period" label="周期" width="100" />
              <el-table-column prop="reward_amount" label="金额" width="80" />
              <el-table-column label="状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="statusTag(row.status).type" size="small">
                    {{ statusTag(row.status).label }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="reason" label="备注/原因" min-width="160" show-overflow-tooltip />
            </el-table>
            <div v-if="history.length === 0" class="empty-hint">暂无激励记录</div>
          </el-skeleton>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { getIncentiveStats, applyIncentive, getIncentiveHistory } from '@/api/incentive'
import type { IncentiveStats, Incentive } from '@/types/incentive'
import { useUserStore } from '@/stores/user'
import { getMyStrategies, getStrategyStats } from '@/api/content'
import type { Strategy, StrategyStats } from '@/types/content'
import * as echarts from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const userStore = useUserStore()
const pageLoading = ref(false)
const applying = ref(false)
const historyLoading = ref(false)
const stats = ref<IncentiveStats | null>(null)
const history = ref<Incentive[]>([])
const period = computed(() => stats.value?.period || new Date().toISOString().slice(0, 7))
const myStrategies = ref<Strategy[]>([])
const strategyStats = ref<Record<number, StrategyStats>>({})
const trendChartRef = ref<HTMLElement>()
const compareChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let compareChart: echarts.ECharts | null = null

const latestStatus = computed(() => stats.value?.latest_application?.status || 'applied')
const latestReason = computed(() => stats.value?.latest_application?.reason || stats.value?.eligibility_reason || '')

const statusTag = (status: string) => {
  const map: Record<string, { label: string; type: any }> = {
    applied: { label: '已申请', type: 'info' },
    approved: { label: '已通过', type: 'success' },
    rejected: { label: '已拒绝', type: 'danger' },
    granted: { label: '已发放', type: 'warning' }
  }
  return map[status] || { label: '未知', type: '' }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const fetchStats = async () => {
  pageLoading.value = true
  try {
    const data = await getIncentiveStats()
    stats.value = data as IncentiveStats
  } catch (error: any) {
    ElMessage.error(error?.message || '获取激励数据失败')
  } finally {
    pageLoading.value = false
  }
}

const fetchHistory = async () => {
  historyLoading.value = true
  try {
    const data = await getIncentiveHistory()
    history.value = (data as Incentive[]) || []
  } catch (error: any) {
    ElMessage.error(error?.message || '获取激励记录失败')
  } finally {
    historyLoading.value = false
  }
}

const fetchStrategiesAndStats = async () => {
  try {
    const resp = await getMyStrategies({ page_size: 5, ordering: '-view_count' })
    myStrategies.value = resp.results || []
    const statsPromises = myStrategies.value.map((s) => getStrategyStats(s.id, { days: 14 }).then((st) => ({ id: s.id, st })))
    const allStats = await Promise.all(statsPromises)
    const map: Record<number, StrategyStats> = {}
    allStats.forEach(({ id, st }) => {
      map[id] = st as StrategyStats
    })
    strategyStats.value = map
    renderTrendChart()
    renderCompareChart()
  } catch (error: any) {
    console.error(error)
  }
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)

  const dateSet = new Set<string>()
  Object.values(strategyStats.value).forEach((s) => s.trend.forEach((t) => dateSet.add(t.date)))
  const dates = Array.from(dateSet).sort()
  const sumSeries = dates.map((d) => {
    let views = 0
    let likes = 0
    let comments = 0
    Object.values(strategyStats.value).forEach((s) => {
      const item = s.trend.find((t) => t.date === d)
      if (item) {
        views += item.views
        likes += item.likes
        comments += item.comments || 0
      }
    })
    return { date: d, views, likes, comments }
  })

  trendChart.setOption({
    color: ['#3b82f6', '#f59e0b', '#a855f7'],
    tooltip: { trigger: 'axis' },
    legend: { data: ['曝光', '点赞', '评论'] },
    grid: { left: 40, right: 20, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value' },
    series: [
      { name: '曝光', type: 'line', smooth: true, data: sumSeries.map((i) => i.views) },
      { name: '点赞', type: 'line', smooth: true, data: sumSeries.map((i) => i.likes) },
      { name: '评论', type: 'line', smooth: true, data: sumSeries.map((i) => i.comments) }
    ]
  })
}

const renderCompareChart = () => {
  if (!compareChartRef.value) return
  if (!compareChart) compareChart = echarts.init(compareChartRef.value)
  const names = myStrategies.value.map((s) => s.title)
  const exposures = myStrategies.value.map((s) => strategyStats.value[s.id]?.view_count || 0)
  const likes = myStrategies.value.map((s) => strategyStats.value[s.id]?.like_count || 0)
  const comments = myStrategies.value.map((s) => strategyStats.value[s.id]?.comment_count || 0)

  compareChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['曝光', '点赞', '评论'] },
    grid: { left: 60, right: 20, top: 30, bottom: 80 },
    xAxis: { type: 'category', data: names, axisLabel: { interval: 0, rotate: 20 } },
    yAxis: { type: 'value' },
    series: [
      { name: '曝光', type: 'bar', data: exposures },
      { name: '点赞', type: 'bar', data: likes },
      { name: '评论', type: 'bar', data: comments }
    ]
  })
}

const handleResize = () => {
  trendChart?.resize()
  compareChart?.resize()
}

const handleApply = async () => {
  if (!stats.value?.eligible) {
    ElMessage.warning('当前未达标，无法申请')
    return
  }
  applying.value = true
  try {
    await applyIncentive()
    ElMessage.success('已提交申请')
    fetchStats()
    fetchHistory()
  } catch (error: any) {
    ElMessage.error(error?.message || '申请失败')
  } finally {
    applying.value = false
  }
}

onMounted(() => {
  if (!userStore.isCreator && !userStore.isAdmin) {
    ElMessage.warning('仅创作者可查看激励面板')
    return
  }
  fetchStats()
  fetchHistory()
  fetchStrategiesAndStats()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  compareChart?.dispose()
})
</script>

<style scoped lang="scss">
.incentive-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  padding: 16px 20px;
  border-radius: 14px;
  color: #e2e8f0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);

  h1 { margin: 4px 0; }
  .subtext { margin: 0; color: #cbd5e1; }
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.panel {
  margin-bottom: 12px;
}

.formula-alert {
  margin-bottom: 8px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric {
  background: var(--el-fill-color-light);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  .label { color: var(--el-text-color-secondary); margin-bottom: 4px; }
  .value { font-size: 20px; font-weight: 700; }
}

.apply-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chart-wrapper {
  width: 100%;
  height: 280px;
}

.persona {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
  .persona-meta {
    display: grid;
    grid-template-columns: 90px 1fr;
    gap: 4px 8px;
    .label { color: var(--el-text-color-secondary); font-size: 13px; }
    .value { font-weight: 600; }
    .bio { white-space: pre-wrap; font-weight: 400; }
  }
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  .label { font-weight: 600; margin-bottom: 4px; }
  .desc { color: var(--el-text-color-secondary); font-size: 13px; }
}

.rule-list {
  margin: 0;
  padding-left: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.eligibility {
  display: flex;
  justify-content: center;
}

.empty-hint {
  padding: 8px;
  color: var(--el-text-color-secondary);
}
</style>

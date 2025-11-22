<template>
  <div class="analytics-view" v-loading="loading">
    <div class="page-header">
      <div>
        <p class="eyebrow">数据分析</p>
        <h1>运营概览</h1>
        <p class="subtext">基于现有数据的用户与内容走势。</p>
      </div>
      <el-select v-model="days" size="small" style="width: 140px" @change="fetchOverview">
        <el-option :value="7" label="近7天" />
        <el-option :value="14" label="近14天" />
        <el-option :value="30" label="近30天" />
      </el-select>
    </div>

    <el-row :gutter="16" class="summary-row">
      <el-col :xs="12" :sm="8" :md="4" v-for="card in cards" :key="card.label">
        <el-card class="summary-card" shadow="never">
          <div class="label">{{ card.label }}</div>
          <div class="value">{{ card.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <p class="eyebrow">趋势</p>
              <h3>新增用户 / 攻略 / 动态 / 评论</h3>
            </div>
          </template>
          <div ref="trendChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <p class="eyebrow">话题</p>
              <h3>热门话题 Top 5</h3>
            </div>
          </template>
          <el-table :data="topics" border height="320" size="small">
            <el-table-column prop="name" label="话题" min-width="120" />
            <el-table-column prop="post_count" label="帖子" width="80" />
            <el-table-column prop="follow_count" label="关注" width="80" />
            <el-table-column prop="heat" label="热度" width="100" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getAnalyticsOverview } from '@/api/analytics'

echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const loading = ref(false)
const days = ref(7)
const overview = ref<any>(null)
const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null

const topics = computed(() => overview.value?.topics || [])

const cards = computed(() => {
  const s = overview.value?.summary || {}
  return [
    { label: '用户', value: s.users_total ?? '--' },
    { label: '创作者', value: s.creators ?? '--' },
    { label: '攻略', value: s.strategies_total ?? '--' },
    { label: '动态', value: s.posts_total ?? '--' },
    { label: '评论', value: s.comments_total ?? '--' },
    { label: '游戏', value: s.games_total ?? '--' }
  ]
})

const fetchOverview = async () => {
  loading.value = true
  try {
    overview.value = await getAnalyticsOverview({ days: days.value })
    await nextTick()
    renderTrend()
  } catch (error: any) {
    ElMessage.error(error?.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

const renderTrend = () => {
  if (!trendChartRef.value || !overview.value?.trend) return
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)
  const t = overview.value.trend
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['用户', '攻略', '动态', '评论'] },
    grid: { left: 50, right: 20, top: 40, bottom: 40 },
    xAxis: { type: 'category', data: t.dates },
    yAxis: { type: 'value' },
    series: [
      { name: '用户', type: 'line', data: t.users },
      { name: '攻略', type: 'line', data: t.strategies },
      { name: '动态', type: 'line', data: t.posts },
      { name: '评论', type: 'line', data: t.comments }
    ]
  })
}

const handleResize = () => {
  trendChart?.resize()
}

onMounted(() => {
  fetchOverview()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped lang="scss">
.analytics-view {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  color: #e2e8f0;
  padding: 14px 16px;
  border-radius: 12px;
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

.summary-row {
  margin-bottom: 4px;
}

.summary-card {
  text-align: center;
  .label { color: var(--el-text-color-secondary); }
  .value { font-size: 22px; font-weight: 700; margin-top: 6px; }
}

.panel-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chart {
  width: 100%;
  height: 340px;
}
</style>

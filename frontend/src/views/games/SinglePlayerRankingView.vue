<template>
  <div class="ranking-page" v-loading="loading">
    <div class="page-header">
      <div>
        <p class="eyebrow">业务定时任务 · 每5分钟刷新</p>
        <h1>单机游戏排行榜</h1>
        <p class="subtext">数据来源：3DM（自动抓取），点击可跳转专题或平台内详情</p>
      </div>
      <div class="actions">
        <el-button :icon="Refresh" @click="fetchData" :loading="loading">手动刷新</el-button>
      </div>
    </div>

    <el-card shadow="never" class="ranking-card">
      <div class="ranking-list">
        <div
          v-for="item in rankings"
          :key="item.id || item.rank"
          class="ranking-row"
        >
          <div class="rank-badge">#{{ item.rank }}</div>
          <div class="cover" @click="openExternal(item.detail_url)">
            <img
              :src="item.cover_url || getPlaceholderImage('game')"
              :alt="item.name"
              @error="handleImageError"
              referrerpolicy="no-referrer"
            />
          </div>
          <div class="meta">
            <div class="title-line">
              <el-link
                v-if="item.detail_url"
                :href="item.detail_url"
                target="_blank"
                class="name"
                :underline="false"
                :title="item.name"
              >
                {{ item.name }}
              </el-link>
              <span v-else class="name" :title="item.name">{{ item.name }}</span>
              <el-tag v-if="item.score" type="warning" effect="dark" size="small">
                {{ item.score }}
              </el-tag>
              <span class="votes" v-if="item.rating_count">· {{ formatNumber(item.rating_count) }} 人评分</span>
            </div>
            <div class="subtitle" v-if="item.english_name">{{ item.english_name }}</div>
            <div class="info-line">
              <span v-if="item.genre">{{ item.genre }}</span>
              <span v-if="item.platforms" class="dot">·</span>
              <span v-if="item.platforms">{{ item.platforms }}</span>
              <span v-if="item.release_date" class="dot">·</span>
              <span v-if="item.release_date">发售：{{ formatDate(item.release_date) }}</span>
            </div>
            <div class="tags" v-if="item.tags?.length">
              <el-tag
                v-for="tag in item.tags.slice(0, 5)"
                :key="tag"
                size="small"
                effect="plain"
                type="info"
              >
                {{ tag }}
              </el-tag>
            </div>
            <div class="link-line">
              <el-button v-if="item.detail_url" size="small" text type="primary" :href="item.detail_url" target="_blank">
                3DM 专题
              </el-button>
              <el-button
                v-if="item.game"
                size="small"
                type="primary"
                round
                @click="gotoGame(item.game)"
              >
                查看平台详情
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-if="!loading && rankings.length === 0" description="暂无榜单数据，稍后重试或手动刷新" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSinglePlayerRanking } from '@/api/game'
import { getPlaceholderImage, handleImageError } from '@/utils/image'
import type { SinglePlayerRanking } from '@/types/game'
import { Refresh } from '@element-plus/icons-vue'

const rankings = ref<SinglePlayerRanking[]>([])
const loading = ref(false)
const router = useRouter()

const formatNumber = (num?: number | null) => {
  if (!num) return 0
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num
}

const formatDate = (v: string) => v?.replace(/-/g, '/') || v

const gotoGame = (game: number | any) => {
  const id = typeof game === 'number' ? game : game?.id
  if (id) {
    router.push(`/games/${id}`)
  }
}

const openExternal = (url?: string | null) => {
  if (url) {
    window.open(url, '_blank', 'noopener')
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getSinglePlayerRanking({ limit: 100, source: '3dm' })
    rankings.value = Array.isArray(data) ? data : data?.results || []
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped lang="scss">
.ranking-page {
  display: flex;
  flex-direction: column;
  gap: 16px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .eyebrow {
      margin: 0;
      font-weight: 700;
      color: var(--el-color-primary);
    }

    h1 {
      margin: 4px 0;
    }

    .subtext {
      margin: 0;
      color: var(--el-text-color-secondary);
    }
  }

  .ranking-card {
    border-radius: 16px;
  }

  .ranking-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .ranking-row {
    display: grid;
    grid-template-columns: 72px 120px 1fr;
    gap: 16px;
    align-items: center;
    padding: 14px;
    border-radius: 12px;
    background: var(--el-fill-color-light);
    transition: transform 0.2s ease, box-shadow 0.2s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
    }
  }

  .rank-badge {
    width: 72px;
    height: 72px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    border-radius: 16px;
    font-weight: 800;
    font-size: 22px;
    box-shadow: 0 10px 20px rgba(118, 75, 162, 0.35);
  }

  .cover {
    width: 120px;
    height: 120px;
    border-radius: 12px;
    overflow: hidden;
    background: var(--el-fill-color-darker);

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .meta {
    display: flex;
    flex-direction: column;
    gap: 6px;

    .title-line {
      display: flex;
      align-items: center;
      gap: 8px;

      .name {
        font-weight: 800;
        font-size: 18px;
        color: var(--el-text-color-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .votes {
        color: var(--el-text-color-secondary);
        font-size: 12px;
      }
    }

    .subtitle {
      color: var(--el-text-color-secondary);
      font-size: 13px;
    }

    .info-line {
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--el-text-color-regular);
      font-size: 13px;

      .dot {
        opacity: 0.5;
      }
    }

    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .link-line {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }
}

@media (max-width: 768px) {
  .ranking-row {
    grid-template-columns: 60px 1fr;
    grid-template-rows: auto auto;
    .cover {
      grid-row: span 2;
    }
  }
}
</style>

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
    <div v-loading="loading">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getRecommendedGames } from '@/api/game'
import { StarFilled, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getGameCoverUrl, handleImageError } from '@/utils/image'

const router = useRouter()

const loading = ref(false)
const recommendedGames = ref<any[]>([])

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

const getRecommendReason = (item: any) => {
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
    const response = await getRecommendedGames({ top: 12 })
    recommendedGames.value = response.results || []
    
    if (recommendedGames.value.length === 0) {
      console.log('暂无推荐数据，建议先与游戏互动（收藏、点赞等）')
    }
  } catch (error: any) {
    console.error('获取推荐失败:', error)
    ElMessage.error(error.message || '获取推荐失败')
  } finally {
    loading.value = false
  }
}

const goToDetail = (id: number) => {
  router.push(`/games/${id}`)
}

onMounted(() => {
  fetchRecommendations()
})
</script>

<style scoped lang="scss">
.recommend-view {
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
}
</style>











<template>
  <div class="strategy-list-view">
    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="搜索攻略标题"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="排序">
          <el-select 
            v-model="filters.ordering" 
            placeholder="请选择排序方式" 
            style="width: 180px"
            @change="handleSearch"
          >
            <el-option 
              v-for="option in orderingOptions"
              :key="option.value"
              :label="option.label" 
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 攻略列表 -->
    <div class="strategy-list" v-loading="loading">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="strategy in strategies" :key="strategy.id">
          <el-card class="strategy-card" @click="handleCardClick(strategy)">
            <div class="strategy-header">
              <el-avatar :src="strategy.author?.avatar" :size="40">
                {{ strategy.author?.username?.[0] || 'U' }}
              </el-avatar>
              <div class="author-info">
                <span class="author-name">{{ strategy.author?.username || '匿名用户' }}</span>
                <span class="publish-time">{{ formatTime(strategy.created_at) }}</span>
              </div>
              <el-tooltip
                v-if="isOwnStrategy(strategy)"
                content="编辑我的攻略"
                placement="top"
              >
                <el-button
                  circle
                  text
                  size="small"
                  @click.stop="goToEdit(strategy.id)"
                >
                  <EditPen />
                </el-button>
              </el-tooltip>
            </div>
            
            <h4 class="strategy-title">{{ strategy.title }}</h4>
            
            <div class="strategy-meta">
              <el-tag size="small" v-if="strategy.game">{{ strategy.game.name }}</el-tag>
              <el-tag size="small" type="success" v-if="strategy.status === 'approved'">已审核</el-tag>
            </div>
            
            <div class="strategy-stats">
              <span><el-icon><View /></el-icon> {{ strategy.view_count || 0 }}</span>
              <span><el-icon><Star /></el-icon> {{ strategy.like_count || 0 }}</span>
              <span><el-icon><Collection /></el-icon> {{ strategy.collect_count || 0 }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 空状态 -->
      <el-empty v-if="!loading && strategies.length === 0" description="暂无攻略" />
    </div>
    
    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 36, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
    
    <!-- 创建攻略按钮 -->
    <el-button
      v-if="userStore.isCreator"
      type="primary"
      circle
      size="large"
      class="create-btn"
      @click="router.push('/strategies/create')"
    >
      <el-icon><EditPen /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getStrategyList } from '@/api/content'
import { Search, View, Star, Collection, EditPen } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const strategies = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 排序选项
const orderingOptions = [
  { label: '最新发布', value: '-created_at' },
  { label: '最多浏览', value: '-view_count' },
  { label: '最多点赞', value: '-like_count' },
  { label: '最多收藏', value: '-collect_count' }
]

const filters = reactive({
  search: '',
  ordering: '-created_at'
})

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString()
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchStrategies()
}

// 重置
const handleReset = () => {
  filters.search = ''
  filters.ordering = '-created_at'
  handleSearch()
}

// 分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchStrategies()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 每页数量变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchStrategies()
}

// 获取攻略列表
const fetchStrategies = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: filters.ordering
    }
    
    if (filters.search) {
      params.search = filters.search
    }
    
    const response = await getStrategyList(params)
    strategies.value = response.results || []
    total.value = response.count || 0
  } catch (error: any) {
    console.warn('获取攻略列表失败:', error)
    strategies.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 跳转到详情
const goToDetail = (strategy: any) => {
  router.push(`/strategies/${strategy.id}`)
}

const goToEdit = (id: number) => {
  router.push(`/strategies/edit/${id}`)
}

const isOwnStrategy = (strategy: any) =>
  !!userStore.userInfo?.id && strategy.author?.id === userStore.userInfo?.id

const handleCardClick = async (strategy: any) => {
  if (isOwnStrategy(strategy)) {
    try {
      await ElMessageBox.confirm('你要对自己的攻略进行什么操作？', '我的攻略', {
        confirmButtonText: '编辑',
        cancelButtonText: '查看',
        distinguishCancelAndClose: true,
        type: 'info'
      })
      goToEdit(strategy.id)
    } catch (action: any) {
      if (action === 'cancel') {
        goToDetail(strategy)
      }
      // close/other do nothing
    }
  } else {
    goToDetail(strategy)
  }
}

onMounted(() => {
  // 从路由参数中获取搜索关键词
  if (route.query.search) {
    filters.search = route.query.search as string
  }
  
  fetchStrategies()
})
</script>

<style scoped lang="scss">
.strategy-list-view {
  .filter-card {
    margin-bottom: 20px;
    
    :deep(.el-form) {
      .el-form-item {
        margin-bottom: 12px;
      }
    }
    
    // 移动端适配
    @media (max-width: 768px) {
      :deep(.el-form) {
        .el-form-item {
          width: 100%;
          margin-right: 0;
          
          .el-select {
            width: 100% !important;
          }
          
          .el-input {
            width: 100%;
          }
        }
      }
    }
  }
  
  .strategy-list {
    min-height: 400px;
    margin-bottom: 20px;
    
    .strategy-card {
      cursor: pointer;
      transition: transform 0.3s, box-shadow 0.3s;
      margin-bottom: 20px;
      height: 100%;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      .strategy-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        
        .author-info {
          display: flex;
          flex-direction: column;
          
          .author-name {
            font-weight: bold;
            color: var(--el-text-color-primary);
          }
          
          .publish-time {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
      }
      
      .strategy-title {
        margin: 0 0 12px;
        font-size: 16px;
        line-height: 1.5;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }
      
      .strategy-meta {
        display: flex;
        gap: 8px;
        margin-bottom: 12px;
      }
      
      .strategy-stats {
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
  }
  
  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
  
  .create-btn {
    position: fixed;
    right: 40px;
    bottom: 40px;
    z-index: 100;
    width: 56px;
    height: 56px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}
</style>

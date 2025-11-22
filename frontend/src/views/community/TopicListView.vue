<template>
  <div class="topic-list-view">
    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="搜索话题名称"
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

        <el-form-item v-if="userStore.isLoggedIn">
          <el-button type="success" @click="showCreateDialog = true">创建话题</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 话题列表 -->
    <div class="topic-list" v-loading="loading">
      <div class="hot-topics" v-if="hotTopics.length">
        <h3>热门话题</h3>
        <div class="hot-list">
          <div class="hot-item" v-for="topic in hotTopics" :key="topic.id" @click="goToTopicPosts(topic.id)">
            <span class="rank">#{{ topic.rank }}</span>
            <span class="name">#{{ topic.name }}</span>
            <span class="heat">热度 {{ formatNumber(topic.heat || 0) }}</span>
            <el-button
              size="small"
              type="primary"
              :plain="!topic.is_followed"
              @click.stop="toggleFollow(topic)"
              :loading="followingIds.has(topic.id)"
            >
              {{ topic.is_followed ? '已关注' : '关注' }}
            </el-button>
          </div>
        </div>
      </div>

      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="topic in topics" :key="topic.id">
          <el-card class="topic-card" @click="goToTopicPosts(topic.id)">
            <div class="topic-header">
              <div class="topic-icon">
                <el-icon :size="32"><CollectionTag /></el-icon>
              </div>
            </div>
            
            <h4 class="topic-name">#{{ topic.name }}</h4>
            <p class="topic-description">{{ topic.description || '暂无描述' }}</p>
            
            <div class="topic-stats">
              <div class="stat-item">
                <span class="stat-value">{{ formatNumber(topic.post_count || 0) }}</span>
                <span class="stat-label">帖子</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ formatNumber(topic.follow_count || 0) }}</span>
                <span class="stat-label">关注</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ formatNumber(topic.heat || 0) }}</span>
                <span class="stat-label">热度</span>
              </div>
            </div>
            
            <el-button
              type="primary"
              :plain="!topic.is_followed"
              class="follow-btn"
              @click.stop="toggleFollow(topic)"
              :loading="followingIds.has(topic.id)"
            >
              {{ topic.is_followed ? '已关注' : '关注' }}
            </el-button>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 空状态 -->
      <el-empty v-if="!loading && topics.length === 0" description="暂无话题" />
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

    <el-dialog v-model="showCreateDialog" title="创建话题" width="520px" @close="resetTopicForm">
      <el-form :model="topicForm" label-width="80px">
        <el-form-item label="话题名称">
          <el-input v-model="topicForm.name" maxlength="20" show-word-limit placeholder="请输入话题名称，如：#动作游戏#" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="topicForm.description" type="textarea" :rows="3" maxlength="200" show-word-limit placeholder="简要介绍话题" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateTopic">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getTopicList, toggleTopicFollow, getHotTopics, createTopic } from '@/api/community'
import { Search, CollectionTag } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const topics = ref<any[]>([])
const hotTopics = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const followingIds = ref(new Set<number>())
const showCreateDialog = ref(false)
const creating = ref(false)
const topicForm = reactive({
  name: '',
  description: ''
})

// 排序选项
const orderingOptions = [
  { label: '热度', value: '-heat' },
  { label: '关注数', value: '-follow_count' },
  { label: '帖子数', value: '-post_count' },
  { label: '最新创建', value: '-created_at' }
]

const filters = reactive({
  search: '',
  ordering: '-heat'
})

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
  currentPage.value = 1
  fetchTopics()
}

// 重置
const handleReset = () => {
  filters.search = ''
  filters.ordering = '-heat'
  handleSearch()
}

// 分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchTopics()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 每页数量变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchTopics()
}

// 获取话题列表
const fetchTopics = async () => {
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
    
    const response = await getTopicList(params)
    topics.value = response.results || []
    total.value = response.count || 0
  } catch (error: any) {
    console.warn('获取话题列表失败:', error)
    topics.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const fetchHotTopics = async () => {
  try {
    const resp = await getHotTopics()
    hotTopics.value = (resp as any[])?.map((t: any, idx: number) => ({ ...t, rank: idx + 1 })) || []
  } catch (error: any) {
    console.warn('获取热门话题失败', error)
  }
}

// 关注/取消关注话题
const toggleFollow = async (topic: any) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  
  followingIds.value.add(topic.id)
  
  try {
    const resp = await toggleTopicFollow(topic.id)
    topic.is_followed = resp.is_following
    if (resp.is_following) {
      topic.follow_count = (topic.follow_count || 0) + 1
    } else {
      topic.follow_count = Math.max(0, (topic.follow_count || 0) - 1)
    }
    ElMessage.success(resp.is_following ? '关注成功' : '取消关注成功')
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    followingIds.value.delete(topic.id)
  }
}

// 跳转到话题下的帖子列表
const goToTopicPosts = (id: number) => {
  router.push(`/community/posts?topic=${id}`)
}

onMounted(() => {
  fetchTopics()
  fetchHotTopics()
})

const resetTopicForm = () => {
  topicForm.name = ''
  topicForm.description = ''
}

const handleCreateTopic = async () => {
  if (!topicForm.name.trim()) {
    ElMessage.warning('请输入话题名称')
    return
  }
  creating.value = true
  try {
    await createTopic({
      name: topicForm.name.trim(),
      description: topicForm.description.trim()
    })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    resetTopicForm()
    fetchTopics()
    fetchHotTopics()
  } catch (error: any) {
    ElMessage.error(error?.message || '创建失败')
  } finally {
    creating.value = false
  }
}
</script>

<style scoped lang="scss">
.topic-list-view {
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
  
  .topic-list {
    min-height: 400px;
    margin-bottom: 20px;
    
    .hot-topics {
      margin-bottom: 16px;
      padding: 12px;
      border: 1px solid var(--el-border-color);
      border-radius: 8px;
      
      .hot-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .hot-item {
        display: grid;
        grid-template-columns: 60px 1fr 120px 120px;
        align-items: center;
        gap: 8px;
        padding: 8px 10px;
        border-radius: 6px;
        cursor: pointer;
        &:hover { background: var(--el-fill-color-light); }
        .rank { font-weight: 700; color: var(--el-color-primary); }
        .name { font-weight: 600; }
        .heat { color: var(--el-text-color-secondary); }
      }
    }
    
    .topic-card {
      cursor: pointer;
      transition: transform 0.3s, box-shadow 0.3s;
      margin-bottom: 20px;
      text-align: center;
      height: 100%;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      .topic-header {
        display: flex;
        justify-content: center;
        margin-bottom: 16px;
        
        .topic-icon {
          width: 64px;
          height: 64px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }
      }
      
      .topic-name {
        margin: 0 0 8px;
        font-size: 18px;
        font-weight: bold;
        color: var(--el-color-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .topic-description {
        margin: 0 0 16px;
        font-size: 14px;
        color: var(--el-text-color-secondary);
        line-height: 1.5;
        height: 42px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }
      
      .topic-stats {
        display: flex;
        justify-content: space-around;
        margin-bottom: 16px;
        padding: 16px 0;
        border-top: 1px solid var(--el-border-color-lighter);
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        .stat-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          
          .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }
          
          .stat-label {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
      }
      
      .follow-btn {
        width: 100%;
      }
    }
  }
  
  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}
</style>

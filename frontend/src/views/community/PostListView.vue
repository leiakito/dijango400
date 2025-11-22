<template>
  <div class="post-list-view">
    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="搜索动态内容"
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
    
    <!-- 动态列表 -->
    <div class="post-list" v-loading="loading">
      <el-timeline>
        <el-timeline-item
          v-for="post in posts"
          :key="post.id"
          :timestamp="formatTime(post.created_at)"
          placement="top"
        >
          <el-card class="post-card" @click="goToDetail(post.id)">
            <div class="post-header">
              <el-avatar :src="post.author?.avatar" :size="40">
                {{ post.author?.username?.[0] || 'U' }}
              </el-avatar>
              <div class="author-info">
                <span class="author-name">{{ post.author?.username || '匿名用户' }}</span>
                <div class="post-topics" v-if="post.topics && post.topics.length > 0">
                  <el-tag
                    v-for="topic in post.topics.slice(0, 3)"
                    :key="topic.id"
                    size="small"
                    type="info"
                    effect="plain"
                  >
                    #{{ topic.name }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <div class="post-content">{{ post.text || '暂无内容' }}</div>
            
            <div class="post-footer">
              <span><el-icon><Star /></el-icon> {{ post.like_count || 0 }}</span>
              <span><el-icon><ChatDotRound /></el-icon> {{ post.comment_count || 0 }}</span>
              <span><el-icon><Share /></el-icon> {{ post.share_count || 0 }}</span>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      
      <!-- 空状态 -->
      <el-empty v-if="!loading && posts.length === 0" description="暂无动态" />
    </div>
    
    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 30, 40]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
    
    <!-- 发布动态按钮 -->
    <el-button
      v-if="userStore.isLoggedIn"
      type="primary"
      circle
      size="large"
      class="create-btn"
      @click="showCreateDialog = true"
    >
      <el-icon><EditPen /></el-icon>
    </el-button>
    
    <!-- 发布动态对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="发布动态"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="postForm" label-width="80px">
        <el-form-item label="动态内容">
          <el-input
            v-model="postForm.text"
            type="textarea"
            :rows="6"
            placeholder="分享你的想法..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getPostList, createPost } from '@/api/community'
import { Search, Star, ChatDotRound, Share, EditPen } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const posts = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const showCreateDialog = ref(false)
const submitting = ref(false)

// 排序选项
const orderingOptions = [
  { label: '最新发布', value: '-created_at' },
  { label: '最多点赞', value: '-like_count' },
  { label: '最多评论', value: '-comment_count' }
]

const filters = reactive({
  search: '',
  ordering: '-created_at'
})

const postForm = reactive({
  text: ''
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
  fetchPosts()
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
  fetchPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 每页数量变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchPosts()
}

// 获取动态列表
const fetchPosts = async () => {
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
    
    const response = await getPostList(params)
    posts.value = response.results || []
    total.value = response.count || 0
  } catch (error: any) {
    console.warn('获取动态列表失败:', error)
    posts.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 跳转到详情
const goToDetail = (id: number) => {
  router.push(`/community/posts/${id}`)
}

// 重置表单
const resetForm = () => {
  postForm.text = ''
}

// 发布动态
const handleCreate = async () => {
  if (!postForm.text.trim()) {
    ElMessage.warning('请输入动态内容')
    return
  }
  
  submitting.value = true
  try {
    await createPost({ text: postForm.text.trim() })
    ElMessage.success('发布成功')
    showCreateDialog.value = false
    resetForm()
    fetchPosts()
  } catch (error: any) {
    ElMessage.error(error.message || '发布失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped lang="scss">
.post-list-view {
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
  
  .post-list {
    min-height: 400px;
    margin-bottom: 20px;
    
    .post-card {
      cursor: pointer;
      transition: box-shadow 0.3s;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      .post-header {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 12px;
        
        .author-info {
          flex: 1;
          
          .author-name {
            display: block;
            font-weight: bold;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }
          
          .post-topics {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
          }
        }
      }
      
      .post-content {
        margin-bottom: 12px;
        line-height: 1.6;
        color: var(--el-text-color-regular);
        white-space: pre-wrap;
        word-break: break-word;
      }
      
      .post-footer {
        display: flex;
        gap: 16px;
        font-size: 14px;
        color: var(--el-text-color-secondary);
        padding-top: 12px;
        border-top: 1px solid var(--el-border-color-lighter);
        
        span {
          display: flex;
          align-items: center;
          gap: 4px;
          
          &:hover {
            color: var(--el-color-primary);
          }
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

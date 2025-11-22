<template>
  <div class="content-review-view">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#409EFF"><Document /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ statistics.total }}</div>
              <div class="stat-label">总攻略数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#E6A23C"><Clock /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ statistics.pending }}</div>
              <div class="stat-label">待审核</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#67C23A"><Select /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ statistics.approved }}</div>
              <div class="stat-label">已通过</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#F56C6C"><CloseBold /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ statistics.rejected }}</div>
              <div class="stat-label">已拒绝</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="搜索标题或内容"
            clearable
            style="width: 240px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select 
            v-model="filters.status" 
            placeholder="全部状态" 
            clearable
            style="width: 160px"
            @change="handleSearch"
          >
            <el-option 
              v-for="option in statusOptions"
              :key="option.value"
              :label="option.label" 
              :value="option.value"
            />
          </el-select>
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
    
    <!-- 内容列表 -->
    <el-card class="list-card">
      <el-table 
        :data="contents" 
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="标题" min-width="200">
          <template #default="{ row }">
            <div class="content-title">
              {{ row.title }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="游戏" width="150">
          <template #default="{ row }">
            {{ row.game?.name || '未知游戏' }}
          </template>
        </el-table-column>
        
        <el-table-column label="作者" width="120">
          <template #default="{ row }">
            {{ row.author?.username || '匿名' }}
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="统计" width="180">
          <template #default="{ row }">
            <div class="stats-mini">
              <span><el-icon><View /></el-icon> {{ row.view_count }}</span>
              <span><el-icon><Star /></el-icon> {{ row.like_count }}</span>
              <span><el-icon><Collection /></el-icon> {{ row.collect_count }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="viewContent(row)"
              link
            >
              查看详情
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleApprove(row)"
              link
              v-if="row.status === 'pending'"
            >
              通过
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleReject(row)"
              link
              v-if="row.status === 'pending'"
            >
              拒绝
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="viewHistory(row)"
              link
            >
              审核历史
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
    
    <!-- 内容详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="攻略详情"
      width="900px"
      @close="closeDetailDialog"
    >
      <div v-if="currentContent" class="content-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">
            {{ currentContent.id }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentContent.status)">
              {{ getStatusLabel(currentContent.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标题" :span="2">
            {{ currentContent.title }}
          </el-descriptions-item>
          <el-descriptions-item label="作者">
            {{ currentContent.author?.username || '匿名' }}
          </el-descriptions-item>
          <el-descriptions-item label="游戏">
            {{ currentContent.game?.name || '未知游戏' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentContent.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(currentContent.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="内容" :span="2">
            <div class="content-text">{{ currentContent.content }}</div>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="dialog-actions">
          <el-button 
            type="success" 
            @click="handleApprove(currentContent)"
            v-if="currentContent.status === 'pending'"
          >
            通过审核
          </el-button>
          <el-button 
            type="danger" 
            @click="handleReject(currentContent)"
            v-if="currentContent.status === 'pending'"
          >
            拒绝审核
          </el-button>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>
    
    <!-- 拒绝原因对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝审核"
      width="500px"
    >
      <el-form :model="rejectForm" label-width="100px">
        <el-form-item label="攻略标题">
          {{ rejectForm.title }}
        </el-form-item>
        <el-form-item label="拒绝原因" required>
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="6"
            placeholder="请输入拒绝原因，将会通知作者"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject" :loading="submitting">确定拒绝</el-button>
      </template>
    </el-dialog>
    
    <!-- 审核历史对话框 -->
    <el-dialog
      v-model="historyDialogVisible"
      title="审核历史"
      width="700px"
    >
      <el-timeline v-if="reviewHistory.length > 0">
        <el-timeline-item
          v-for="review in reviewHistory"
          :key="review.id"
          :timestamp="formatDate(review.reviewed_at)"
          placement="top"
          :type="review.decision === 'approved' ? 'success' : 'danger'"
        >
          <div class="review-item">
            <p><strong>审核人：</strong>{{ review.reviewer_name || '系统' }}</p>
            <p><strong>决定：</strong>
              <el-tag :type="review.decision === 'approved' ? 'success' : 'danger'" size="small">
                {{ review.decision === 'approved' ? '通过' : '拒绝' }}
              </el-tag>
            </p>
            <p v-if="review.reason"><strong>原因：</strong>{{ review.reason }}</p>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无审核记录" :image-size="100" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, Clock, Select, CloseBold, Search, View, Star, Collection 
} from '@element-plus/icons-vue'
import { 
  getReviewList, getReviewStatistics, 
  approveContent, rejectContent, getReviewHistory 
} from '@/api/admin'

const loading = ref(false)
const submitting = ref(false)
const contents = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 统计信息
const statistics = ref({
  total: 0,
  pending: 0,
  approved: 0,
  rejected: 0
})

// 筛选选项
const statusOptions = [
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' }
]

const orderingOptions = [
  { label: '最新创建', value: '-created_at' },
  { label: '最早创建', value: 'created_at' },
  { label: '最近更新', value: '-updated_at' }
]

const filters = reactive({
  search: '',
  status: 'pending', // 默认显示待审核
  ordering: '-created_at'
})

// 内容详情
const detailDialogVisible = ref(false)
const currentContent = ref<any>(null)

// 拒绝对话框
const rejectDialogVisible = ref(false)
const rejectForm = reactive({
  id: 0,
  title: '',
  reason: ''
})

// 审核历史
const historyDialogVisible = ref(false)
const reviewHistory = ref<any[]>([])

// 获取状态标签类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || ''
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return labelMap[status] || status
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchContents()
}

// 重置
const handleReset = () => {
  filters.search = ''
  filters.status = 'pending'
  filters.ordering = '-created_at'
  handleSearch()
}

// 分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchContents()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 每页数量变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchContents()
}

// 获取统计信息
const fetchStatistics = async () => {
  try {
    const data = await getReviewStatistics()
    statistics.value = data
  } catch (error: any) {
    console.error('获取统计信息失败:', error)
  }
}

// 获取内容列表
const fetchContents = async () => {
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
    if (filters.status) {
      params.status = filters.status
    }
    
    const response = await getReviewList(params)
    contents.value = response.results || []
    total.value = response.count || 0
  } catch (error: any) {
    ElMessage.error(error.message || '获取内容列表失败')
    contents.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 查看内容详情
const viewContent = (content: any) => {
  currentContent.value = content
  detailDialogVisible.value = true
}

// 关闭详情对话框
const closeDetailDialog = () => {
  currentContent.value = null
}

// 通过审核
const handleApprove = async (content: any) => {
  try {
    await ElMessageBox.confirm('确定通过该攻略的审核吗？', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })
    
    loading.value = true
    await approveContent(content.id)
    ElMessage.success('审核通过')
    
    // 关闭对话框并刷新列表
    detailDialogVisible.value = false
    fetchContents()
    fetchStatistics()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  } finally {
    loading.value = false
  }
}

// 拒绝审核
const handleReject = (content: any) => {
  rejectForm.id = content.id
  rejectForm.title = content.title
  rejectForm.reason = ''
  rejectDialogVisible.value = true
}

// 确认拒绝
const confirmReject = async () => {
  if (!rejectForm.reason.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }
  
  submitting.value = true
  try {
    await rejectContent(rejectForm.id, rejectForm.reason)
    ElMessage.success('已拒绝')
    
    // 关闭对话框并刷新列表
    rejectDialogVisible.value = false
    detailDialogVisible.value = false
    fetchContents()
    fetchStatistics()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 查看审核历史
const viewHistory = async (content: any) => {
  try {
    loading.value = true
    const data = await getReviewHistory(content.id)
    reviewHistory.value = data
    historyDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取审核历史失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStatistics()
  fetchContents()
})
</script>

<style scoped lang="scss">
.content-review-view {
  .stats-row {
    margin-bottom: 20px;
    
    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 20px;
        
        .stat-text {
          flex: 1;
          
          .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: var(--el-text-color-primary);
            margin-bottom: 8px;
          }
          
          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-secondary);
          }
        }
      }
    }
  }
  
  .filter-card {
    margin-bottom: 20px;
    
    :deep(.el-form) {
      .el-form-item {
        margin-bottom: 12px;
      }
    }
  }
  
  .list-card {
    .content-title {
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
    
    .stats-mini {
      display: flex;
      gap: 12px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      
      span {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
    
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
  
  .content-detail {
    .content-text {
      max-height: 300px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.6;
    }
    
    .dialog-actions {
      margin-top: 20px;
      text-align: right;
      padding-top: 20px;
      border-top: 1px solid var(--el-border-color);
    }
  }
  
  .review-item {
    p {
      margin: 4px 0;
      font-size: 14px;
    }
  }
}
</style>

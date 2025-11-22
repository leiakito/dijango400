<template>
  <div class="user-manage-view">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#409EFF"><User /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ statistics.total }}</div>
              <div class="stat-label">总用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#67C23A"><UserFilled /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ statistics.by_status[1] || 0 }}</div>
              <div class="stat-label">正常用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#F56C6C"><Warning /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ statistics.by_status[0] || 0 }}</div>
              <div class="stat-label">封禁用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#E6A23C"><TrendCharts /></el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ statistics.recent_registrations }}</div>
              <div class="stat-label">近30天注册</div>
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
            placeholder="搜索用户名或邮箱"
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
        
        <el-form-item label="角色">
          <el-select 
            v-model="filters.role" 
            placeholder="全部角色" 
            clearable
            style="width: 160px"
            @change="handleSearch"
          >
            <el-option 
              v-for="option in roleOptions"
              :key="option.value"
              :label="option.label" 
              :value="option.value"
            />
          </el-select>
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
    
    <!-- 用户表格 -->
    <el-card class="table-card">
      <el-table 
        :data="users" 
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="用户" min-width="200">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :src="row.avatar" :size="40">
                {{ row.username[0] }}
              </el-avatar>
              <div class="user-text">
                <div class="username">{{ row.username }}</div>
                <div class="email">{{ row.email || '未设置邮箱' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="角色" width="140">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">
              {{ UserRoleLabels[row.role] }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ UserStatusLabels[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.register_time) }}
          </template>
        </el-table-column>
        
        <el-table-column label="最后登录" width="180">
          <template #default="{ row }">
            {{ row.last_login_time ? formatDate(row.last_login_time) : '从未登录' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="viewUser(row)"
              link
            >
              查看详情
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="changeRole(row)"
              link
            >
              修改角色
            </el-button>
            <el-button 
              :type="row.status === 1 ? 'danger' : 'success'" 
              size="small" 
              @click="toggleStatus(row)"
              link
            >
              {{ row.status === 1 ? '封禁' : '解封' }}
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
    
    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="用户详情"
      width="800px"
      @close="closeDetailDialog"
    >
      <div v-if="currentUser" class="user-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">
            {{ currentUser.id }}
          </el-descriptions-item>
          <el-descriptions-item label="用户名">
            {{ currentUser.username }}
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">
            {{ currentUser.email || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="手机号">
            {{ currentUser.phone || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="getRoleType(currentUser.role)">
              {{ UserRoleLabels[currentUser.role] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentUser.status === 1 ? 'success' : 'danger'">
              {{ UserStatusLabels[currentUser.status] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">
            {{ formatDate(currentUser.register_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后登录">
            {{ currentUser.last_login_time ? formatDate(currentUser.last_login_time) : '从未登录' }}
          </el-descriptions-item>
          <el-descriptions-item label="个人简介" :span="2">
            {{ currentUser.bio || '暂无简介' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 操作记录 -->
        <div class="operations-section">
          <h3>操作记录（最近50条）</h3>
          <el-timeline v-if="userOperations.length > 0">
            <el-timeline-item
              v-for="op in userOperations"
              :key="op.id"
              :timestamp="formatDate(op.created_at)"
              placement="top"
            >
              <p>{{ op.content }}</p>
              <p class="operation-meta">
                <span v-if="op.ip_address">IP: {{ op.ip_address }}</span>
              </p>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无操作记录" :image-size="100" />
        </div>
      </div>
    </el-dialog>
    
    <!-- 修改角色对话框 -->
    <el-dialog
      v-model="roleDialogVisible"
      title="修改用户角色"
      width="500px"
    >
      <el-form :model="roleForm" label-width="100px">
        <el-form-item label="当前角色">
          <el-tag :type="getRoleType(roleForm.currentRole)">
            {{ UserRoleLabels[roleForm.currentRole] }}
          </el-tag>
        </el-form-item>
        <el-form-item label="新角色">
          <el-select v-model="roleForm.newRole" placeholder="请选择新角色" style="width: 100%">
            <el-option 
              v-for="option in roleOptions"
              :key="option.value"
              :label="option.label" 
              :value="option.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmChangeRole" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 封禁/解封对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      :title="statusForm.action === 'ban' ? '封禁用户' : '解封用户'"
      width="500px"
    >
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="用户">
          {{ statusForm.username }}
        </el-form-item>
        <el-form-item label="原因" v-if="statusForm.action === 'ban'">
          <el-input
            v-model="statusForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入封禁原因"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button 
          :type="statusForm.action === 'ban' ? 'danger' : 'success'" 
          @click="confirmToggleStatus" 
          :loading="submitting"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, User, UserFilled, Warning, TrendCharts 
} from '@element-plus/icons-vue'
import { 
  getUserList, getUserDetail, getUserOperations, 
  updateUserRole, updateUserStatus, getUserStatistics 
} from '@/api/admin'
import type { 
  AdminUser, UserOperation, UserStatistics, UserRole, UserStatus 
} from '@/types/admin'
import { UserRoleLabels, UserStatusLabels } from '@/types/admin'

const loading = ref(false)
const submitting = ref(false)
const users = ref<AdminUser[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 统计信息
const statistics = ref<UserStatistics>({
  total: 0,
  by_role: {},
  by_status: {},
  recent_registrations: 0
})

// 筛选项
const roleOptions = [
  { label: '普通玩家', value: 'player' },
  { label: '内容创作者', value: 'creator' },
  { label: '发行商', value: 'publisher' },
  { label: '系统管理员', value: 'admin' }
]

const statusOptions = [
  { label: '正常', value: 1 },
  { label: '封禁', value: 0 }
]

const orderingOptions = [
  { label: '最新注册', value: '-register_time' },
  { label: '最早注册', value: 'register_time' },
  { label: '最近登录', value: '-last_login_time' }
]

const filters = reactive({
  search: '',
  role: '',
  status: '',
  ordering: '-register_time'
})

// 用户详情
const detailDialogVisible = ref(false)
const currentUser = ref<AdminUser | null>(null)
const userOperations = ref<UserOperation[]>([])

// 修改角色
const roleDialogVisible = ref(false)
const roleForm = reactive({
  userId: 0,
  currentRole: '' as UserRole,
  newRole: '' as UserRole
})

// 修改状态
const statusDialogVisible = ref(false)
const statusForm = reactive({
  userId: 0,
  username: '',
  action: 'ban' as 'ban' | 'unban',
  currentStatus: 1 as UserStatus,
  reason: ''
})

// 获取角色标签类型
const getRoleType = (role: UserRole) => {
  const typeMap = {
    player: '',
    creator: 'success',
    publisher: 'warning',
    admin: 'danger'
  }
  return typeMap[role] || ''
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
  fetchUsers()
}

// 重置
const handleReset = () => {
  filters.search = ''
  filters.role = ''
  filters.status = ''
  filters.ordering = '-register_time'
  handleSearch()
}

// 分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchUsers()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 每页数量变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchUsers()
}

// 获取统计信息
const fetchStatistics = async () => {
  try {
    const data = await getUserStatistics()
    statistics.value = data
  } catch (error: any) {
    console.error('获取统计信息失败:', error)
  }
}

// 获取用户列表
const fetchUsers = async () => {
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
    if (filters.role) {
      params.role = filters.role
    }
    if (filters.status !== '') {
      params.status = filters.status
    }
    
    const response = await getUserList(params)
    users.value = response.results || []
    total.value = response.count || 0
  } catch (error: any) {
    ElMessage.error(error.message || '获取用户列表失败')
    users.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 查看用户详情
const viewUser = async (user: AdminUser) => {
  try {
    loading.value = true
    const [detail, operations] = await Promise.all([
      getUserDetail(user.id),
      getUserOperations(user.id)
    ])
    currentUser.value = detail
    userOperations.value = operations
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取用户详情失败')
  } finally {
    loading.value = false
  }
}

// 关闭详情对话框
const closeDetailDialog = () => {
  currentUser.value = null
  userOperations.value = []
}

// 修改角色
const changeRole = (user: AdminUser) => {
  roleForm.userId = user.id
  roleForm.currentRole = user.role
  roleForm.newRole = user.role
  roleDialogVisible.value = true
}

// 确认修改角色
const confirmChangeRole = async () => {
  if (roleForm.newRole === roleForm.currentRole) {
    ElMessage.warning('角色未改变')
    return
  }
  
  submitting.value = true
  try {
    await updateUserRole(roleForm.userId, roleForm.newRole)
    ElMessage.success('角色修改成功')
    roleDialogVisible.value = false
    fetchUsers()
    fetchStatistics()
  } catch (error: any) {
    ElMessage.error(error.message || '角色修改失败')
  } finally {
    submitting.value = false
  }
}

// 封禁/解封用户
const toggleStatus = (user: AdminUser) => {
  statusForm.userId = user.id
  statusForm.username = user.username
  statusForm.currentStatus = user.status
  statusForm.action = user.status === 1 ? 'ban' : 'unban'
  statusForm.reason = ''
  statusDialogVisible.value = true
}

// 确认封禁/解封
const confirmToggleStatus = async () => {
  if (statusForm.action === 'ban' && !statusForm.reason.trim()) {
    ElMessage.warning('请输入封禁原因')
    return
  }
  
  submitting.value = true
  try {
    const newStatus = statusForm.action === 'ban' ? 0 : 1
    await updateUserStatus(statusForm.userId, newStatus, statusForm.reason)
    ElMessage.success(statusForm.action === 'ban' ? '封禁成功' : '解封成功')
    statusDialogVisible.value = false
    fetchUsers()
    fetchStatistics()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchStatistics()
  fetchUsers()
})
</script>

<style scoped lang="scss">
.user-manage-view {
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
  
  .table-card {
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .user-text {
        flex: 1;
        
        .username {
          font-weight: bold;
          color: var(--el-text-color-primary);
          margin-bottom: 4px;
        }
        
        .email {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }
    
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
  
  .user-detail {
    .operations-section {
      margin-top: 30px;
      
      h3 {
        margin-bottom: 20px;
        font-size: 16px;
        color: var(--el-text-color-primary);
      }
      
      .operation-meta {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        margin-top: 4px;
      }
    }
  }
}
</style>

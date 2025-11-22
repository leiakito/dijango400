<template>
  <div class="system-config-view">
    <!-- 系统健康状态 -->
    <el-card class="health-card" v-loading="healthLoading">
      <template #header>
        <div class="card-header">
          <span>系统健康状态</span>
          <el-button type="primary" size="small" @click="refreshHealth">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <div class="health-content" v-if="healthData">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="health-item">
              <el-icon :size="32" :color="healthData.status === 'healthy' ? '#67C23A' : '#F56C6C'">
                <SuccessFilled v-if="healthData.status === 'healthy'" />
                <CircleCloseFilled v-else />
              </el-icon>
              <div class="health-text">
                <div class="health-label">总体状态</div>
                <div class="health-value">{{ healthData.status === 'healthy' ? '健康' : '异常' }}</div>
              </div>
            </div>
          </el-col>
          
          <el-col :span="6" v-for="(check, key) in healthData.checks" :key="key">
            <div class="health-item">
              <el-icon :size="32" :color="getCheckColor(check.status)">
                <SuccessFilled v-if="check.status === 'ok'" />
                <WarningFilled v-else-if="check.status === 'warning'" />
                <CircleCloseFilled v-else />
              </el-icon>
              <div class="health-text">
                <div class="health-label">{{ getCheckLabel(key) }}</div>
                <div class="health-value">{{ check.message }}</div>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <el-divider />
        
        <div class="system-info">
          <h4>系统信息</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Python版本">
              {{ healthData.system_info?.python_version?.split(' ')[0] || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="平台">
              {{ healthData.system_info?.platform || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间" :span="2">
              {{ formatDate(healthData.timestamp) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>
    
    <!-- Tab切换 -->
    <el-card class="content-card">
      <el-tabs v-model="activeTab">
        <!-- 系统配置 -->
        <el-tab-pane label="系统配置" name="config">
          <div class="tab-actions">
            <el-input
              v-model="configSearch"
              placeholder="搜索配置项"
              clearable
              style="width: 300px"
              @input="handleConfigSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-button type="primary" @click="handleSaveConfigs" :loading="saving">
              <el-icon><Check /></el-icon>
              保存更改
            </el-button>
          </div>
          
          <el-table 
            :data="filteredConfigs" 
            v-loading="configLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="key" label="配置键" width="250" />
            
            <el-table-column label="配置值" min-width="300">
              <template #default="{ row }">
                <el-input 
                  v-model="row.value" 
                  placeholder="请输入配置值"
                  @change="markConfigChanged(row)"
                />
              </template>
            </el-table-column>
            
            <el-table-column prop="description" label="描述" min-width="250" />
            
            <el-table-column label="公开" width="80">
              <template #default="{ row }">
                <el-switch 
                  v-model="row.is_public" 
                  @change="markConfigChanged(row)"
                />
              </template>
            </el-table-column>
            
            <el-table-column label="更新时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.updated_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <!-- 系统日志 -->
        <el-tab-pane label="系统日志" name="logs">
          <div class="tab-actions">
            <el-form :inline="true" :model="logFilters">
              <el-form-item label="日志级别">
                <el-select 
                  v-model="logFilters.level" 
                  placeholder="全部级别"
                  clearable
                  style="width: 150px"
                  @change="fetchLogs"
                >
                  <el-option label="调试" value="DEBUG" />
                  <el-option label="信息" value="INFO" />
                  <el-option label="警告" value="WARNING" />
                  <el-option label="错误" value="ERROR" />
                  <el-option label="严重" value="CRITICAL" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="模块">
                <el-input
                  v-model="logFilters.module"
                  placeholder="模块名称"
                  clearable
                  style="width: 200px"
                  @clear="fetchLogs"
                  @keyup.enter="fetchLogs"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="fetchLogs">查询</el-button>
                <el-button @click="handleCleanupLogs">清理日志</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <el-table 
            :data="logs" 
            v-loading="logLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column label="级别" width="100">
              <template #default="{ row }">
                <el-tag :type="getLogLevelType(row.level)" size="small">
                  {{ row.level }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="module" label="模块" width="150" />
            <el-table-column prop="message" label="消息" min-width="300" />
            <el-table-column prop="user_name" label="用户" width="120" />
            <el-table-column prop="ip_address" label="IP地址" width="150" />
            
            <el-table-column label="时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination" v-if="logTotal > 0">
            <el-pagination
              v-model:current-page="logPage"
              v-model:page-size="logPageSize"
              :total="logTotal"
              :page-sizes="[20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="fetchLogs"
              @size-change="fetchLogs"
            />
          </div>
        </el-tab-pane>
        
        <!-- 数据备份 -->
        <el-tab-pane label="数据备份" name="backup">
          <div class="tab-actions">
            <el-button type="primary" @click="handleCreateBackup" :loading="backupCreating">
              <el-icon><Download /></el-icon>
              创建备份
            </el-button>
          </div>
          
          <el-table 
            :data="backups" 
            v-loading="backupLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="80" />
            
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getBackupStatusType(row.status)">
                  {{ getBackupStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="文件名" min-width="300">
              <template #default="{ row }">
                <span :title="row.file_path">{{ row.file_name || row.file_path || '-' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="文件大小" width="120">
              <template #default="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>
            </el-table-column>
            
            <el-table-column label="耗时" width="100">
              <template #default="{ row }">
                {{ row.duration ? `${row.duration.toFixed(2)}s` : '-' }}
              </template>
            </el-table-column>
            
            <el-table-column label="开始时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.started_at) }}
              </template>
            </el-table-column>
            
            <el-table-column label="完成时间" width="180">
              <template #default="{ row }">
                {{ row.finished_at ? formatDate(row.finished_at) : '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Search, Check, Download,
  SuccessFilled, CircleCloseFilled, WarningFilled
} from '@element-plus/icons-vue'
import {
  getSystemHealth, getSystemConfigs, updateSystemConfig,
  batchUpdateConfigs, getSystemLogs, cleanupLogs,
  getBackupJobs, createBackup
} from '@/api/admin'

const activeTab = ref('config')

// 健康状态
const healthLoading = ref(false)
const healthData = ref<any>(null)

// 系统配置
const configLoading = ref(false)
const saving = ref(false)
const configs = ref<any[]>([])
const configSearch = ref('')
const changedConfigs = ref(new Set<string>())
const forbiddenKey = 'forbidden_words'

// 系统日志
const logLoading = ref(false)
const logs = ref<any[]>([])
const logPage = ref(1)
const logPageSize = ref(20)
const logTotal = ref(0)
const logFilters = reactive({
  level: '',
  module: ''
})

// 数据备份
const backupLoading = ref(false)
const backupCreating = ref(false)
const backups = ref<any[]>([])

// 过滤后的配置
const filteredConfigs = computed(() => {
  if (!configSearch.value) return configs.value
  const search = configSearch.value.toLowerCase()
  return configs.value.filter(config =>
    config.key.toLowerCase().includes(search) ||
    config.description?.toLowerCase().includes(search)
  )
})

// 健康检查相关
const getCheckColor = (status: string) => {
  const colorMap: Record<string, string> = {
    ok: '#67C23A',
    warning: '#E6A23C',
    error: '#F56C6C'
  }
  return colorMap[status] || '#909399'
}

const getCheckLabel = (key: string) => {
  const labelMap: Record<string, string> = {
    database: '数据库',
    cache: '缓存系统',
    storage: '存储系统'
  }
  return labelMap[key] || key
}

const refreshHealth = async () => {
  healthLoading.value = true
  try {
    healthData.value = await getSystemHealth()
  } catch (error: any) {
    ElMessage.error('获取系统状态失败')
  } finally {
    healthLoading.value = false
  }
}

// 配置相关
const fetchConfigs = async () => {
  configLoading.value = true
  try {
    const response = await getSystemConfigs({ page_size: 1000 })
    const data = response.results || []
    const hasForbidden = data.some((c: any) => c.key === forbiddenKey)
    if (!hasForbidden) {
      data.push({
        key: forbiddenKey,
        value: '["违禁","非法","敏感词"]',
        description: '违禁词列表，JSON数组或逗号分隔',
        is_public: false
      })
    }
    configs.value = data
  } catch (error: any) {
    ElMessage.error('获取配置失败')
  } finally {
    configLoading.value = false
  }
}

const handleConfigSearch = () => {
  // 实时搜索由computed处理
}

const markConfigChanged = (config: any) => {
  changedConfigs.value.add(String(config.id || config.key))
}

const handleSaveConfigs = async () => {
  if (changedConfigs.value.size === 0) {
    ElMessage.warning('没有更改需要保存')
    return
  }
  
  const configsToUpdate = configs.value.filter(c => changedConfigs.value.has(String(c.id || c.key)))
  
  saving.value = true
  try {
    await batchUpdateConfigs(configsToUpdate)
    ElMessage.success('配置保存成功')
    changedConfigs.value.clear()
    // 重新获取配置
    await fetchConfigs()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 日志相关
const getLogLevelType = (level: string) => {
  const typeMap: Record<string, any> = {
    DEBUG: 'info',
    INFO: '',
    WARNING: 'warning',
    ERROR: 'danger',
    CRITICAL: 'danger'
  }
  return typeMap[level] || ''
}

const fetchLogs = async () => {
  logLoading.value = true
  try {
    const params: any = {
      page: logPage.value,
      page_size: logPageSize.value
    }
    
    if (logFilters.level) params.level = logFilters.level
    if (logFilters.module) params.module = logFilters.module
    
    const response = await getSystemLogs(params)
    logs.value = response.results || []
    logTotal.value = response.count || 0
  } catch (error: any) {
    ElMessage.error('获取日志失败')
  } finally {
    logLoading.value = false
  }
}

const handleCleanupLogs = async () => {
  try {
    const { value } = await ElMessageBox.prompt(
      '请输入要保留最近多少天的日志',
      '清理日志',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^\d+$/,
        inputErrorMessage: '请输入有效的天数',
        inputValue: '30'
      }
    )
    
    const days = parseInt(value)
    const result = await cleanupLogs(days)
    ElMessage.success(result.message)
    fetchLogs()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('清理失败')
    }
  }
}

// 备份相关
const getBackupStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    running: 'warning',
    success: 'success',
    failed: 'danger'
  }
  return typeMap[status] || ''
}

const getBackupStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    running: '运行中',
    success: '成功',
    failed: '失败'
  }
  return labelMap[status] || status
}

const fetchBackups = async () => {
  backupLoading.value = true
  try {
    const response = await getBackupJobs({ page_size: 50 })
    backups.value = response.results || []
  } catch (error: any) {
    ElMessage.error('获取备份列表失败')
  } finally {
    backupLoading.value = false
  }
}

const handleCreateBackup = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要创建数据库备份吗？这可能需要一些时间',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    backupCreating.value = true
    const result = await createBackup()
    ElMessage.success(result.message)
    fetchBackups()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('创建备份失败')
    }
  } finally {
    backupCreating.value = false
  }
}

// 工具函数
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

const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

onMounted(() => {
  refreshHealth()
  fetchConfigs()
})
</script>

<style scoped lang="scss">
.system-config-view {
  .health-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .health-content {
      .health-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border: 1px solid var(--el-border-color);
        border-radius: 4px;
        
        .health-text {
          flex: 1;
          
          .health-label {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            margin-bottom: 4px;
          }
          
          .health-value {
            font-size: 14px;
            font-weight: 500;
            color: var(--el-text-color-primary);
          }
        }
      }
      
      .system-info {
        margin-top: 20px;
        
        h4 {
          margin-bottom: 12px;
          font-size: 14px;
          color: var(--el-text-color-primary);
        }
      }
    }
  }
  
  .content-card {
    .tab-actions {
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .el-form {
        margin-bottom: 0;
      }
    }
    
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style>

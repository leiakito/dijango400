<template>
  <div class="report-manage">
    <div class="page-header">
      <div>
        <p class="eyebrow">举报管理</p>
        <h2>举报审核</h2>
      </div>
      <el-select v-model="filters.status" placeholder="状态筛选" clearable style="width: 180px" @change="fetchReports">
        <el-option label="全部" value="" />
        <el-option label="待处理" value="pending" />
        <el-option label="已处理" value="resolved" />
      </el-select>
    </div>

    <el-card shadow="never">
      <el-table :data="reports" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="举报人" min-width="140">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :src="row.reporter?.avatar" :size="28">
                {{ row.reporter?.username?.[0] || 'U' }}
              </el-avatar>
              <span>{{ row.reporter?.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="原因" min-width="200" show-overflow-tooltip />
        <el-table-column prop="content_type" label="对象类型" width="120" />
        <el-table-column prop="object_id" label="对象ID" width="90" />
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handle_result" label="处理结果" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openHandle(row)">处理</el-button>
            <el-button size="small" type="danger" link @click="deleteReport(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="reports.length === 0 && !loading" class="empty-hint">暂无举报</div>
    </el-card>

    <el-dialog v-model="handleDialog.visible" title="处理举报" width="480px">
      <el-form :model="handleDialog.form" label-width="90px">
        <el-form-item label="状态">
          <el-select v-model="handleDialog.form.status" style="width: 100%">
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="resolved" />
          </el-select>
        </el-form-item>
        <el-form-item label="结果备注">
          <el-input
            v-model="handleDialog.form.handle_result"
            type="textarea"
            :rows="4"
            maxlength="300"
            show-word-limit
            placeholder="填写处理意见，例如删除、忽略等"
          />
        </el-form-item>
        <el-form-item label="操作">
          <el-checkbox v-model="handleDialog.form.delete_target">删除被举报内容</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="handleDialog.loading" @click="submitHandle">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getReports, updateReport, deleteReport as apiDeleteReport } from '@/api/community'

const loading = ref(false)
const reports = ref<any[]>([])
const filters = reactive({ status: '' })

const handleDialog = reactive({
  visible: false,
  loading: false,
  currentId: 0,
  form: {
    status: 'resolved',
    handle_result: '',
    delete_target: false
  }
})

const fetchReports = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filters.status) params.status = filters.status
  const resp = await getReports(params)
    reports.value = resp.results || resp || []
  } catch (error: any) {
    ElMessage.error(error?.message || '获取举报失败')
  } finally {
    loading.value = false
  }
}

const openHandle = (row: any) => {
  handleDialog.currentId = row.id
  handleDialog.form.status = row.status
  handleDialog.form.handle_result = row.handle_result || ''
  handleDialog.form.delete_target = false
  handleDialog.visible = true
}

const submitHandle = async () => {
  if (!handleDialog.currentId) return
  handleDialog.loading = true
  try {
    await updateReport(handleDialog.currentId, {
      status: handleDialog.form.status,
      handle_result: handleDialog.form.handle_result,
      action: handleDialog.form.delete_target ? 'delete_target' : undefined
    })
    ElMessage.success('处理成功')
    handleDialog.visible = false
    fetchReports()
  } catch (error: any) {
    ElMessage.error(error?.message || '处理失败')
  } finally {
    handleDialog.loading = false
  }
}

const deleteReport = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认删除该举报记录？', '提示', { type: 'warning' })
    await apiDeleteReport(row.id)
    ElMessage.success('已删除')
    fetchReports()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.message || '删除失败')
    }
  }
}

onMounted(fetchReports)
</script>

<style scoped lang="scss">
.report-manage {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.eyebrow {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  letter-spacing: 1px;
  text-transform: uppercase;
}
.user-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}
.empty-hint {
  padding: 12px;
  color: var(--el-text-color-secondary);
}
</style>

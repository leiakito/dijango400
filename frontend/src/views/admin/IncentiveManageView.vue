<template>
  <div class="incentive-manage">
    <div class="page-header">
      <div>
        <p class="eyebrow">创作者激励</p>
        <h2>激励审核与发放</h2>
      </div>
      <el-select v-model="filters.status" placeholder="状态筛选" clearable style="width: 180px" @change="fetchList">
        <el-option label="全部" value="" />
        <el-option label="已申请" value="applied" />
        <el-option label="已通过" value="approved" />
        <el-option label="已拒绝" value="rejected" />
        <el-option label="已发放" value="granted" />
      </el-select>
    </div>

    <el-alert
      type="info"
      :closable="false"
      class="formula-alert"
      title="激励金额计算公式"
      description="金额 = A * (曝光量 / 1000) + B * 点赞数 + C * 评论数（当前默认 A = 1, B = 1, C = 1，可通过后端配置调整）"
    />

    <el-card shadow="never">
      <el-table :data="list" v-loading="loading" border>
        <el-table-column prop="period" label="周期" width="120" />
        <el-table-column label="作者" min-width="140">
          <template #default="{ row }">
            <div class="author-cell">
              <el-avatar :src="row.author?.avatar" :size="32">{{ row.author?.username?.[0] }}</el-avatar>
              <span>{{ row.author?.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="exposure" label="曝光" width="90" />
        <el-table-column prop="likes" label="点赞" width="90" />
        <el-table-column prop="comments" label="评论" width="90" />
        <el-table-column prop="publish_count" label="发布数" width="90" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status).type">{{ statusTag(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reward_amount" label="金额" width="100" />
        <el-table-column prop="reason" label="备注/原因" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openReview(row)" :disabled="row.status === 'granted'">
              审核
            </el-button>
            <el-button size="small" type="success" link @click="openGrant(row)" :disabled="row.status !== 'approved'">
              发放
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="list.length === 0 && !loading" class="empty-hint">暂无激励申请</div>
    </el-card>

    <el-dialog v-model="reviewDialog.visible" title="审核申请" width="420px">
      <el-form :model="reviewDialog.form" label-width="80px">
        <el-form-item label="状态">
          <el-radio-group v-model="reviewDialog.form.status">
            <el-radio label="approved">通过</el-radio>
            <el-radio label="rejected">拒绝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="原因">
          <el-input
            v-model="reviewDialog.form.reason"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="可填写拒绝原因或备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="reviewDialog.loading" @click="submitReview">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="grantDialog.visible" title="发放激励" width="360px">
      <el-form :model="grantDialog.form" label-width="100px">
        <el-form-item label="金额">
          <el-input-number v-model="grantDialog.form.reward_amount" :min="0" :step="50" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="grantDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="grantDialog.loading" @click="submitGrant">确认发放</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getIncentiveHistory, reviewIncentive, grantIncentive } from '@/api/incentive'
import type { Incentive } from '@/types/incentive'

const list = ref<Incentive[]>([])
const loading = ref(false)
const filters = reactive({ status: '' })

const reviewDialog = reactive({
  visible: false,
  loading: false,
  currentId: 0,
  form: {
    status: 'approved',
    reason: ''
  }
})

const grantDialog = reactive({
  visible: false,
  loading: false,
  currentId: 0,
  form: {
    reward_amount: 0
  }
})

const statusTag = (status: string) => {
  const map: Record<string, { label: string; type: any }> = {
    applied: { label: '已申请', type: 'info' },
    approved: { label: '已通过', type: 'success' },
    rejected: { label: '已拒绝', type: 'danger' },
    granted: { label: '已发放', type: 'warning' }
  }
  return map[status] || { label: '未知', type: '' }
}

const fetchList = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filters.status) params.status = filters.status
    const data = await getIncentiveHistory(params)
    list.value = (data as Incentive[]) || []
  } catch (error: any) {
    ElMessage.error(error?.message || '获取激励数据失败')
  } finally {
    loading.value = false
  }
}

const openReview = (row: Incentive) => {
  reviewDialog.currentId = row.id
  reviewDialog.form.status = row.status === 'rejected' ? 'rejected' : 'approved'
  reviewDialog.form.reason = row.reason || ''
  reviewDialog.visible = true
}

const submitReview = async () => {
  if (!reviewDialog.currentId) return
  reviewDialog.loading = true
  try {
    await reviewIncentive(reviewDialog.currentId, {
      status: reviewDialog.form.status as 'approved' | 'rejected',
      reason: reviewDialog.form.reason
    })
    ElMessage.success('审核已提交')
    reviewDialog.visible = false
    fetchList()
  } catch (error: any) {
    ElMessage.error(error?.message || '审核失败')
  } finally {
    reviewDialog.loading = false
  }
}

const openGrant = (row: Incentive) => {
  grantDialog.currentId = row.id
  grantDialog.form.reward_amount = row.reward_amount || 0
  grantDialog.visible = true
}

const submitGrant = async () => {
  if (!grantDialog.currentId) return
  grantDialog.loading = true
  try {
    await grantIncentive(grantDialog.currentId, {
      reward_amount: grantDialog.form.reward_amount
    })
    ElMessage.success('已标记发放')
    grantDialog.visible = false
    fetchList()
  } catch (error: any) {
    ElMessage.error(error?.message || '发放失败')
  } finally {
    grantDialog.loading = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped lang="scss">
.incentive-manage {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.formula-alert {
  margin-bottom: 12px;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.author-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-hint {
  padding: 12px;
  color: var(--el-text-color-secondary);
}
</style>

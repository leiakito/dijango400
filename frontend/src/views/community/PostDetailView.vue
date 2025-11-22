<template>
  <div class="post-detail" v-loading="loading">
    <el-card v-if="post" class="post-card" shadow="never">
      <div class="post-header">
        <el-avatar :src="post.author?.avatar" :size="48">
          {{ post.author?.username?.[0] || 'U' }}
        </el-avatar>
        <div class="meta">
          <div class="name">{{ post.author?.username }}</div>
          <div class="time">{{ formatTime(post.created_at) }}</div>
          <div class="topics" v-if="post.topics?.length">
            <el-tag
              v-for="topic in post.topics"
              :key="topic.id"
              size="small"
              type="info"
              effect="plain"
              @click="goTopic(topic.id)"
            >#{{ topic.name }}</el-tag>
          </div>
        </div>
      </div>

      <div class="content">{{ post.text }}</div>

      <div class="actions">
        <el-button text :type="post.is_liked ? 'primary' : 'default'" @click="doReaction('like')">
          <el-icon><StarFilled v-if="post.is_liked" /><Star v-else /></el-icon>
          点赞 {{ post.like_count || 0 }}
        </el-button>
        <el-button text @click="commentInputRef?.focus()">
          <el-icon><ChatDotRound /></el-icon>
          评论 {{ post.comment_count || 0 }}
        </el-button>
        <el-button text @click="openReport">
          <el-icon><WarningFilled /></el-icon>
          举报
        </el-button>
      </div>
    </el-card>

    <el-card shadow="never" class="comment-card">
      <div class="comment-header">
        <h3>评论</h3>
        <el-select v-model="commentOrdering" placeholder="排序" size="small" @change="fetchComments">
          <el-option label="按时间" value="time" />
          <el-option label="按热度" value="hot" />
        </el-select>
      </div>

      <div class="comment-editor" v-if="userStore.isLoggedIn">
        <el-input
          ref="commentInputRef"
          v-model="commentContent"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="发表评论..."
        />
        <div class="comment-actions">
          <el-button type="primary" @click="submitComment" :loading="commentSubmitting">发布</el-button>
        </div>
      </div>
      <div v-else class="login-tip">
        <el-button type="primary" @click="router.push('/auth/login')">登录后评论</el-button>
      </div>

      <el-skeleton :loading="commentLoading" animated :rows="4">
        <div v-if="comments.length === 0" class="empty">暂无评论</div>
        <div v-else class="comment-list">
          <CommentNode
            v-for="item in comments"
            :key="item.id"
            :comment="item"
            :depth="1"
            :current-user-id="userStore.userInfo?.id"
            :is-admin="userStore.isAdmin"
            @reply="setReply"
            @delete="deleteCommentItem"
          />
        </div>
      </el-skeleton>
    </el-card>

    <el-dialog v-model="reportDialog.visible" title="举报" width="420px">
      <el-form :model="reportDialog.form" label-width="80px">
        <el-form-item label="原因">
          <el-select v-model="reportDialog.form.reason" placeholder="请选择原因" style="width: 100%">
            <el-option label="广告" value="ad" />
            <el-option label="辱骂" value="abuse" />
            <el-option label="侵权" value="infringement" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="reportDialog.form.content" type="textarea" :rows="3" maxlength="300" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="reportDialog.loading" @click="submitReport">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPostDetail, getComments, createComment, toggleReaction, deleteComment as apiDeleteComment, reportContent } from '@/api/community'
import { Star, StarFilled, ChatDotRound, WarningFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import type { Post, Comment } from '@/types/community'
import CommentNode from '@/components/CommentNode.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const post = ref<Post | null>(null)
const loading = ref(false)
const commentLoading = ref(false)
const commentSubmitting = ref(false)
const comments = ref<Comment[]>([])
const commentContent = ref('')
const commentOrdering = ref<'time' | 'hot'>('time')
const replyTo = ref<Comment | null>(null)
const commentInputRef = ref()

const reportDialog = ref({
  visible: false,
  loading: false,
  form: {
    reason: '',
    content: ''
  }
})

const formatTime = (time?: string) => {
  if (!time) return ''
  const d = new Date(time)
  return d.toLocaleString()
}

const fetchDetail = async () => {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const data = await getPostDetail(id)
    post.value = data as Post
  } catch (error: any) {
    ElMessage.error(error?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const fetchComments = async () => {
  if (!post.value) return
  commentLoading.value = true
  try {
    const resp = await getComments({
      target: 'post',
      target_id: post.value.id,
      ordering: commentOrdering.value === 'hot' ? 'hot' : undefined
    } as any)
    comments.value = resp.results || resp || []
    if (post.value && Array.isArray(comments.value)) {
      post.value.comment_count = comments.value.length
    }
  } catch (error: any) {
    ElMessage.error(error?.message || '获取评论失败')
  } finally {
    commentLoading.value = false
  }
}

const submitComment = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  if (!commentContent.value.trim() || !post.value) {
    ElMessage.warning('请输入内容')
    return
  }
  commentSubmitting.value = true
  try {
    await createComment({
      content: commentContent.value.trim(),
      target: 'post',
      target_id: post.value.id,
      parent: replyTo.value?.id
    } as any)
    commentContent.value = ''
    replyTo.value = null
    ElMessage.success('评论成功')
    if (post.value) {
      post.value.comment_count = (post.value.comment_count || 0) + 1
    }
    fetchComments()
  } catch (error: any) {
    ElMessage.error(error?.message || '评论失败')
  } finally {
    commentSubmitting.value = false
  }
}

const setReply = (comment: Comment) => {
  replyTo.value = comment
  commentContent.value = ''
}

const clearReply = () => {
  replyTo.value = null
  commentContent.value = ''
}

const doReaction = async (type: 'like' | 'dislike') => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  if (!post.value) return
  try {
    const resp = await toggleReaction({ content_type: 'post', object_id: post.value.id, reaction_type: type })
    post.value.like_count = resp.like_count ?? post.value.like_count
    post.value.is_liked = resp.is_liked
  } catch (error: any) {
    ElMessage.error(error?.message || '操作失败')
  }
}

const deleteCommentItem = async (comment: Comment) => {
  try {
    await apiDeleteComment(comment.id)
    ElMessage.success('已删除')
    if (post.value) {
      post.value.comment_count = Math.max(0, (post.value.comment_count || 0) - 1)
    }
    fetchComments()
  } catch (error: any) {
    ElMessage.error(error?.message || '删除失败')
  }
}

const openReport = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  reportDialog.value.visible = true
  reportDialog.value.form.reason = ''
  reportDialog.value.form.content = ''
}

const submitReport = async () => {
  if (!post.value) return
  if (!reportDialog.value.form.reason) {
    ElMessage.warning('请选择原因')
    return
  }
  reportDialog.value.loading = true
  try {
    await reportContent({
      target_type: 'post',
      target_id: post.value.id,
      reason: reportDialog.value.form.reason,
      content: reportDialog.value.form.content || reportDialog.value.form.reason
    } as any)
    ElMessage.success('已提交举报')
    reportDialog.value.visible = false
  } catch (error: any) {
    ElMessage.error(error?.message || '提交失败')
  } finally {
    reportDialog.value.loading = false
  }
}

const goTopic = (id: number) => {
  router.push(`/community/posts?topic=${id}`)
}

onMounted(() => {
  fetchDetail()
  fetchComments()
})
</script>

<style scoped lang="scss">
.post-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-card {
  .post-header {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
    align-items: center;
  }
  .meta {
    flex: 1;
    .name { font-weight: 700; }
    .time { color: var(--el-text-color-secondary); font-size: 13px; }
    .topics { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
  }
  .content {
    font-size: 16px;
    line-height: 1.7;
    margin-bottom: 12px;
    white-space: pre-wrap;
  }
  .actions {
    display: flex;
    gap: 8px;
  }
}

.comment-card {
  .comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  .comment-editor {
    margin-bottom: 12px;
  }
  .comment-actions {
    margin-top: 6px;
    display: flex;
    justify-content: flex-end;
  }
  .login-tip {
    margin-bottom: 12px;
  }
  .comment-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .comment-item {
    display: flex;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    background: var(--el-fill-color-light);
  }
  .comment-body {
    flex: 1;
    .comment-meta {
      display: flex;
      gap: 8px;
      color: var(--el-text-color-secondary);
      font-size: 13px;
    }
    .comment-text {
      margin: 6px 0;
      line-height: 1.6;
    }
    .comment-actions {
      display: flex;
      gap: 8px;
    }
    .reply {
      margin-top: 8px;
    }
  }
  .empty {
    text-align: center;
    color: var(--el-text-color-secondary);
  }
}
</style>

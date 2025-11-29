<template>
  <div class="comment-item" :style="{ marginLeft: (depth - 1) * 16 + 'px' }">
    <el-avatar :src="comment.user?.avatar" :size="36">
      {{ comment.user?.username?.[0] || 'U' }}
    </el-avatar>
    <div class="comment-body">
      <div class="comment-meta">
        <span class="name">{{ comment.user?.username }}</span>
        <el-tag
          v-if="comment.user?.role"
          size="small"
          type="info"
          class="role-tag"
        >
          {{ getRoleLabel(comment.user.role) }}
        </el-tag>
        <span class="time">{{ formatTime(comment.created_at) }}</span>
      </div>
      <div class="comment-text">{{ comment.content }}</div>
      <div class="comment-actions">
        <el-button text size="small" @click="$emit('reply', comment)">回复</el-button>
        <el-button
          text
          size="small"
          type="danger"
          v-if="isAdmin || (currentUserId && currentUserId === comment.user?.id)"
          @click="$emit('delete', comment)"
        >
          删除
        </el-button>
      </div>
      <div class="replies" v-if="comment.replies && comment.replies.length">
        <CommentNode
          v-for="child in comment.replies"
          :key="child.id"
          :comment="child"
          :depth="depth + 1"
          :current-user-id="currentUserId"
          :is-admin="isAdmin"
          @reply="$emit('reply', $event)"
          @delete="$emit('delete', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineOptions } from 'vue'
import type { Comment } from '@/types/community'

defineOptions({ name: 'CommentNode' })

defineProps<{
  comment: Comment
  depth?: number
  currentUserId?: number
  isAdmin?: boolean
}>()

const roleLabels: Record<string, string> = {
  player: '玩家',
  creator: '创作者',
  publisher: '发行商',
  admin: '管理员'
}

const formatTime = (time?: string) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

const getRoleLabel = (role?: string) => {
  if (!role) return '用户'
  return roleLabels[role] || '用户'
}
</script>

<style scoped>
.comment-item {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
}
.comment-body {
  flex: 1;
}
.comment-meta {
  display: flex;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  align-items: center;

  .role-tag {
    border-radius: 6px;
  }
}
.comment-text {
  margin: 6px 0;
  line-height: 1.6;
}
.comment-actions {
  display: flex;
  gap: 8px;
}
.replies {
  margin-top: 8px;
}
</style>

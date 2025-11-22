<template>
  <div class="profile-view" v-loading="pageLoading">
    <div class="hero-card">
      <div class="hero-text">
        <p class="eyebrow">创作者中心</p>
        <h1>{{ profileForm.username || '个人中心' }}</h1>
        <p class="subtitle">完善创作档案、联系方式与账户安全设置。</p>

        <div class="hero-meta">
          <div class="meta-item">
            <el-icon><Calendar /></el-icon>
            <div>
              <p class="label">注册时间</p>
              <p class="value">{{ formatDate(registerTime) }}</p>
            </div>
          </div>
          <div class="meta-item">
            <el-icon><Clock /></el-icon>
            <div>
              <p class="label">最后登录</p>
              <p class="value">{{ formatDate(lastLoginTime) }}</p>
            </div>
          </div>
          <el-tag v-if="userStore.isAdmin" type="danger" effect="dark">管理员</el-tag>
          <el-tag v-else-if="userStore.isCreator" type="success" effect="dark">创作者</el-tag>
          <el-tag v-else effect="plain">玩家</el-tag>
        </div>
      </div>

      <div class="hero-avatar">
        <el-upload
          class="avatar-uploader"
          action=""
          :show-file-list="false"
          :http-request="handleAvatarUpload"
          :before-upload="beforeAvatarUpload"
          :disabled="avatarLoading"
        >
          <div class="avatar-wrapper" :class="{ uploading: avatarLoading }">
            <el-avatar :size="104" :src="profileForm.avatar || userStore.userInfo?.avatar">
              {{ profileForm.username?.[0] || 'U' }}
            </el-avatar>
            <div class="overlay">
              <el-icon><Camera /></el-icon>
              <span>{{ avatarLoading ? '上传中...' : '更换头像' }}</span>
            </div>
          </div>
        </el-upload>
        <p class="hint">推荐使用 400x400 以上的方形图片</p>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="card-header">
              <div>
                <p class="eyebrow">基础资料</p>
                <h3>展示给粉丝的创作者名片</h3>
              </div>
              <el-tag effect="plain">可公开</el-tag>
            </div>
          </template>

          <el-form label-width="120px" :model="profileForm" class="profile-form">
            <el-form-item label="昵称">
              <el-input v-model="profileForm.username" placeholder="填写昵称" maxlength="20" show-word-limit />
            </el-form-item>
            <el-form-item label="简介 / 风格">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="4"
                maxlength="200"
                show-word-limit
                placeholder="简要介绍你的创作方向、擅长的游戏类型..."
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingBasic" @click="saveBasic">保存基础信息</el-button>
              <el-button text @click="resetProfileForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="card-header">
              <div>
                <p class="eyebrow">联系方式</p>
                <h3>绑定邮箱 / 手机号</h3>
              </div>
              <el-tag type="info" effect="plain">私密信息</el-tag>
            </div>
          </template>

          <el-form label-width="120px" :model="profileForm" class="profile-form">
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" placeholder="用于通知与安全验证">
                <template #prefix><el-icon><Message /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profileForm.phone" placeholder="用于安全验证或私信联系">
                <template #prefix><el-icon><Iphone /></el-icon></template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingContact" @click="saveContact">更新联系方式</el-button>
              <span class="form-hint">不会公开展示联系方式，除非你在内容中主动分享。</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="card-header">
              <div>
                <p class="eyebrow">账户安全</p>
                <h3>修改密码</h3>
              </div>
            </div>
          </template>

          <el-form label-width="100px" :model="passwordForm" class="password-form">
            <el-form-item label="当前密码">
              <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入当前密码" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="至少 8 位，建议数字+符号组合"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认新密码">
              <el-input v-model="passwordForm.confirm_password" type="password" placeholder="再次输入新密码" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingPassword" @click="savePassword">更新密码</el-button>
              <el-button text @click="resetPasswordForm">清空</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" class="section-card quick-actions">
          <template #header>
            <div class="card-header">
              <div>
                <p class="eyebrow">快速入口</p>
                <h3>注册 / 登录 / 安全操作</h3>
              </div>
            </div>
          </template>
          <div class="action-list">
            <div class="action-item">
              <div class="icon">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="content">
                <div class="title">重新登录</div>
                <p class="desc">切换账户或验证登录流程。</p>
                <el-button link type="primary" @click="goLogin">前往登录</el-button>
              </div>
            </div>
            <div class="action-item">
              <div class="icon">
                <el-icon><Link /></el-icon>
              </div>
              <div class="content">
                <div class="title">注册新账号</div>
                <p class="desc">体验注册流程或为团队创建账号。</p>
                <el-button link type="primary" @click="goRegister">前往注册</el-button>
              </div>
            </div>
            <div class="action-item">
              <div class="icon">
                <el-icon><Key /></el-icon>
              </div>
              <div class="content">
                <div class="title">密码修改</div>
                <p class="desc">已支持在线修改密码，提交后立即生效。</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type UploadRequestOptions } from 'element-plus'
import { Calendar, Clock, Camera, Message, Iphone, UserFilled, Link, Key } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { updateProfile, changePassword, uploadAvatar } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

const pageLoading = ref(false)
const savingBasic = ref(false)
const savingContact = ref(false)
const savingPassword = ref(false)
const avatarLoading = ref(false)

const profileForm = reactive({
  username: '',
  bio: '',
  email: '',
  phone: '',
  avatar: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const registerTime = computed(() => userStore.userInfo?.register_time || '')
const lastLoginTime = computed(() => userStore.userInfo?.last_login_time || userStore.userInfo?.last_login || '')

const formatDate = (value: string | undefined) => {
  if (!value) return '未提供'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const resetProfileForm = () => {
  const info = userStore.userInfo
  if (!info) return
  profileForm.username = info.username || ''
  profileForm.bio = info.bio || ''
  profileForm.email = info.email || ''
  profileForm.phone = info.phone || ''
  profileForm.avatar = info.avatar || ''
}

const resetPasswordForm = () => {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片文件')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB')
    return false
  }
  return true
}

const handleAvatarUpload = async (options: UploadRequestOptions) => {
  const file = options.file as File
  avatarLoading.value = true
  try {
    const resp = await uploadAvatar(file)
    const url = (resp as any).avatar || (resp as any).url || ''
    if (url) {
      profileForm.avatar = url
      userStore.updateUserInfo({ avatar: url })
    }
    ElMessage.success('头像已更新')
    options.onSuccess?.(resp as any)
  } catch (error: any) {
    options.onError?.(error)
    ElMessage.error(error?.message || '头像上传失败')
  } finally {
    avatarLoading.value = false
  }
}

const saveBasic = async () => {
  if (!profileForm.username.trim()) {
    ElMessage.warning('请输入昵称')
    return
  }
  savingBasic.value = true
  try {
    await updateProfile({
      username: profileForm.username.trim(),
      bio: profileForm.bio.trim()
    })
    userStore.updateUserInfo({
      username: profileForm.username.trim(),
      bio: profileForm.bio.trim()
    })
    ElMessage.success('基础信息已更新')
  } catch (error: any) {
    ElMessage.error(error?.message || '更新基础信息失败')
  } finally {
    savingBasic.value = false
  }
}

const saveContact = async () => {
  if (!profileForm.email && !profileForm.phone) {
    ElMessage.warning('请至少填写邮箱或手机号')
    return
  }
  savingContact.value = true
  try {
    await updateProfile({
      email: profileForm.email.trim(),
      phone: profileForm.phone.trim()
    })
    userStore.updateUserInfo({
      email: profileForm.email.trim(),
      phone: profileForm.phone.trim()
    })
    ElMessage.success('联系方式已更新')
  } catch (error: any) {
    ElMessage.error(error?.message || '更新联系方式失败')
  } finally {
    savingContact.value = false
  }
}

const savePassword = async () => {
  if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirm_password) {
    ElMessage.warning('请完整填写密码信息')
    return
  }
  if (passwordForm.new_password.length < 8) {
    ElMessage.warning('新密码长度不能少于 8 个字符')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  if (passwordForm.old_password === passwordForm.new_password) {
    ElMessage.warning('新密码不能与旧密码相同')
    return
  }

  savingPassword.value = true
  try {
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码已更新')
    resetPasswordForm()
  } catch (error: any) {
    ElMessage.error(error?.message || '修改密码失败')
  } finally {
    savingPassword.value = false
  }
}

const goLogin = () => {
  router.push({ name: 'Login' })
}

const goRegister = () => {
  router.push({ name: 'Register' })
}

onMounted(async () => {
  pageLoading.value = true
  try {
    if (!userStore.userInfo) {
      const result = await userStore.fetchUserInfo()
      if (result?.success === false && result.message) {
        ElMessage.error(result.message)
      }
    }
    resetProfileForm()
  } finally {
    pageLoading.value = false
  }
})

watch(
  () => userStore.userInfo,
  (val) => {
    if (val) resetProfileForm()
  }
)
</script>

<style scoped lang="scss">
.profile-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 24px;
  border-radius: 16px;
  background: linear-gradient(120deg, #0f1f3d, #1f4f8b);
  color: #fff;

  .hero-text {
    flex: 1;

    .eyebrow {
      margin: 0;
      font-size: 13px;
      letter-spacing: 1px;
      opacity: 0.8;
    }

    h1 {
      margin: 6px 0 4px;
      font-size: 28px;
      font-weight: 700;
    }

    .subtitle {
      margin: 0 0 12px;
      color: rgba(255, 255, 255, 0.8);
    }

    .hero-meta {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;

      .meta-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        backdrop-filter: blur(10px);

        .label {
          margin: 0;
          font-size: 12px;
          opacity: 0.8;
        }

        .value {
          margin: 2px 0 0;
          font-size: 14px;
          font-weight: 600;
        }
      }
    }
  }

  .hero-avatar {
    text-align: center;

    .avatar-wrapper {
      position: relative;
      width: 120px;
      height: 120px;
      border-radius: 20px;
      display: grid;
      place-items: center;
      border: 2px dashed rgba(255, 255, 255, 0.4);
      background: rgba(255, 255, 255, 0.08);
      transition: all 0.2s ease;
      cursor: pointer;

      &.uploading {
        opacity: 0.8;
      }

      &:hover .overlay {
        opacity: 1;
        transform: translateY(0);
      }

      .overlay {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        color: #fff;
        background: rgba(0, 0, 0, 0.35);
        border-radius: 18px;
        opacity: 0;
        transform: translateY(4px);
        transition: all 0.2s ease;
        font-size: 13px;
      }
    }

    .hint {
      margin-top: 8px;
      font-size: 12px;
      color: rgba(255, 255, 255, 0.85);
    }
  }
}

.section-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    h3 {
      margin: 2px 0 0;
    }
  }

  .profile-form,
  .password-form {
    padding-top: 8px;
  }
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.form-hint {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.quick-actions {
  .action-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .action-item {
    display: grid;
    grid-template-columns: 48px 1fr;
    gap: 12px;
    padding: 12px;
    border-radius: 12px;
    background: var(--el-fill-color-light);
    align-items: center;

    .icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: grid;
      place-items: center;
      background: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
    }

    .title {
      font-weight: 600;
      margin-bottom: 2px;
    }

    .desc {
      margin: 0 0 6px;
      color: var(--el-text-color-secondary);
    }
  }
}

@media (max-width: 960px) {
  .hero-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .section-card {
    margin-bottom: 12px;
  }
}
</style>

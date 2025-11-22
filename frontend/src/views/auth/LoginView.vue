<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <img src="@/assets/logo.svg" alt="Logo" class="logo" />
          <h2>游戏推荐平台</h2>
          <p>欢迎回来，请登录您的账户</p>
        </div>
      </template>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        size="large"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <div class="remember-row">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" :underline="false" class="forgot-link">忘记密码？</el-link>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="footer">
        <span>还没有账号？</span>
        <el-link type="primary" @click="router.push('/register')">立即注册</el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

// 本地存储的键名
const REMEMBER_KEY = 'login_remember'
const USERNAME_KEY = 'login_username'

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于 8 个字符', trigger: 'blur' }
  ]
}

// 从本地存储加载记住的用户名
const loadRememberedUsername = () => {
  try {
    const remembered = localStorage.getItem(REMEMBER_KEY)
    const savedUsername = localStorage.getItem(USERNAME_KEY)
    
    if (remembered === 'true' && savedUsername) {
      loginForm.username = savedUsername
      loginForm.remember = true
    }
  } catch (error) {
    console.error('加载记住的用户名失败:', error)
  }
}

// 保存或清除记住的用户名
const saveRememberPreference = () => {
  try {
    if (loginForm.remember) {
      localStorage.setItem(REMEMBER_KEY, 'true')
      localStorage.setItem(USERNAME_KEY, loginForm.username)
    } else {
      localStorage.removeItem(REMEMBER_KEY)
      localStorage.removeItem(USERNAME_KEY)
    }
  } catch (error) {
    console.error('保存记住我偏好失败:', error)
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      const result = await userStore.loginAction(loginForm.username, loginForm.password, loginForm.remember)
      
      loading.value = false
      
      if (result.success) {
        // 保存记住我偏好
        saveRememberPreference()
        
        ElMessage.success('登录成功')
        
        // 跳转到原页面或首页
        const redirect = route.query.redirect as string || '/home'
        router.push(redirect)
      } else {
        ElMessage.error(result.message || '登录失败')
      }
    }
  })
}

// 组件挂载时加载记住的用户名
onMounted(() => {
  loadRememberedUsername()
})
</script>

<style scoped lang="scss">
.login-container {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  
  .login-card {
    width: 100%;
    max-width: 420px;
    
    .card-header {
      text-align: center;
      
      .logo {
        width: 64px;
        height: 64px;
        margin-bottom: 16px;
      }
      
      h2 {
        margin: 0 0 8px;
        font-size: 24px;
        color: var(--el-text-color-primary);
      }
      
      p {
        margin: 0;
        font-size: 14px;
        color: var(--el-text-color-secondary);
      }
    }
    
    .remember-row {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .forgot-link {
        font-size: 14px;
        cursor: pointer;
        
        &:hover {
          opacity: 0.8;
        }
      }
    }
    
    .login-button {
      width: 100%;
    }
    
    .footer {
      text-align: center;
      font-size: 14px;
      color: var(--el-text-color-secondary);
      
      span {
        margin-right: 8px;
      }
    }
  }
}
</style>







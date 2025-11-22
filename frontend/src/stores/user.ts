/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'
import { login, register, getCurrentUser, refreshToken } from '@/api/user'
import router from '@/router'
import { setRememberEnabled, getStorage } from '@/utils/storage'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string>('')
  const refreshTokenValue = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)
  const isLoading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isCreator = computed(() => userInfo.value?.role === 'creator' || isAdmin.value)
  const isPublisher = computed(() => userInfo.value?.role === 'publisher' || isAdmin.value)

  // 登录
  const loginAction = async (username: string, password: string, remember: boolean = false) => {
    try {
      isLoading.value = true
      const response = await login({ username, password })
      
      token.value = response.access
      refreshTokenValue.value = response.refresh
      
      // 设置"记住我"状态，这将影响后续的存储策略
      setRememberEnabled(remember)
      
      // 获取用户信息
      await fetchUserInfo()
      
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message || '登录失败' }
    } finally {
      isLoading.value = false
    }
  }

  // 注册
  const registerAction = async (data: any) => {
    try {
      isLoading.value = true
      await register(data)
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message || '注册失败' }
    } finally {
      isLoading.value = false
    }
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const data = await getCurrentUser()
      userInfo.value = data
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message }
    }
  }

  // 刷新 Token
  const refreshTokenAction = async () => {
    try {
      if (!refreshTokenValue.value) {
        throw new Error('No refresh token')
      }
      const response = await refreshToken(refreshTokenValue.value)
      token.value = response.access
      return { success: true }
    } catch (error) {
      // Token 刷新失败，清除登录状态
      logout()
      return { success: false }
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    refreshTokenValue.value = ''
    userInfo.value = null
    router.push('/login')
  }

  // 更新用户信息
  const updateUserInfo = (data: Partial<UserInfo>) => {
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...data }
    }
  }

  return {
    // 状态
    token,
    refreshTokenValue,
    userInfo,
    isLoading,
    // 计算属性
    isLoggedIn,
    isAdmin,
    isCreator,
    isPublisher,
    // 方法
    loginAction,
    registerAction,
    fetchUserInfo,
    refreshTokenAction,
    logout,
    updateUserInfo
  }
}, {
  persist: {
    key: 'game-platform-user',
    storage: {
      getItem: (key: string) => {
        // 优先从 localStorage 读取，如果没有则从 sessionStorage 读取
        const item = localStorage.getItem(key) || sessionStorage.getItem(key)
        return item
      },
      setItem: (key: string, value: string) => {
        // 根据"记住我"设置选择存储位置
        const storage = getStorage()
        storage.setItem(key, value)
      },
      removeItem: (key: string) => {
        // 同时从两个存储中移除
        localStorage.removeItem(key)
        sessionStorage.removeItem(key)
      }
    },
    paths: ['token', 'refreshTokenValue', 'userInfo']
  }
})

















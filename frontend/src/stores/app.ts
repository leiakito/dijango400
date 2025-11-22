/**
 * 应用全局状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 从 localStorage 初始化主题
  const savedTheme = localStorage.getItem('theme')
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  
  // 状态
  const isDarkMode = ref(savedTheme ? savedTheme === 'dark' : systemPrefersDark)
  const sidebarCollapsed = ref(false)
  const locale = ref('zh-CN')
  const loading = ref(false)
  
  // 防抖计时器
  let updateTimer: number | null = null

  // 切换暗黑模式
  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value
    updateTheme()
  }

  // 设置暗黑模式
  const setDarkMode = (value: boolean) => {
    isDarkMode.value = value
    updateTheme()
  }

  // 更新主题（优化版本 - 快速切换，无卡顿）
  const updateTheme = () => {
    // 清除之前的计时器
    if (updateTimer) {
      clearTimeout(updateTimer)
    }
    
    const htmlElement = document.documentElement
    const isDark = isDarkMode.value
    
    // 使用 batch 操作，减少重排重绘
    if (isDark) {
      htmlElement.classList.add('dark')
    } else {
      htmlElement.classList.remove('dark')
    }
    htmlElement.style.colorScheme = isDark ? 'dark' : 'light'
    
    // 异步保存到 localStorage，避免阻塞 UI
    updateTimer = setTimeout(() => {
      try {
        localStorage.setItem('theme', isDark ? 'dark' : 'light')
      } catch (e) {
        console.warn('Failed to save theme preference', e)
      }
      updateTimer = null
    }, 50) as unknown as number
  }

  // 切换侧边栏
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // 设置语言
  const setLocale = (lang: string) => {
    locale.value = lang
  }

  // 设置全局加载状态
  const setLoading = (value: boolean) => {
    loading.value = value
  }

  return {
    // 状态
    isDarkMode,
    sidebarCollapsed,
    locale,
    loading,
    // 方法
    toggleDarkMode,
    setDarkMode,
    updateTheme,
    toggleSidebar,
    setLocale,
    setLoading
  }
}, {
  persist: {
    key: 'game-platform-app',
    storage: localStorage,
    pick: ['isDarkMode', 'sidebarCollapsed', 'locale']
  }
})










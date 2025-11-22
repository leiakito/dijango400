/**
 * 存储工具函数
 * 根据"记住我"选项决定使用 localStorage 还是 sessionStorage
 */

const REMEMBER_KEY = 'login_remember'

/**
 * 检查是否启用了"记住我"
 */
export const isRememberEnabled = (): boolean => {
  try {
    return localStorage.getItem(REMEMBER_KEY) === 'true'
  } catch {
    return false
  }
}

/**
 * 设置"记住我"状态
 */
export const setRememberEnabled = (enabled: boolean): void => {
  try {
    if (enabled) {
      localStorage.setItem(REMEMBER_KEY, 'true')
    } else {
      localStorage.removeItem(REMEMBER_KEY)
    }
  } catch (error) {
    console.error('设置记住我状态失败:', error)
  }
}

/**
 * 获取合适的存储对象
 */
export const getStorage = (): Storage => {
  return isRememberEnabled() ? localStorage : sessionStorage
}

/**
 * 存储数据，根据"记住我"状态选择存储位置
 */
export const setStorageItem = (key: string, value: string): void => {
  try {
    const storage = getStorage()
    storage.setItem(key, value)
  } catch (error) {
    console.error('存储数据失败:', error)
  }
}

/**
 * 获取存储的数据，优先从 localStorage 查找，然后是 sessionStorage
 */
export const getStorageItem = (key: string): string | null => {
  try {
    return localStorage.getItem(key) || sessionStorage.getItem(key)
  } catch {
    return null
  }
}

/**
 * 删除存储的数据，同时从两个存储中删除
 */
export const removeStorageItem = (key: string): void => {
  try {
    localStorage.removeItem(key)
    sessionStorage.removeItem(key)
  } catch (error) {
    console.error('删除存储数据失败:', error)
  }
}

/**
 * 清除所有认证相关的存储数据
 */
export const clearAuthStorage = (): void => {
  const authKeys = [
    'game-platform-user',
    'login_remember',
    'login_username'
  ]
  
  authKeys.forEach(key => {
    removeStorageItem(key)
  })
}


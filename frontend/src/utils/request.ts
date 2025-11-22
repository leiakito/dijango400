/**
 * Axios 请求配置
 * 统一处理请求拦截、响应拦截、错误处理
 */
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    
    // 自动注入 Token
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    
    // 常见成功状态码：200/201/204
    if (![200, 201, 204].includes(response.status)) {
      ElMessage.error(res?.message || '请求失败')
      return Promise.reject(new Error(res?.message || '请求失败'))
    }
    
    return res
  },
  (error) => {
    console.error('Response error:', error)
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 只有在用户已登录（有token）时才处理为"登录过期"
          const userStore = useUserStore()
          if (userStore.token) {
            ElMessage.error('登录已过期，请重新登录')
            userStore.logout() // logout 内部会跳转登录页，不需要重复跳转
          } else {
            // 未登录状态下的 401，静默处理（公开接口可能返回 401）
            console.warn('未登录状态收到 401，接口可能需要认证')
          }
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          // 404 不显示错误提示，让调用方处理
          console.warn('请求的资源不存在:', error.config?.url)
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        case 400:
          // 处理 400 错误，显示详细的验证错误信息
          if (data) {
            // 如果是对象，提取第一个错误消息
            if (typeof data === 'object') {
              const errors = []
              for (const key in data) {
                if (Array.isArray(data[key])) {
                  errors.push(...data[key])
                } else if (typeof data[key] === 'string') {
                  errors.push(data[key])
                }
              }
              if (errors.length > 0) {
                ElMessage.error(errors[0])
              } else {
                ElMessage.error('请求参数错误')
              }
            } else if (data.message || data.detail) {
              ElMessage.error(data.message || data.detail)
            } else {
              ElMessage.error('请求参数错误')
            }
          }
          break
        default:
          if (data?.message || data?.detail) {
            ElMessage.error(data.message || data.detail)
          }
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查您的网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 封装常用请求方法
export const request = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return service.get(url, config)
  },
  
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.post(url, data, config)
  },
  
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.put(url, data, config)
  },
  
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.patch(url, data, config)
  },
  
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return service.delete(url, config)
  }
}

export default service


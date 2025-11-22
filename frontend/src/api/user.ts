/**
 * 用户相关 API
 */
import { request } from '@/utils/request'
import type { LoginForm, RegisterForm, UserInfo, UserProfile } from '@/types/user'

/**
 * 用户登录
 */
export function login(data: LoginForm) {
  return request.post('/auth/login/', data)
}

/**
 * 用户注册
 */
export function register(data: RegisterForm) {
  return request.post('/users/', data)
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser(): Promise<UserInfo> {
  return request.get('/users/me/')
}

/**
 * 更新用户信息
 */
export function updateProfile(data: Partial<UserProfile>) {
  return request.patch('/users/me/', data)
}

/**
 * 修改密码
 */
export function changePassword(data: { old_password: string; new_password: string }) {
  return request.post('/users/change-password/', data)
}

/**
 * 刷新 Token
 */
export function refreshToken(refresh: string) {
  return request.post('/auth/refresh/', { refresh })
}

/**
 * 获取用户操作日志
 */
export function getUserOperations(params?: any) {
  return request.get('/users/operations/', { params })
}

/**
 * 上传头像
 */
export function uploadAvatar(file: File) {
  const formData = new FormData()
  formData.append('avatar', file)
  return request.post('/users/upload-avatar/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}



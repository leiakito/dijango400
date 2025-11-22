import { request } from '@/utils/request'

export function getIncentiveStats(params?: { period?: string; user?: number }) {
  return request.get('/content/incentives/stats/', { params })
}

export function applyIncentive(data?: { period?: string }) {
  return request.post('/content/incentives/apply/', data)
}

export function getIncentiveHistory(params?: { user?: number }) {
  return request.get('/content/incentives/history/', { params })
}

export function reviewIncentive(id: number, data: { status: 'approved' | 'rejected'; reason?: string }) {
  return request.patch(`/content/incentives/${id}/review/`, data)
}

export function grantIncentive(id: number, data: { reward_amount: number }) {
  return request.patch(`/content/incentives/${id}/grant/`, data)
}

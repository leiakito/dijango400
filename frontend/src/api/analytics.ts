import { request } from '@/utils/request'

export function getAnalyticsOverview(params?: { days?: number }) {
  return request.get('/analytics/overview/', { params })
}

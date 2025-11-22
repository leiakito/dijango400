export type IncentiveStatus = 'applied' | 'approved' | 'rejected' | 'granted'

export interface Incentive {
  id: number
  author?: any
  period: string
  exposure: number
  likes: number
  comments: number
  publish_count: number
  status: IncentiveStatus
  reason?: string
  reward_amount: number
  created_at: string
  updated_at: string
}

export interface IncentiveStats {
  period: string
  exposure: number
  likes: number
  comments: number
  publish_count: number
  eligible: boolean
  eligibility_reason: string
  latest_application?: Incentive | null
}

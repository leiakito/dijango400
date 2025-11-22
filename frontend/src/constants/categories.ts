/**
 * 游戏分类常量配置
 * 包含中英文映射和显示名称
 */

export interface Category {
  value: string // 后端存储的值（中文）
  label: string // 前端显示的标签
  enValue?: string // 英文值（备用）
}

/**
 * 游戏分类列表（基于实际数据）
 */
export const GAME_CATEGORIES: Category[] = [
  { value: 'MOBA', label: 'MOBA', enValue: 'moba' },
  { value: '动作', label: '动作', enValue: 'action' },
  { value: '冒险', label: '冒险', enValue: 'adventure' },
  { value: '角色扮演', label: 'RPG', enValue: 'rpg' },
  { value: '策略', label: '策略', enValue: 'strategy' },
  { value: '射击', label: '射击', enValue: 'fps' },
  { value: '休闲', label: '休闲', enValue: 'casual' },
  { value: '沙盒', label: '沙盒', enValue: 'sandbox' },
  { value: '卡牌', label: '卡牌', enValue: 'card' },
  { value: '格斗', label: '格斗', enValue: 'fighting' }
]

/**
 * 分类值到标签的映射
 */
export const CATEGORY_MAP: Record<string, string> = {
  'MOBA': 'MOBA',
  '动作': '动作',
  '冒险': '冒险',
  '角色扮演': 'RPG',
  '策略': '策略',
  '射击': '射击',
  '休闲': '休闲',
  '沙盒': '沙盒',
  '卡牌': '卡牌',
  '格斗': '格斗',
  // 兼容英文值
  'moba': 'MOBA',
  'action': '动作',
  'adventure': '冒险',
  'rpg': 'RPG',
  'strategy': '策略',
  'fps': '射击',
  'casual': '休闲',
  'sandbox': '沙盒',
  'card': '卡牌',
  'fighting': '格斗'
}

/**
 * 获取分类显示标签
 * @param category 分类值（中文或英文）
 * @returns 显示标签
 */
export function getCategoryLabel(category: string): string {
  return CATEGORY_MAP[category] || category
}

/**
 * 获取分类的中文值（用于API请求）
 * @param value 前端选择的值
 * @returns 后端使用的中文值
 */
export function getCategoryValue(value: string): string {
  const category = GAME_CATEGORIES.find(c => 
    c.value === value || c.enValue === value || c.label === value
  )
  return category?.value || value
}


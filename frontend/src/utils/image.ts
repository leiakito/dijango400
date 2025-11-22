/**
 * 图片 URL 处理工具
 */

/**
 * 获取完整的媒体文件 URL
 * @param path 相对路径或完整 URL
 * @returns 完整的 URL
 */
export function getMediaUrl(path: string | null | undefined): string {
  if (!path) {
    return getPlaceholderImage()
  }

  // 如果已经是完整 URL，直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }

  // 拼接后端服务器 URL
  const serverURL = import.meta.env.VITE_SERVER_URL || 'http://localhost:8000'
  // 确保路径以 / 开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${serverURL}${normalizedPath}`
}

/**
 * 获取游戏封面 URL
 * @param coverImage 封面图片路径
 * @returns 完整的 URL 或占位图
 */
export function getGameCoverUrl(coverImage: string | null | undefined): string {
  return getMediaUrl(coverImage) || getPlaceholderImage('game')
}

/**
 * 获取用户头像 URL
 * @param avatar 头像路径
 * @returns 完整的 URL 或占位图
 */
export function getUserAvatarUrl(avatar: string | null | undefined): string {
  return getMediaUrl(avatar) || getPlaceholderImage('avatar')
}

/**
 * 获取占位图
 * @param type 类型：game, avatar, banner 等
 * @returns 占位图 URL
 */
export function getPlaceholderImage(type: 'game' | 'avatar' | 'banner' = 'game'): string {
  const placeholders = {
    game: 'https://placehold.co/400x500/667eea/white?text=Game+Cover',
    avatar: 'https://placehold.co/100x100/4b5563/white?text=User',
    banner: 'https://placehold.co/1200x400/667eea/white?text=Banner'
  }
  return placeholders[type]
}

/**
 * 图片加载失败处理器
 * @param event 错误事件
 * @param fallbackUrl 备用图片 URL（可选）
 */
export function handleImageError(event: Event, fallbackUrl?: string) {
  const img = event.target as HTMLImageElement
  if (!img) return

  const placeholder = fallbackUrl || getPlaceholderImage()
  // 避免无限循环
  if (img.src !== placeholder) {
    img.src = placeholder
  }
}


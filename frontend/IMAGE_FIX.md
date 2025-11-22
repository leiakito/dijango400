# 图片加载问题修复说明

## 问题描述
热门游戏组件中的游戏封面图片无法正确加载显示。

## 根本原因

### 1. 后端问题
在推荐视图中，序列化器没有接收到 `request` 上下文，导致无法生成完整的图片 URL。

**修复前：**
```python
serializer = GameListSerializer(games, many=True)
```

**修复后：**
```python
serializer = GameListSerializer(games, many=True, context={'request': request})
```

### 2. 前端问题
- 没有正确处理相对路径和绝对路径
- 缺少图片加载失败的容错机制
- API 基础 URL 和媒体文件 URL 混淆

## 修复内容

### 后端修复

#### 1. 更新推荐视图 (`backend/apps/recommendations/views.py`)

为 `hot_games` 和 `new_games` 视图添加 request 上下文：

```python
# 热门游戏接口
@api_view(['GET'])
@permission_classes([])
def hot_games(request):
    games = recommendation_service.get_hot_games(category=category, top_k=top_k)
    serializer = GameListSerializer(games, many=True, context={'request': request})
    return Response(serializer.data)

# 最新游戏接口
@api_view(['GET'])
@permission_classes([])
def new_games(request):
    games = recommendation_service.get_new_games(category=category, top_k=top_k)
    serializer = GameListSerializer(games, many=True, context={'request': request})
    return Response(serializer.data)
```

### 前端修复

#### 1. 创建图片工具模块 (`frontend/src/utils/image.ts`)

新建统一的图片 URL 处理工具：

```typescript
// 获取完整的媒体文件 URL
export function getMediaUrl(path: string | null | undefined): string {
  if (!path) return getPlaceholderImage()
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  const serverURL = import.meta.env.VITE_SERVER_URL || 'http://localhost:8000'
  return `${serverURL}${path}`
}

// 获取游戏封面 URL
export function getGameCoverUrl(coverImage: string | null | undefined): string {
  return getMediaUrl(coverImage) || getPlaceholderImage('game')
}

// 图片加载失败处理
export function handleImageError(event: Event, fallbackUrl?: string) {
  const img = event.target as HTMLImageElement
  if (!img) return
  const placeholder = fallbackUrl || getPlaceholderImage()
  if (img.src !== placeholder) {
    img.src = placeholder
  }
}
```

#### 2. 更新首页组件 (`frontend/src/views/home/IndexView.vue`)

使用新的图片工具函数：

```vue
<template>
  <img 
    :src="getGameCoverUrl(game.cover_image)" 
    :alt="game.name"
    @error="handleImageError"
  />
</template>

<script setup>
import { getGameCoverUrl, handleImageError } from '@/utils/image'
</script>
```

#### 3. 环境变量配置

需要创建环境变量文件（注意：`.env*` 文件被 git 忽略）：

**`.env.development`**
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SERVER_URL=http://localhost:8000
```

**`.env.production`**
```env
VITE_API_BASE_URL=https://your-domain.com/api/v1
VITE_SERVER_URL=https://your-domain.com
```

## URL 结构说明

### API 请求 URL
```
http://localhost:8000/api/v1/recommend/hot/
```
使用 `VITE_API_BASE_URL` 环境变量

### 媒体文件 URL
```
http://localhost:8000/media/games/covers/2025/01/game_cover.jpg
```
使用 `VITE_SERVER_URL` 环境变量

## 测试验证

### 1. 检查后端响应
```bash
curl http://localhost:8000/api/v1/recommend/hot/
```

期望返回：
```json
{
  "results": [
    {
      "id": 1,
      "name": "游戏名称",
      "cover_image": "http://localhost:8000/media/games/covers/2025/01/cover.jpg"
    }
  ]
}
```

### 2. 检查前端显示
1. 打开浏览器开发者工具
2. 访问首页
3. 查看 Network 标签，确认图片请求正确
4. 如果图片不存在，应显示占位图

### 3. 图片加载失败测试
- 确保不存在的图片自动显示占位图
- 占位图 URL: `https://placehold.co/400x500/667eea/white?text=Game+Cover`

## 其他组件适配

以下组件也可能需要类似修复：

1. **游戏列表页** (`GameListView.vue`)
2. **游戏详情页** (`GameDetailView.vue`)
3. **推荐页面** (`RecommendView.vue`)
4. **用户头像** (各个用户相关组件)

### 使用示例

```vue
<script setup>
import { getGameCoverUrl, getUserAvatarUrl, handleImageError } from '@/utils/image'
</script>

<template>
  <!-- 游戏封面 -->
  <img :src="getGameCoverUrl(game.cover_image)" @error="handleImageError" />
  
  <!-- 用户头像 -->
  <img :src="getUserAvatarUrl(user.avatar)" @error="handleImageError" />
</template>
```

## 注意事项

1. **开发环境配置**
   - 确保后端服务运行在 `http://localhost:8000`
   - 确保 MEDIA 文件配置正确
   - 检查 CORS 配置允许前端访问

2. **生产环境配置**
   - 更新 `.env.production` 中的域名
   - 配置 Nginx 正确代理 `/media` 路径
   - 确保媒体文件可公开访问

3. **性能优化**
   - 考虑使用 CDN 托管媒体文件
   - 添加图片懒加载
   - 使用 WebP 格式提升加载速度

## 故障排查

### 问题：图片仍然不显示

1. **检查后端**
   ```bash
   # 查看游戏数据
   python manage.py shell
   >>> from apps.games.models import Game
   >>> game = Game.objects.first()
   >>> print(game.cover_image)
   >>> print(game.cover_image.url)
   ```

2. **检查 MEDIA 配置**
   ```python
   # settings/base.py
   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR.parent / 'media'
   ```

3. **检查文件权限**
   ```bash
   ls -la backend/media/games/covers/
   ```

4. **检查前端请求**
   - 打开浏览器开发者工具
   - Network 标签查看图片请求
   - 检查请求 URL 是否正确
   - 查看响应状态码

### 问题：占位图也不显示

检查网络连接，占位图使用的是外部服务 `placehold.co`。如果无法访问，可以：

1. 替换为本地占位图
2. 使用 base64 编码的占位图
3. 使用项目 assets 中的默认图片

## 相关文件

- 后端：`backend/apps/recommendations/views.py`
- 后端：`backend/apps/games/serializers.py`
- 前端：`frontend/src/utils/image.ts`
- 前端：`frontend/src/views/home/IndexView.vue`
- 配置：`backend/config/settings/base.py` (MEDIA 配置)


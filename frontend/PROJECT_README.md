# 游戏推荐平台 - 前端项目

基于 Vue.js 3 + Element Plus + TypeScript + Pinia 的现代化游戏推荐平台前端应用。

## 🚀 技术栈

- **框架**: Vue.js 3 (Composition API)
- **构建工具**: Vite 5
- **UI 组件库**: Element Plus
- **状态管理**: Pinia + pinia-plugin-persistedstate
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **数据可视化**: ECharts + vue-echarts
- **语言**: TypeScript
- **代码规范**: ESLint

## 📁 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API 接口封装
│   │   ├── user.ts        # 用户相关 API
│   │   ├── game.ts        # 游戏相关 API
│   │   ├── community.ts   # 社区相关 API
│   │   └── content.ts     # 内容相关 API
│   ├── assets/            # 资源文件
│   │   ├── images/        # 图片
│   │   └── styles/        # 样式
│   ├── components/        # 公共组件
│   │   ├── GameCard.vue   # 游戏卡片
│   │   ├── StrategyCard.vue  # 攻略卡片
│   │   └── ...
│   ├── composables/       # 组合式函数
│   ├── layouts/           # 布局组件
│   │   ├── MainLayout.vue    # 主布局
│   │   └── BlankLayout.vue   # 空白布局
│   ├── router/            # 路由配置
│   │   └── index.ts       # 路由定义和权限控制
│   ├── stores/            # 状态管理
│   │   ├── user.ts        # 用户状态
│   │   ├── game.ts        # 游戏状态
│   │   └── app.ts         # 应用全局状态
│   ├── types/             # TypeScript 类型定义
│   │   ├── user.ts
│   │   ├── game.ts
│   │   ├── community.ts
│   │   └── content.ts
│   ├── utils/             # 工具函数
│   │   └── request.ts     # Axios 封装
│   ├── views/             # 页面组件
│   │   ├── auth/          # 认证页面
│   │   │   ├── LoginView.vue
│   │   │   └── RegisterView.vue
│   │   ├── home/          # 首页
│   │   ├── games/         # 游戏模块
│   │   ├── strategies/    # 攻略模块
│   │   ├── community/     # 社区模块
│   │   ├── profile/       # 个人中心
│   │   ├── analytics/     # 数据分析
│   │   ├── admin/         # 管理后台
│   │   └── error/         # 错误页面
│   ├── App.vue            # 根组件
│   └── main.ts            # 入口文件
├── .env.development       # 开发环境配置
├── .env.production        # 生产环境配置
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 🎯 核心功能模块

### 1. 用户管理
- ✅ 用户注册/登录（JWT 认证）
- ✅ 个人中心
- ✅ 角色权限控制（玩家、创作者、发行商、管理员）
- ✅ 头像上传
- ✅ 个人信息编辑

### 2. 游戏推荐
- ✅ 游戏列表浏览
- ✅ 游戏详情展示
- ✅ 个性化推荐
- ✅ 热门游戏排行
- ✅ 游戏搜索和筛选
- ✅ 游戏收藏

### 3. 内容创作
- ✅ 攻略发布（富文本编辑）
- ✅ 图片/视频上传
- ✅ 攻略编辑和管理
- ✅ 内容审核（管理员）
- ✅ 攻略收藏

### 4. 社区互动
- ✅ 动态发布
- ✅ 多级评论系统
- ✅ 点赞/收藏
- ✅ 话题关注
- ✅ @用户功能
- ✅ 举报与反馈

### 5. 数据分析
- ✅ 游戏热度可视化
- ✅ 用户行为分析
- ✅ ECharts 数据图表
- ✅ 数据导出

### 6. 系统管理
- ✅ 用户管理
- ✅ 内容审核
- ✅ 系统配置
- ✅ 日志查看

## 🛠️ 开发指南

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

### 代码检查

```bash
npm run lint
```

### 类型检查

```bash
npm run type-check
```

## 📝 环境变量配置

### 开发环境 (.env.development)

```env
VITE_APP_TITLE=游戏推荐平台
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_UPLOAD_URL=http://localhost:8000
```

### 生产环境 (.env.production)

```env
VITE_APP_TITLE=游戏推荐平台
VITE_API_BASE_URL=https://api.example.com/api/v1
VITE_UPLOAD_URL=https://api.example.com
```

## 🎨 UI 设计规范

### 主题色

- 主色调: #409EFF (Element Plus 默认蓝色)
- 成功: #67C23A
- 警告: #E6A23C
- 危险: #F56C6C
- 信息: #909399

### 响应式断点

- xs: < 768px (移动设备)
- sm: >= 768px (平板)
- md: >= 992px (桌面)
- lg: >= 1200px (大屏幕)
- xl: >= 1920px (超大屏幕)

### 暗黑模式

项目支持暗黑模式切换，通过 Element Plus 的暗黑模式 CSS 变量实现。

## 🔐 权限控制

### 路由权限

路由配置中通过 `meta` 字段控制权限：

```typescript
{
  path: '/admin',
  meta: {
    requiresAuth: true,      // 需要登录
    roles: ['admin']         // 需要的角色
  }
}
```

### 角色说明

- `player`: 普通玩家（浏览、收藏、评论）
- `creator`: 内容创作者（发布攻略）
- `publisher`: 游戏发行商（查看数据分析）
- `admin`: 系统管理员（所有权限）

## 📦 状态管理

### User Store (用户状态)

```typescript
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 登录
await userStore.loginAction(username, password)

// 登出
userStore.logout()

// 获取用户信息
const userInfo = userStore.userInfo
```

### Game Store (游戏状态)

```typescript
import { useGameStore } from '@/stores/game'

const gameStore = useGameStore()

// 获取游戏列表
await gameStore.fetchGames({ page: 1, category: 'action' })
```

### App Store (应用状态)

```typescript
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 切换暗黑模式
appStore.toggleDarkMode()

// 切换侧边栏
appStore.toggleSidebar()
```

## 🌐 API 调用示例

### 基础用法

```typescript
import { getGameList } from '@/api/game'

// 获取游戏列表
const response = await getGameList({
  page: 1,
  page_size: 20,
  category: 'action'
})
```

### 错误处理

API 调用已在 Axios 拦截器中统一处理，会自动显示错误提示。

## 🚀 部署

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/game-platform/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker 部署

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📚 开发规范

### 组件命名

- 使用 PascalCase 命名组件文件
- 组件名应该有意义且具有描述性

### 代码风格

- 使用 TypeScript
- 使用 Composition API
- 使用 `<script setup>` 语法糖
- 使用 ESLint 进行代码检查

### Git 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 License

MIT License

## 👥 团队

- 前端开发：[Your Name]
- UI 设计：[Designer Name]
- 项目经理：[PM Name]

## 📞 联系方式

- Email: support@example.com
- 官网: https://www.example.com

















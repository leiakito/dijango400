# 游戏推荐平台

一个功能完整的游戏社区推荐系统，基于 Django + Vue.js 3 构建，提供个性化推荐、内容创作、社区互动等功能。

## 📋 项目概述

本项目是一个全栈游戏推荐平台，支持四种用户角色（普通玩家、内容创作者、游戏发行商、系统管理员），提供智能推荐算法、内容创作系统、社区互动平台和数据分析功能。

### 核心特性

- ✅ **智能推荐算法**: 基于静态热度和动态热度的混合推荐系统
- ✅ **内容创作平台**: 支持图文/视频攻略发布，内容审核机制
- ✅ **社区互动**: 动态发布、多级评论、话题关注、点赞收藏
- ✅ **数据分析**: ECharts 可视化，游戏热度分析，用户行为统计
- ✅ **权限管理**: 基于角色的访问控制（RBAC）
- ✅ **爬虫系统**: Scrapy 定时爬取第三方平台数据

## 🏗️ 技术架构

### 后端技术栈

- **框架**: Django 4.2 + Django REST Framework
- **数据库**: MySQL 8.0 (PyMySQL)
- **缓存**: Redis
- **任务队列**: Celery + Redis
- **爬虫**: Scrapy
- **认证**: JWT (djangorestframework-simplejwt)
- **API 文档**: drf-spectacular (OpenAPI 3.0)

### 前端技术栈

- **框架**: Vue.js 3 + TypeScript
- **构建工具**: Vite 5
- **UI 组件库**: Element Plus
- **状态管理**: Pinia + pinia-plugin-persistedstate
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **数据可视化**: ECharts

## 📁 项目结构

```
dijango400/
├── backend/                 # 后端项目
│   ├── apps/               # 应用模块
│   │   ├── users/          # 用户管理
│   │   ├── games/          # 游戏管理
│   │   ├── recommendations/# 推荐系统
│   │   ├── content/        # 内容创作
│   │   ├── community/      # 社区互动
│   │   ├── analytics/      # 数据分析
│   │   └── system/         # 系统管理
│   ├── config/             # 项目配置
│   ├── crawlers/           # Scrapy 爬虫
│   ├── scripts/            # 工具脚本
│   ├── .env                # 环境变量
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── api/           # API 接口
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 公共组件
│   │   ├── layouts/       # 布局组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── types/         # TypeScript 类型
│   │   ├── utils/         # 工具函数
│   │   └── views/         # 页面组件
│   ├── .env.development   # 开发环境配置
│   └── package.json       # npm 依赖
│
├── start-dev.sh           # 开发环境启动脚本
└── SETUP_COMPLETE.md      # 配置完成说明
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis (可选，用于缓存和 Celery)

### 一键启动（推荐）

```bash
# 赋予执行权限
chmod +x start-dev.sh

# 启动所有服务
./start-dev.sh
```

### 手动启动

#### 1. 后端启动

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux

# 启动 Django 服务
python manage.py runserver
```

#### 2. 前端启动

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

### 访问地址

- 前端应用: http://localhost:5173
- 后端 API: http://localhost:8000/api/v1
- API 文档: http://localhost:8000/api/v1/schema/swagger-ui/
- 管理后台: http://localhost:8000/admin

### 默认账户

**管理员账户**
- 用户名: `admin`
- 密码: `admin123456`
- 邮箱: `admin@example.com`

## 📚 功能模块

### 1. 用户管理 (users)

- 用户注册/登录（JWT 认证）
- 四种角色：普通玩家、内容创作者、发行商、管理员
- 个人中心、头像上传
- 用户操作日志

### 2. 游戏管理 (games)

- 游戏列表浏览、搜索、筛选
- 游戏详情展示
- 游戏收藏功能
- 标签、分类、发行商管理

### 3. 推荐系统 (recommendations)

**推荐算法**:
- 静态热度: `H_static = 0.5*D + 0.3*F + 0.2*R`
- 动态热度: `H_dynamic = Σ (0.6*L + 0.4*C) * exp(-λ*t)`
- 总热度: `H_total = α*H_static + β*H_dynamic`
- 个性化推荐: 基于标签相似度

**功能**:
- 热门游戏排行
- 个性化推荐
- 用户兴趣分析
- 每日指标统计

### 4. 内容创作 (content)

- 攻略发布（支持富文本、图片、视频）
- 攻略编辑和管理
- 内容审核机制
- 攻略收藏和点赞
- 媒体资源上传

### 5. 社区互动 (community)

- 动态发布（支持 @用户、#话题）
- 多级评论系统
- 点赞/踩功能
- 话题关注
- 举报与反馈

### 6. 数据分析 (analytics)

- 游戏热度可视化
- 用户行为分析
- 爬虫数据管理
- 数据导出功能

### 7. 系统管理 (system)

- 用户管理
- 内容审核
- 系统配置
- 日志查看
- 数据库备份

## 🔧 配置说明

### 后端配置

**数据库配置** (backend/.env):
```env
DATABASE_URL=mysql://root:1234567890@localhost:3306/game_platform?charset=utf8mb4
```

**Redis 配置**:
```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 前端配置

**开发环境** (frontend/.env.development):
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_UPLOAD_URL=http://localhost:8000
```

## 📖 API 文档

启动后端服务后访问:
- Swagger UI: http://localhost:8000/api/v1/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/v1/schema/redoc/
- OpenAPI Schema: http://localhost:8000/api/v1/schema/

## 🧪 测试

### 后端测试

```bash
cd backend
python manage.py test
```

### 前端测试

```bash
cd frontend
npm run test
```

## 📦 部署

### Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 生产环境部署

详见各模块的部署文档:
- [后端部署文档](backend/README.md#部署)
- [前端部署文档](frontend/PROJECT_README.md#部署)

## 🛠️ 开发指南

### 代码规范

- 后端遵循 PEP 8 规范
- 前端使用 ESLint + TypeScript
- 提交遵循 Conventional Commits 规范

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

## 📝 待完成功能

根据当前进度，以下功能需要继续开发：

- [ ] 攻略列表页面
- [ ] 攻略详情页面
- [ ] 攻略编辑页面（富文本编辑器）
- [ ] 社区动态列表
- [ ] 动态详情页面
- [ ] 话题广场页面
- [ ] 个人中心页面
- [ ] 数据可视化仪表盘
- [ ] 管理后台页面

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License

## 👥 作者

- 开发者: [Your Name]
- 项目创建时间: 2025-11-06

## 📞 联系方式

- Email: support@example.com
- GitHub: https://github.com/yourusername/game-platform

## 🙏 致谢

感谢以下开源项目:
- Django & Django REST Framework
- Vue.js & Element Plus
- ECharts
- Scrapy

---

**最后更新**: 2025-11-06










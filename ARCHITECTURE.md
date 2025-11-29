# 项目架构总览

本文件汇总前后端整体架构、关键目录、运行方式、接口约定与推荐算法逻辑，便于快速理解与维护本项目。

## 项目概览

- 前端：Vue 3 + TypeScript + Vite，状态管理使用 Pinia，路由使用 Vue Router，UI 组件库为 Element Plus；网络请求由 Axios 封装；图表与编辑器分别使用 ECharts 与 Vditor。
- 后端：Django 4.2 + Django REST Framework（DRF）；认证使用 `djangorestframework-simplejwt` 的 JWT；接口文档由 `drf-spectacular` 提供；异步任务由 Celery + Redis；部署可用 Gunicorn + Nginx。
- 接口统一前缀：`/api/v1/`，前端通过环境变量 `VITE_API_BASE_URL` 连接后端。

## 目录结构（核心）

- 根目录
  - `frontend/`：前端工程（Vite 项目）。
  - `backend/`：后端工程（Django 项目）。
  - `start-dev.sh`：一键启动本地前后端开发环境。
  - 文档与说明：`README.md`、`PROJECT_README.md` 等。
- 前端核心目录（`frontend/src/`）
  - `api/`：接口定义与分模块封装。
  - `utils/request.ts`：Axios 实例、拦截器与通用请求方法。
  - `stores/`：Pinia 全局状态（`user.ts`、`app.ts`、`game.ts`）。
  - `router/`：路由配置与鉴权（`index.ts`）。
  - `views/`：页面视图（主页、列表、详情等）。
  - `styles/`、`components/`、`layouts/`：样式、组件与布局。
- 后端核心目录（`backend/`）
  - `config/urls.py`：URL 路由与子应用聚合、文档、健康检查。
  - `config/settings/`：`dev.py`、`prod.py` 环境差异与安全策略。
  - `apps/`：业务子应用（`games`、`recommendations`、`content`、`community`、`users`、`analytics`、`system`）。
  - `openapi/`：接口文档生成相关。
  - `docker/`、`ops/`：容器与运行配置（Nginx、Gunicorn）。

## 前端架构

- 请求封装（`src/utils/request.ts`）
  - `baseURL`：`VITE_API_BASE_URL`（开发：`http://localhost:8000/api/v1`）。
  - 超时：15 秒。
  - 请求拦截：从用户状态自动注入 `Authorization: Bearer <token>`。
  - 响应拦截：统一处理 401（登录过期/未认证）、403、404、500；对 400 提取详细字段错误并提示。
  - 封装方法：`get/post/put/patch/delete` 返回统一数据结构。
- 状态管理（Pinia）
  - `stores/user.ts`：`token`、`refreshTokenValue`、`userInfo`、`isLoading`；计算属性 `isLoggedIn`、`isAdmin`、`isCreator`、`isPublisher`；动作包括登录/注册、拉取资料、刷新令牌、登出、更新资料；通过 `pinia-plugin-persistedstate` 持久化（基于“记住我”）。
  - `stores/app.ts`：暗色模式、侧栏折叠、`locale` 与全局 `loading`；主题切换包含性能优化（节流/防抖）。
- 路由与视图
  - `router/index.ts`：页面路由、权限守卫（如需）。
  - `views/home/IndexView.vue`：主页视图。说明：已根据需求移除手动刷新时的覆盖层动画，仅保留分区 loading 遮罩与刷新按钮旋转，慢速刷新逻辑仍保留。
- 环境变量与构建
  - `.env.development`：`VITE_API_BASE_URL=http://localhost:8000/api/v1`、`VITE_UPLOAD_URL=http://localhost:8000`。
  - `.env.production`：`VITE_API_BASE_URL=https://api.example.com/api/v1`、`VITE_UPLOAD_URL=https://api.example.com`。

## 后端架构

- 路由与版本（`backend/config/urls.py`）
  - 统一前缀：`/api/v1/`，包含 `users`、`games`、`recommend`、`content`、`community`、`analytics`、`system` 等子应用路由。
  - 认证：登录与令牌刷新（JWT）。
  - 文档：`/api/v1/schema/`、`/api/v1/swagger/`、`/api/v1/redoc/`。
  - 健康检查：`/api/v1/health/`。
  - 开发模式下服务静态与媒体文件。
- 设置差异（`config/settings/dev.py` vs `prod.py`）
  - `dev.py`：`DEBUG=True`，CORS 允许 `localhost:5173`；日志 `DEBUG`；控制台邮件；不强制安全。
  - `prod.py`：`DEBUG=False`，开启 SSL 重定向、安全 Cookie、XSS 过滤、HSTS；日志 `WARNING` 并单独记录请求错误；邮件使用 SMTP（读环境变量）。
- 游戏模块（`apps/games`）
  - `urls.py`：`DefaultRouter` 注册 `publishers/`、`tags/`、`single-player-rankings/`、`games/`；将 `GameViewSet` 注册在最后以避免拦截其他路由。
  - `views.py`：
    - `GameViewSet`：公开读；发布者/管理员写；`collect` 动作用于用户收藏（需登录）。
    - `PublisherViewSet`、`TagViewSet`：只读。
    - `SinglePlayerRankingViewSet`：只读，支持来源与数量过滤。
- 推荐与个性化（`apps/recommendations/services.py`）
  - 静态热度：`H_static = w_d*D + w_f*F + w_r*R`（下载/关注/评论计权）。
  - 动态热度：基于帖子点赞/评论的时间衰减累计（指数衰减，最近 N 天）。
  - 总热度：`H_total = α*H_static + β*H_dynamic`；支持批量更新与榜单缓存（热门/最新）。
  - 用户兴趣：根据收藏游戏、收藏攻略关联游戏、点赞帖子关联游戏的标签权重（归一化）。
  - 相似度：用户兴趣向量与游戏标签的余弦相似度（排除已收藏）。
  - 个性化推荐：生成并持久化推荐记录，默认 `top_k`，缓存 30 分钟；提供强制刷新与缓存清理。

## 数据流示例

- 登录与令牌
  - 前端登录成功后保存 `token` 与 `refreshTokenValue`；请求拦截器自动注入 `Authorization`；401 时尝试刷新令牌或引导登录。
- 个性化推荐
  - 用户行为（收藏、点赞帖子等）→ 更新兴趣向量 → 计算与游戏标签相似度 → 按分数降序生成推荐与缓存；行为变更时清除相关缓存。
- 收藏行为影响
  - 发生收藏/取消收藏后，后端清理用户推荐记录与缓存；前端刷新推荐列表。

## 开发与运行

- 一键启动（`start-dev.sh`）
  - 启动后端 Django：`http://localhost:8000`（含 `api/v1/`、文档与健康检查）。
  - 启动前端 Vite：`http://localhost:5173`。
  - 自动安装依赖与检查虚拟环境。
- 依赖
  - 后端：见 `backend/requirements.txt`（Django/DRF/JWT/Spectacular/Celery/Redis/Pillow/Scrapy/Gunicorn）。
  - 前端：见 `frontend/package.json`（Vue/Pinia/Router/Element Plus/Axios/ECharts/Vditor 等）。
## 接口约定
- 基础
  - 前缀：`/api/v1/`；需认证的接口使用 `Authorization: Bearer <token>`。
  - 常用地址：`/api/v1/swagger/`、`/api/v1/redoc/`、`/api/v1/health/`。
- 错误处理
  - 401：登录过期或未认证；拦截器尝试刷新或提示登录。
  - 403/404/500：统一提示。
  - 400：提取详细字段错误信息并展示。
- 示例（游戏相关）
  - 列表/详情：`GET /api/v1/games/`、`GET /api/v1/games/{id}/`。
  - 收藏：`POST /api/v1/games/{id}/collect/`（需登录）。
  - 单机榜单：`GET /api/v1/single-player-rankings/`（支持来源与数量过滤）。
## 部署与运维
- 容器与网关：`docker/compose.yml`、`docker/nginx.conf`；应用入口建议使用 Nginx 反向代理 + Gunicorn。
- 静态与媒体：生产环境下由 Nginx 提供静态与媒体文件服务；后端配置静态/媒体根目录。
- 异步任务：Celery + Redis；建议在推荐热度批量更新、定时任务与爬虫任务中使用。
- 日志：`config/logging.conf` 与 `prod.py` 的请求错误文件日志；建议对关键操作与异常进行结构化日志。
## 常用地址（开发）
- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000`
- Swagger：`http://localhost:8000/api/v1/swagger/`
- Redoc：`http://localhost:8000/api/v1/redoc/`
- 健康检查：`http://localhost:8000/api/v1/health/`

## 游戏截图功能（新增）

### 后端实现
- **模型**：`GameScreenshot` 模型支持游戏截图的存储与管理
  - 字段：`game`（外键）、`image`（图片文件）、`title`（标题）、`description`（描述）、`order`（排序）
  - 存储路径：`games/screenshots/%Y/%m/`

- **序列化器**
  - `GameScreenshotSerializer`：用于读取截图信息，包含完整的 `image_url`
  - `GameScreenshotCreateSerializer`：用于创建/更新截图

- **视图集**
  - `GameScreenshotViewSet`：完整的 CRUD 操作
    - 列表/详情：公开读取
    - 创建/更新/删除：仅发行商或管理员可操作
    - 支持按 `game_id` 过滤
    - 自动按 `game`、`order`、`created_at` 排序

- **接口**
  - `POST /api/v1/games/{id}/upload_screenshot/`：快速上传单张截图（GameViewSet 的 action）
  - `GET /api/v1/games/screenshots/?game_id={id}`：获取游戏截图列表
  - `POST /api/v1/games/screenshots/`：创建截图
  - `PATCH /api/v1/games/screenshots/{id}/`：更新截图
  - `DELETE /api/v1/games/screenshots/{id}/`：删除截图

### 前端实现
- **API 方法**（`frontend/src/api/game.ts`）
  - `uploadGameScreenshot(gameId, formData)`：上传截图
  - `getGameScreenshots(gameId)`：获取游戏截图列表
  - `deleteGameScreenshot(screenshotId)`：删除截图
  - `updateGameScreenshot(screenshotId, data)`：更新截图

- **游戏创建/编辑页面**（`GameCreateEditView.vue`）
  - 支持上传游戏封面图（单张）
  - 支持批量上传游戏截图（最多 10 张）
  - 支持删除已上传的截图
  - 支持图片预览
  - 表单验证与错误处理

- **游戏详情页面优化**
  - 从后端动态加载截图列表
  - 支持图片库预览（点击放大）
  - 优化图片加载性能（lazy loading）

- **游戏列表页面优化**
  - 添加 `loading="lazy"` 属性实现图片懒加载
  - 改进图片错误处理

- **路由**
  - `GET /games/create`：创建游戏页面（需要 publisher/admin 角色）
  - `GET /games/edit/:id`：编辑游戏页面（需要 publisher/admin 角色）

### 权限控制
- 创建/更新/删除截图：仅发行商（该游戏的发行商）或管理员
- 查看截图：公开

## 变更记录（近期）

- 主页手动刷新：移除覆盖层动画；保留分区 loading 遮罩与刷新按钮旋转；慢速刷新逻辑保留。
- **游戏截图功能**：完整实现游戏截图的上传、管理与展示功能，包括后端 API、前端页面与路由。

---

如需补充更详细的模块接口清单或组件交互图，请提出具体范围，我将完善并提交更新。


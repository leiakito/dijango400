# 游戏推荐平台后端系统

基于 Django 4.2 + DRF + MySQL 8.0 + Scrapy + Celery + Redis 的游戏推荐平台后端系统。

## 技术栈

- **框架**: Django 4.2 + Django REST framework
- **数据库**: MySQL 8.0 (InnoDB, UTF8MB4)
- **缓存**: Redis
- **任务队列**: Celery + Redis
- **爬虫**: Scrapy
- **数据分析**: Pandas
- **认证**: JWT (djangorestframework-simplejwt)
- **API文档**: drf-spectacular (OpenAPI 3.0)
- **部署**: Gunicorn + Nginx

## 功能模块

### 1. 用户管理 (users)
- 四类角色：普通玩家、内容创作者、发行商、系统管理员
- JWT 认证与 RBAC 权限控制
- 用户操作日志记录

### 2. 游戏管理 (games)
- 游戏信息管理（发行商、标签、分类）
- 游戏收藏功能
- 统计数据（下载数、关注数、评价数）

### 3. 推荐系统 (recommendations)
- **静态热度**: H_static = 0.5*D + 0.3*F + 0.2*R
- **动态热度**: H_dynamic = Σ (0.6*L + 0.4*C) * exp(-λ*t)
- **总热度**: H_total = α*H_static + β*H_dynamic
- **个性化推荐**: 基于标签相似度的"猜你喜欢"
- 可配置的算法参数

### 4. 内容创作 (content)
- 游戏攻略发布（支持富文本、图片、视频）
- 内容审核机制（自动关键词检测 + 人工审核）
- 攻略收藏和点赞

### 5. 社区互动 (community)
- 动态发布（支持 @用户、#话题）
- 多级评论系统
- 点赞/踩互动
- 话题关注
- 举报与反馈

### 6. 数据分析 (analytics)
- 定时爬取第三方平台数据（每日 02:00）
- 数据清洗与指标计算（每日 03:00）
- 可视化数据接口（ECharts）

### 7. 系统管理 (system)
- 系统日志
- 配置管理
- 数据库备份与恢复
- 创作者激励机制

## 快速开始

### 1. 环境准备

```bash
# Python 3.10+
python --version

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis 等
```

### 2. 数据库初始化

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE game_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 执行迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 3. 启动服务

```bash
# 开发环境
python manage.py runserver

# Celery Worker
celery -A config worker -l info
cd backend
./venv/bin/celery -A config worker -l info -Q analytics,recommendations,community,system,crawl,celery

# Celery Beat (定时任务)
celery -A config beat -l info

# Redis (需要单独启动)
redis-server
```

### 4. 访问系统

- **API 文档**: http://localhost:8000/api/schema/swagger/
- **管理后台**: http://localhost:8000/admin/
- **API 根路径**: http://localhost:8000/api/v1/

## API 接口

### 认证
- `POST /api/v1/auth/login/` - 登录获取 JWT Token
- `POST /api/v1/auth/refresh/` - 刷新 Token
- `POST /api/v1/auth/register/` - 用户注册

### 游戏
- `GET /api/v1/games/` - 游戏列表（支持过滤、排序）
- `GET /api/v1/games/{id}/` - 游戏详情
- `POST /api/v1/games/{id}/collect/` - 收藏游戏

### 推荐
- `GET /api/v1/recommend/hot/` - 热门游戏榜单
- `GET /api/v1/recommend/new/` - 最新游戏榜单
- `GET /api/v1/recommend/personal/` - 个性化推荐

### 内容
- `GET /api/v1/strategies/` - 攻略列表
- `POST /api/v1/strategies/` - 发布攻略
- `GET /api/v1/strategies/{id}/` - 攻略详情

### 社区
- `GET /api/v1/posts/` - 动态列表
- `POST /api/v1/posts/` - 发布动态
- `POST /api/v1/comments/` - 发表评论
- `POST /api/v1/reactions/` - 点赞/踩

### 数据分析
- `GET /api/v1/analytics/overview/` - 概览趋势
- `GET /api/v1/analytics/heatmap/` - 热度分布
- `GET /api/v1/analytics/publisher/` - 发行商统计

## 定时任务

- **02:00** - 爬取第三方平台数据
- **03:00** - 计算游戏热度和每日指标
- **03:30** - 生成个性化推荐
- **04:00** - 数据库备份
- **每小时** - 更新话题热度

## 推荐算法

### 静态热度
```python
H_static = 0.5 * 下载数 + 0.3 * 关注数 + 0.2 * 评价数
```

### 动态热度（带时间衰减）
```python
单帖分数 = 0.6 * 点赞数 + 0.4 * 评论数
衰减分数 = 单帖分数 * exp(-λ * 时间差)
H_dynamic = Σ 衰减分数
```

### 总热度
```python
H_total = α * H_static + β * H_dynamic
默认: α=0.7, β=0.3
```

### 个性化推荐
基于用户兴趣向量与游戏标签向量的余弦相似度：
```python
similarity = cos(user_vector, game_vector)
```

## 部署

### 生产环境配置

```bash
# 使用生产配置
export DJANGO_SETTINGS_MODULE=config.settings.prod

# 收集静态文件
python manage.py collectstatic --noinput

# 使用 Gunicorn 启动
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Nginx 配置
# 参考 docker/nginx.conf
```

### Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 测试

```bash
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test apps.users
```

## 数据库备份与恢复

```bash
# 备份
python scripts/db_backup.py

# 恢复
python scripts/db_backup.py restore backups/backup_20240101_120000.sql
```

## 爬虫运行

```bash
# 运行所有爬虫
python scripts/crawl_run.py

# 运行指定爬虫
python scripts/crawl_run.py steam
```

## 项目结构

```
backend/
├── apps/                    # 应用模块
│   ├── users/              # 用户管理
│   ├── games/              # 游戏管理
│   ├── recommendations/    # 推荐系统
│   ├── content/            # 内容创作
│   ├── community/          # 社区互动
│   ├── analytics/          # 数据分析
│   └── system/             # 系统管理
├── config/                  # 项目配置
│   ├── settings/           # 分环境配置
│   ├── urls.py             # 路由配置
│   ├── celery.py           # Celery 配置
│   └── permissions.py      # 权限配置
├── crawlers/               # 爬虫模块
│   └── game_crawler/       # 游戏爬虫
├── scripts/                # 运维脚本
│   ├── crawl_run.py        # 爬虫运行
│   └── db_backup.py        # 数据库备份
├── logs/                   # 日志文件
├── media/                  # 媒体文件
├── static/                 # 静态文件
├── manage.py               # Django 管理脚本
└── requirements.txt        # 依赖列表
```

## 性能指标

- 列表/搜索/推荐接口响应时间 ≤ 3s
- 页面加载时间 ≤ 5s
- 支持并发 ≥ 10 在线用户
- 峰值请求 ≥ 10 req/s

## 安全措施

- JWT Token 认证
- RBAC 权限控制
- 密码加密存储
- SQL 注入防护
- XSS 防护
- CSRF 防护
- 敏感词过滤
- 文件上传白名单

## 许可证

MIT License

## 联系方式

如有问题，请联系开发团队。


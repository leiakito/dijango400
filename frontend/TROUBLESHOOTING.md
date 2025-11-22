# 前端问题排查指南

## 🔴 问题：页面一直重定向到登录页

### 原因分析
1. 浏览器 localStorage 中可能存储了旧的或损坏的用户状态
2. Pinia store 的持久化数据可能有问题
3. 路由守卫逻辑可能有bug

### 解决方案

#### 方法1：清除浏览器缓存和 localStorage（推荐）

1. 打开浏览器开发者工具（F12 或 Cmd+Option+I）
2. 切换到 "Console" 标签页
3. 输入以下命令并回车：

```javascript
localStorage.clear()
sessionStorage.clear()
location.reload()
```

4. 页面会自动刷新，应该能看到首页了

#### 方法2：手动删除特定的 localStorage 项

在浏览器开发者工具的 Console 中执行：

```javascript
localStorage.removeItem('game-platform-user')
localStorage.removeItem('game-platform-app')
location.reload()
```

#### 方法3：使用无痕模式测试

1. 打开浏览器的无痕/隐私模式
2. 访问 http://localhost:5173
3. 这样可以排除是否是缓存问题

## 🔴 问题：页面显示空白或加载失败

### 检查步骤

1. **检查前端服务是否运行**
   ```bash
   # 在终端查看 npm run dev 是否还在运行
   # 如果没有，重新启动：
   cd /Volumes/GT/dijango400/frontend
   npm run dev
   ```

2. **检查控制台错误**
   - 打开浏览器开发者工具 (F12)
   - 查看 Console 标签页是否有红色错误信息
   - 查看 Network 标签页，看请求是否失败

3. **强制刷新页面**
   - Mac: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + Shift + R`

## 🔴 问题：API 请求失败（CORS 错误）

### 症状
控制台显示类似错误：
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/...' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

### 解决方案

1. **确认后端服务正在运行**
   ```bash
   # 检查 Django 服务器
   curl http://localhost:8000/api/v1/
   ```

2. **如果后端没运行，启动它**
   ```bash
   cd /Volumes/GT/dijango400/backend
   source venv/bin/activate
   export DJANGO_SETTINGS_MODULE=config.settings.dev
   python manage.py runserver 8000
   ```

3. **检查 CORS 配置**
   - 后端的 CORS 已经配置好了
   - 如果还有问题，检查 `backend/config/settings/dev.py`

## 🔴 问题：页面样式混乱

### 解决方案

1. **清除 Vite 缓存**
   ```bash
   cd /Volumes/GT/dijango400/frontend
   rm -rf node_modules/.vite
   npm run dev
   ```

2. **重新安装依赖**
   ```bash
   cd /Volumes/GT/dijango400/frontend
   rm -rf node_modules
   npm install
   npm run dev
   ```

## ✅ 快速修复命令

在浏览器控制台执行：

```javascript
// 清除所有存储并刷新
localStorage.clear();
sessionStorage.clear();
location.href = '/';
```

## 📝 预期的正确行为

1. 访问 `http://localhost:5173/` 应该：
   - 自动重定向到 `/home`
   - 显示带侧边栏的主布局
   - 显示首页内容（热门游戏、最新攻略、社区动态）

2. 未登录用户应该可以：
   - 浏览首页
   - 查看游戏列表
   - 查看攻略列表
   - 查看社区动态

3. 只有访问特定页面才需要登录：
   - 个性化推荐（`/games/recommend`）
   - 个人中心（`/profile`）
   - 创建攻略（`/strategies/create`）
   - 管理后台（`/admin/*`）

## 🆘 如果问题仍然存在

1. 关闭浏览器，重新打开
2. 尝试使用不同的浏览器
3. 检查终端的 npm 和 Django 服务是否有错误输出
4. 确保没有其他服务占用 5173 或 8000 端口


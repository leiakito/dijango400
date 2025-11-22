# 主题切换功能说明

## 功能概述

本项目已实现深色和浅色主题的无缝切换功能，支持以下特性：

- ✅ 全局主题切换（深色/浅色模式）
- ✅ 主题偏好持久化存储
- ✅ 自动适配系统主题偏好
- ✅ 平滑的主题切换动画
- ✅ Element Plus 组件完全适配

## 实现位置

### 1. 主题切换按钮
位于 `MainLayout.vue` 顶部导航栏右侧：
```vue
<el-switch
  v-model="appStore.isDarkMode"
  @change="appStore.updateTheme"
  inline-prompt
  :active-icon="Moon"
  :inactive-icon="Sunny"
/>
```

### 2. 状态管理
在 `stores/app.ts` 中管理主题状态：
- `isDarkMode`: 当前主题模式（true=深色，false=浅色）
- `toggleDarkMode()`: 切换主题
- `setDarkMode(value)`: 设置指定主题
- `updateTheme()`: 更新 DOM 主题类名

### 3. 主题样式
- Element Plus 深色主题样式已在 `main.ts` 中引入
- 全局过渡动画在 `assets/main.css` 中定义

## 使用方式

### 用户操作
1. 登录后，在顶部导航栏右侧找到太阳/月亮图标的开关
2. 点击开关即可切换深色/浅色主题
3. 主题选择会自动保存，下次打开自动应用

### 开发者使用
在组件中使用主题状态：

```typescript
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 获取当前主题
console.log(appStore.isDarkMode) // true 或 false

// 切换主题
appStore.toggleDarkMode()

// 设置特定主题
appStore.setDarkMode(true)  // 设置为深色
appStore.setDarkMode(false) // 设置为浅色
```

## 技术实现

### 1. 初始化逻辑
```typescript
// 优先使用保存的主题，否则使用系统主题偏好
const savedTheme = localStorage.getItem('theme')
const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
const isDarkMode = ref(savedTheme ? savedTheme === 'dark' : systemPrefersDark)
```

### 2. 主题应用
```typescript
const updateTheme = () => {
  const htmlElement = document.documentElement
  if (isDarkMode.value) {
    htmlElement.classList.add('dark')
    htmlElement.style.colorScheme = 'dark'
  } else {
    htmlElement.classList.remove('dark')
    htmlElement.style.colorScheme = 'light'
  }
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}
```

### 3. 持久化存储
使用 `pinia-plugin-persistedstate` 自动保存主题设置：
```typescript
{
  persist: {
    key: 'game-platform-app',
    storage: localStorage,
    pick: ['isDarkMode', 'sidebarCollapsed', 'locale']
  }
}
```

## 浏览器兼容性

- ✅ Chrome 76+
- ✅ Firefox 67+
- ✅ Safari 12.1+
- ✅ Edge 79+

## 注意事项

1. 主题切换会应用到所有 Element Plus 组件
2. 自定义组件应使用 Element Plus 的 CSS 变量以适配主题
3. 图片和图标建议使用 SVG 格式，便于主题适配

## CSS 变量参考

Element Plus 提供的主题变量示例：
```css
/* 文本颜色 */
--el-text-color-primary
--el-text-color-regular
--el-text-color-secondary

/* 背景颜色 */
--el-bg-color
--el-bg-color-page
--el-fill-color-light

/* 边框颜色 */
--el-border-color
--el-border-color-light
```

在自定义样式中使用：
```css
.custom-component {
  color: var(--el-text-color-primary);
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
}
```


<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Logo" v-if="!appStore.sidebarCollapsed" />
        <span v-if="!appStore.sidebarCollapsed">游戏推荐平台</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="appStore.sidebarCollapsed"
        :router="true"
        class="sidebar-menu"
      >
        <el-menu-item index="/home">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-menu-item index="/games/list">
          <el-icon><Grid /></el-icon>
          <span>游戏列表</span>
        </el-menu-item>
        
        <el-menu-item index="/games/ranking">
          <el-icon><DataAnalysis /></el-icon>
          <span>单机游戏排行榜</span>
        </el-menu-item>
        
        <el-menu-item index="/games/recommend" v-if="userStore.isLoggedIn">
          <el-icon><MagicStick /></el-icon>
          <span>推荐游戏</span>
        </el-menu-item>
        
        <el-menu-item index="/strategies/list">
          <el-icon><Document /></el-icon>
          <span>游戏攻略</span>
        </el-menu-item>
        
        <el-menu-item index="/strategies/incentives" v-if="userStore.isCreator">
          <el-icon><Trophy /></el-icon>
          <span>创作者中心</span>
        </el-menu-item>
        
        <el-menu-item index="/community/posts">
          <el-icon><ChatDotRound /></el-icon>
          <span>社区动态</span>
        </el-menu-item>
        
        <el-menu-item index="/community/topics">
          <el-icon><CollectionTag /></el-icon>
          <span>话题广场</span>
        </el-menu-item>
        
        <el-menu-item index="/analytics" v-if="userStore.isAdmin || userStore.isPublisher">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
        
        <el-menu-item index="/publisher" v-if="userStore.userInfo?.role === 'publisher'">
          <el-icon><OfficeBuilding /></el-icon>
          <span>发行商中心</span>
        </el-menu-item>
        
        <el-sub-menu index="/admin" v-if="userStore.isAdmin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/admin/users">用户管理</el-menu-item>
          <el-menu-item index="/admin/content">内容审核</el-menu-item>
          <el-menu-item index="/admin/incentives">创作者激励</el-menu-item>
          <el-menu-item index="/admin/reports">举报管理</el-menu-item>
          <el-menu-item index="/admin/system">系统配置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-button
            :icon="appStore.sidebarCollapsed ? Expand : Fold"
            @click="appStore.toggleSidebar"
            text
          />
          
          <!-- 搜索框 -->
          <el-input
            v-model="searchKeyword"
            placeholder="搜索游戏、攻略..."
            :prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
            class="search-input"
          />
        </div>
        
        <div class="header-right">
          <!-- 暗黑模式切换 -->
          <el-switch
            v-model="appStore.isDarkMode"
            @change="appStore.updateTheme"
            inline-prompt
            :active-icon="Moon"
            :inactive-icon="Sunny"
          />
          
          <!-- 用户菜单 -->
          <el-dropdown v-if="userStore.isLoggedIn" trigger="click">
            <div class="user-avatar">
              <el-avatar :src="userStore.userInfo?.avatar" :size="32">
                {{ userStore.userInfo?.username?.[0] }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.username }}</span>
            </div>
            
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item @click="router.push('/strategies/create')" v-if="userStore.isCreator">
                  <el-icon><EditPen /></el-icon>
                  创作攻略
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- 未登录状态 -->
          <div v-else class="auth-buttons">
            <el-button @click="router.push('/login')" text>登录</el-button>
            <el-button @click="router.push('/register')" type="primary">注册</el-button>
          </div>
        </div>
      </el-header>
      
      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component, route }">
          <transition name="fade" mode="out-in">
            <component v-if="Component" :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import {
  HomeFilled,
  Grid,
  MagicStick,
  Document,
  ChatDotRound,
  CollectionTag,
  DataAnalysis,
  OfficeBuilding,
  Trophy,
  Setting,
  Search,
  Fold,
  Expand,
  Moon,
  Sunny,
  User,
  EditPen,
  SwitchButton
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()

const searchKeyword = ref('')

// 计算侧边栏宽度
const sidebarWidth = computed(() => appStore.sidebarCollapsed ? '64px' : '200px')

// 计算当前激活的菜单
const activeMenu = computed(() => route.path)

// 处理搜索
const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({
      name: 'GameList',
      query: { search: searchKeyword.value }
    })
  }
}

// 处理退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    userStore.logout()
    ElMessage.success('已退出登录')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  
  .sidebar {
    background-color: var(--el-bg-color);
    border-right: 1px solid var(--el-border-color);
    transition: width 0.3s;
    
    .logo {
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 0 16px;
      border-bottom: 1px solid var(--el-border-color);
      
      img {
        width: 32px;
        height: 32px;
      }
      
      span {
        font-size: 18px;
        font-weight: bold;
        color: var(--el-text-color-primary);
      }
    }
    
    .sidebar-menu {
      border-right: none;
      height: calc(100vh - 60px);
      overflow-y: auto;
    }
  }
  
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--el-bg-color);
    border-bottom: 1px solid var(--el-border-color);
    padding: 0 16px;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .search-input {
        width: 300px;
      }
    }
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .user-avatar {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        padding: 4px 12px;
        border-radius: 4px;
        transition: background-color 0.3s;
        
        &:hover {
          background-color: var(--el-fill-color-light);
        }
        
        .username {
          font-size: 14px;
        }
      }
      
      .auth-buttons {
        display: flex;
        gap: 8px;
      }
    }
  }
  
  .main-content {
    background-color: var(--el-bg-color-page);
    padding: 20px;
    overflow-y: auto;
  }
}

// 页面过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

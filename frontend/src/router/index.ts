import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

// 布局组件
const MainLayout = () => import('@/layouts/MainLayout.vue')
const BlankLayout = () => import('@/layouts/BlankLayout.vue')

// 定义路由
const routes: RouteRecordRaw[] = [
  // 主应用（带布局）
  {
    path: '/',
    component: MainLayout,
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/home/IndexView.vue'),
        meta: { title: '首页' }
      },
      
      // 游戏推荐模块
      {
        path: 'games',
        name: 'Games',
        redirect: '/games/list',
        children: [
          {
            path: 'list',
            name: 'GameList',
            component: () => import('@/views/games/GameListView.vue'),
            meta: { title: '游戏列表' }
          },
          {
            path: 'ranking',
            name: 'GameRanking',
            component: () => import('@/views/games/SinglePlayerRankingView.vue'),
            meta: { title: '单机游戏排行榜' }
          },
          {
            path: 'create',
            name: 'GameCreate',
            component: () => import('@/views/games/GameCreateEditView.vue'),
            meta: { title: '创建游戏', requiresAuth: true, roles: ['publisher', 'admin'] }
          },
          {
            path: 'edit/:id',
            name: 'GameEdit',
            component: () => import('@/views/games/GameCreateEditView.vue'),
            meta: { title: '编辑游戏', requiresAuth: true, roles: ['publisher', 'admin'] }
          },
          {
            path: ':id',
            name: 'GameDetail',
            component: () => import('@/views/games/GameDetailView.vue'),
            meta: { title: '游戏详情' }
          },
          {
            path: 'recommend',
            name: 'GameRecommend',
            component: () => import('@/views/games/RecommendView.vue'),
            meta: { title: '推荐游戏', requiresAuth: true }
          }
        ]
      },
      
      // 内容创作模块
      {
        path: 'strategies',
        name: 'Strategies',
        redirect: '/strategies/list',
        children: [
          {
            path: 'list',
            name: 'StrategyList',
            component: () => import('@/views/strategies/StrategyListView.vue'),
            meta: { title: '攻略列表' }
          },
          {
            path: ':id',
            name: 'StrategyDetail',
            component: () => import('@/views/strategies/StrategyDetailView.vue'),
            meta: { title: '攻略详情' }
          },
          {
            path: 'create',
            name: 'StrategyCreate',
            component: () => import('@/views/strategies/StrategyEditView.vue'),
            meta: { title: '创建攻略', requiresAuth: true, roles: ['creator', 'admin'] }
          },
          {
            path: 'edit/:id',
            name: 'StrategyEdit',
            component: () => import('@/views/strategies/StrategyEditView.vue'),
            meta: { title: '编辑攻略', requiresAuth: true, roles: ['creator', 'admin'] }
          },
          {
            path: 'incentives',
            name: 'CreatorIncentives',
            component: () => import('@/views/strategies/CreatorIncentiveView.vue'),
            meta: { title: '创作者激励', requiresAuth: true, roles: ['creator', 'admin'] }
          }
        ]
      },
      
      // 社区模块
      {
        path: 'community',
        name: 'Community',
        redirect: '/community/posts',
        children: [
          {
            path: 'posts',
            name: 'Posts',
            component: () => import('@/views/community/PostListView.vue'),
            meta: { title: '社区动态' }
          },
          {
            path: 'posts/:id',
            name: 'PostDetail',
            component: () => import('@/views/community/PostDetailView.vue'),
            meta: { title: '动态详情' }
          },
          {
            path: 'topics',
            name: 'Topics',
            component: () => import('@/views/community/TopicListView.vue'),
            meta: { title: '话题广场' }
          }
        ]
      },
      
      // 个人中心
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/ProfileView.vue'),
        meta: { title: '个人中心', requiresAuth: true }
      },
      
      // 数据分析（管理员/发行商）
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/analytics/AnalyticsView.vue'),
        meta: { title: '数据分析', requiresAuth: true, roles: ['admin', 'publisher'] }
      },
      {
        path: 'publisher',
        name: 'PublisherCenter',
        component: () => import('@/views/publisher/PublisherDashboardView.vue'),
        meta: { title: '发行商中心', requiresAuth: true, roles: ['publisher'] }
      },
      
      // 系统管理（管理员）
      {
        path: 'admin',
        name: 'Admin',
        redirect: '/admin/users',
        meta: { requiresAuth: true, roles: ['admin'] },
        children: [
          {
            path: 'users',
            name: 'AdminUsers',
            component: () => import('@/views/admin/UserManageView.vue'),
            meta: { title: '用户管理', requiresAuth: true, roles: ['admin'] }
          },
          {
            path: 'content',
            name: 'AdminContent',
            component: () => import('@/views/admin/ContentReviewView.vue'),
            meta: { title: '内容审核', requiresAuth: true, roles: ['admin'] }
          },
          {
            path: 'incentives',
            name: 'AdminIncentives',
            component: () => import('@/views/admin/IncentiveManageView.vue'),
            meta: { title: '创作者激励', requiresAuth: true, roles: ['admin'] }
          },
          {
            path: 'reports',
            name: 'AdminReports',
            component: () => import('@/views/admin/ReportManageView.vue'),
            meta: { title: '举报管理', requiresAuth: true, roles: ['admin'] }
          },
          {
            path: 'system',
            name: 'AdminSystem',
            component: () => import('@/views/admin/SystemConfigView.vue'),
            meta: { title: '系统配置', requiresAuth: true, roles: ['admin'] }
          }
        ]
      }
    ]
  },

  // 登录注册页面（使用空白布局）
  {
    path: '/auth',
    component: BlankLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/auth/LoginView.vue'),
        meta: { title: '登录', guest: true }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/auth/RegisterView.vue'),
        meta: { title: '注册', guest: true }
      }
    ]
  },
  
  // 兼容旧路径（重定向）
  {
    path: '/login',
    redirect: '/auth/login'
  },
  {
    path: '/register',
    redirect: '/auth/register'
  },
  
  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFoundView.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 游戏推荐平台` : '游戏推荐平台'
  
  // 等待 Pinia store 初始化
  const userStore = useUserStore()
  
  // 已登录用户访问登录/注册页，重定向到首页
  if (to.meta.guest && userStore.isLoggedIn) {
    next({ name: 'Home' })
    return
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 检查角色权限
  if (to.meta.roles && userStore.userInfo) {
    const roles = to.meta.roles as string[]
    if (!roles.includes(userStore.userInfo.role)) {
      ElMessage.error('没有权限访问该页面')
      next({ name: 'Home' })
      return
    }
  }
  
  next()
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import { useUserStore } from '@/stores/modules/user'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false
  const requiresAdmin = to.meta.requiresAdmin === true

  // 如果有 token 但没有用户信息，尝试恢复登录状态
  if (!userStore.userInfo && userStore.token) {
    try {
      await userStore.restoreSession()
    } catch (error) {
      console.error('路由守卫中恢复会话失败:', error)
      // 如果恢复失败，清除 token
      userStore.logout()
    }
  }

  // 检查是否需要登录
  if (requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 检查是否需要管理员权限
  if (requiresAdmin && userStore.userInfo?.role !== 'admin') {
    next({ name: 'MyPlants' })
    return
  }

  next()
})

export default router
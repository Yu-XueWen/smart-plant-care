/**
 * 认证逻辑组合式函数
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/modules/user'
import { isAuthenticated } from '@/utils/auth'

export function useAuth() {
  const router = useRouter()
  const userStore = useUserStore()
  
  const loading = ref(false)
  
  /**
   * 检查是否已登录
   */
  const isLoggedIn = computed(() => isAuthenticated())
  
  /**
   * 获取当前用户角色
   */
  const userRole = computed(() => userStore.userInfo?.role || null)
  
  /**
   * 检查是否为管理员
   */
  const isAdmin = computed(() => userRole.value === 'admin')
  
  /**
   * 登出
   */
  async function logout() {
    try {
      loading.value = true
      await userStore.logout()
      await router.push('/login')
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 需要登录的操作
   */
  function requireAuth(redirectUrl?: string) {
    if (!isLoggedIn.value) {
      router.push({
        path: '/login',
        query: { redirect: redirectUrl || router.currentRoute.value.fullPath }
      })
      return false
    }
    return true
  }
  
  /**
   * 需要管理员权限的操作
   */
  function requireAdmin() {
    if (!isAdmin.value) {
      router.push('/')
      return false
    }
    return true
  }
  
  return {
    loading,
    isLoggedIn,
    userRole,
    isAdmin,
    logout,
    requireAuth,
    requireAdmin
  }
}

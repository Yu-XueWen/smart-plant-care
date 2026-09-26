<template>
  <div class="layout-container" :class="{ 'mobile-layout': isMobile, 'tablet-layout': isTablet }">
    <!-- 桌面端侧边栏 -->
    <el-aside v-if="!isMobile && !isTablet" :width="isCollapse ? '64px' : '200px'" class="sidebar desktop-sidebar">
      <div class="logo">
        <el-icon v-if="!isCollapse" :size="32"><Opportunity /></el-icon>
        <span v-if="!isCollapse">植物养护</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
      >
        <!-- 普通用户菜单（所有用户都有） -->
        <el-menu-item index="/my-plants">
          <el-icon><House /></el-icon>
          <span>我的盆栽</span>
        </el-menu-item>
        
        <el-menu-item index="/identify">
          <el-icon><Camera /></el-icon>
          <span>看图识花</span>
        </el-menu-item>
        
        <el-menu-item index="/diagnose">
          <el-icon><FirstAidKit /></el-icon>
          <span>病害诊断</span>
        </el-menu-item>
        
        <el-menu-item index="/recommend">
          <el-icon><Star /></el-icon>
          <span>养花推荐</span>
        </el-menu-item>
        
        <el-menu-item index="/reminders">
          <el-icon><Bell /></el-icon>
          <span>提醒管理</span>
        </el-menu-item>
        
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>历史记录</span>
        </el-menu-item>
        
        <!-- 管理员菜单（仅管理员可见） -->
        <template v-if="userRole === 'admin'">
          <el-divider content-position="left">管理</el-divider>
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/roles">
            <el-icon><Key /></el-icon>
            <span>角色权限</span>
          </el-menu-item>
          <el-menu-item index="/admin/knowledge">
            <el-icon><Reading /></el-icon>
            <span>知识库管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/logs">
            <el-icon><Document /></el-icon>
            <span>操作日志</span>
          </el-menu-item>
          <el-menu-item index="/admin/system">
            <el-icon><Monitor /></el-icon>
            <span>系统监控</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header" :class="{ 'mobile-header': isMobile || isTablet }">
        <div class="header-left">
          <el-icon 
            v-if="!isMobile && !isTablet"
            class="collapse-btn" 
            @click="toggleCollapse"
          >
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <div v-if="isMobile || isTablet" class="mobile-logo">
            <el-icon :size="24"><Opportunity /></el-icon>
            <span class="logo-text">植物养护</span>
          </div>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="isMobile || isTablet ? 28 : 32" :src="(userInfo as any)?.avatar">
                {{ userInfo?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span v-if="!isMobile" class="username">{{ userInfo?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主要内容 -->
      <el-main class="main-content" :class="{ 'mobile-content': isMobile, 'tablet-content': isTablet }">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
      
      <!-- 移动端/平板底部导航 -->
      <div v-if="isMobile || isTablet" class="bottom-nav">
        <div 
          v-for="item in menuItems" 
          :key="item.path"
          class="nav-item"
          :class="{ active: activeMenu === item.path }"
          @click="navigateTo(item.path)"
        >
          <el-icon :size="20">
            <component :is="item.icon" />
          </el-icon>
          <span class="nav-label">{{ item.label }}</span>
        </div>
      </div>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { 
  Opportunity, House, Camera, FirstAidKit, Star, Bell, Clock,
  User, Fold, Expand, SwitchButton, DataAnalysis, Key, Reading, Document, Monitor
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/modules/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 响应式状态
const isMobile = ref(false)
const isTablet = ref(false)

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 用户信息
const userInfo = computed(() => userStore.userInfo)
const userRole = computed(() => userStore.userRole)

// 菜单项配置
const menuItems = computed(() => {
  const baseItems = [
    { path: '/my-plants', icon: House, label: '盆栽' },
    { path: '/identify', icon: Camera, label: '识花' },
    { path: '/diagnose', icon: FirstAidKit, label: '诊断' },
    { path: '/recommend', icon: Star, label: '推荐' },
    { path: '/reminders', icon: Bell, label: '提醒' }
  ]
  
  // 管理员额外添加管理菜单
  if (userRole.value === 'admin') {
    return [
      ...baseItems,
      { path: '/admin/dashboard', icon: User, label: '数据看板' },
      { path: '/admin/users', icon: User, label: '用户管理' },
      { path: '/admin/logs', icon: User, label: '操作日志' },
      { path: '/admin/system', icon: User, label: '系统监控' }
    ]
  }
  
  return baseItems
})

// 检测设备类型
const checkDeviceType = () => {
  const width = window.innerWidth
  isMobile.value = width <= 768
  isTablet.value = width > 768 && width <= 1024
}

// 导航到指定路径
const navigateTo = (path: string) => {
  router.push(path)
}

// 切换侧边栏
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      userStore.logout()
      router.push('/login')
    } catch {
      // 取消退出
    }
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

// 监听窗口大小变化
onMounted(() => {
  checkDeviceType()
  window.addEventListener('resize', checkDeviceType)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkDeviceType)
})
</script>

<style scoped lang="scss">
.layout-container {
  display: flex;
  height: 100vh;
  
  &.mobile-layout {
    .main-content {
      padding-bottom: 70px; // 为底部导航留出空间
    }
  }
  
  &.tablet-layout {
    .main-content {
      padding-bottom: 70px; // 为底部导航留出空间
    }
  }
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  :deep(.el-menu) {
    border-right: none;
    background-color: #304156;
    
    .el-menu-item {
      color: #bfcbd9;
      
      &:hover,
      &.is-active {
        background-color: #263445;
        color: #409eff;
      }
    }
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
  
  &.mobile-header {
    padding: 0 12px;
    height: 50px;
  }
  
  .header-left {
    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      transition: color 0.3s;
      
      &:hover {
        color: #409eff;
      }
    }
    
    .mobile-logo {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #409eff;
      font-weight: 600;
      
      .logo-text {
        font-size: 16px;
      }
    }
  }
  
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      
      .username {
        font-size: 14px;
        color: #606266;
      }
    }
  }
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  
  &.mobile-content {
    padding: 12px;
    transform-origin: top left;
  }
  
  &.tablet-content {
    padding: 16px;
  }
}

// 底部导航栏
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom); // 适配iPhone X等设备的底部安全区域
  
  .nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    cursor: pointer;
    transition: all 0.3s;
    color: #909399;
    padding: 8px 0;
    
    &:hover {
      color: #409eff;
    }
    
    &.active {
      color: #409eff;
      
      .nav-label {
        font-weight: 600;
      }
    }
    
    .nav-label {
      font-size: 11px;
      white-space: nowrap;
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 移动端响应式优化
@media screen and (max-width: 768px) {
  .layout-container.mobile-layout {
    .main-content {
      padding: 10px;
      
      :deep(*) {
        font-size: 14px;
      }
      
      :deep(.el-card) {
        margin-bottom: 12px;
        border-radius: 8px;
      }
      
      :deep(.el-button) {
        padding: 8px 16px;
        font-size: 13px;
      }
      
      :deep(h1) {
        font-size: 20px;
      }
      
      :deep(h2) {
        font-size: 18px;
      }
      
      :deep(h3) {
        font-size: 16px;
      }
      
      :deep(.el-input__inner),
      :deep(.el-textarea__inner) {
        font-size: 14px;
      }
    }
  }
}

// 平板端响应式优化
@media screen and (min-width: 769px) and (max-width: 1024px) {
  .layout-container.tablet-layout {
    .main-content {
      padding: 16px;
      
      :deep(*) {
        font-size: 15px;
      }
      
      :deep(.el-card) {
        margin-bottom: 16px;
      }
      
      :deep(.el-button) {
        padding: 9px 18px;
      }
      
      :deep(h1) {
        font-size: 22px;
      }
      
      :deep(h2) {
        font-size: 20px;
      }
      
      :deep(h3) {
        font-size: 18px;
      }
    }
  }
}
</style>

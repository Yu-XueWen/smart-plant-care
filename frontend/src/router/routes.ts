import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        redirect: '/my-plants',
      },
      // 普通用户路由
      {
        path: 'my-plants',
        name: 'MyPlants',
        component: () => import('@/views/user/MyPlants.vue'),
        meta: { title: '我的盆栽' },
      },
      {
        path: 'plants/:id',
        name: 'PlantDetail',
        component: () => import('@/views/user/PlantDetail.vue'),
        meta: { title: '盆栽详情' },
      },
      {
        path: 'recommend',
        name: 'Recommend',
        component: () => import('@/views/user/Recommend.vue'),
        meta: { title: '养花推荐' },
      },
      {
        path: 'identify',
        name: 'Identify',
        component: () => import('@/views/user/Identify.vue'),
        meta: { title: '看图识花' },
      },
      {
        path: 'diagnose',
        name: 'Diagnose',
        component: () => import('@/views/user/Diagnose.vue'),
        meta: { title: '病害诊断' },
      },
      {
        path: 'reminders',
        name: 'Reminders',
        component: () => import('@/views/user/Reminders.vue'),
        meta: { title: '提醒管理' },
      },
      {
        path: 'watering-reminder',
        redirect: '/reminders',  // 重定向到提醒管理
        meta: { title: '浇水提醒' },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/user/History.vue'),
        meta: { title: '历史记录' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/user/Profile.vue'),
        meta: { title: '个人资料' },
      },
      // 管理员路由
      {
        path: 'admin',
        name: 'Admin',
        redirect: '/admin/users',
        meta: { requiresAdmin: true },
        children: [
          {
            path: 'users',
            name: 'UserManage',
            component: () => import('@/views/admin/UserManage.vue'),
            meta: { title: '用户管理', requiresAdmin: true },
          },
          {
            path: 'users/:userId/plants',
            name: 'UserPlants',
            component: () => import('@/views/admin/UserPlants.vue'),
            meta: { title: '用户盆栽', requiresAdmin: true },
          },
          {
            path: 'users/:userId/records',
            name: 'UserRecords',
            component: () => import('@/views/admin/UserRecords.vue'),
            meta: { title: '用户记录', requiresAdmin: true },
          },
          {
            path: 'dashboard',
            name: 'AdminDashboard',
            component: () => import('@/views/admin/Dashboard.vue'),
            meta: { title: '统计看板', requiresAdmin: true },
          },
          {
            path: 'logs',
            name: 'AdminLogs',
            component: () => import('@/views/admin/OperationLog.vue'),
            meta: { title: '操作日志', requiresAdmin: true },
          },
          {
            path: 'system',
            name: 'AdminSystem',
            component: () => import('@/views/admin/SystemMonitor.vue'),
            meta: { title: '系统监控', requiresAdmin: true },
          },
          {
            path: 'roles',
            name: 'AdminRoles',
            component: () => import('@/views/admin/RoleManage.vue'),
            meta: { title: '角色权限', requiresAdmin: true },
          },
          {
            path: 'knowledge',
            name: 'AdminKnowledge',
            component: () => import('@/views/admin/KnowledgeManage.vue'),
            meta: { title: '知识库管理', requiresAdmin: true },
          },
        ],
      },
    ],
  },
]

export default routes
# 智能植物养护系统 — 管理员端开发计划

> **项目当前状态概览**：项目采用 FastAPI + Vue 3 + MySQL + Neo4j 架构。已有基础用户/角色模型（`user`/`admin`）、JWT 认证、管理员依赖注入、以及部分管理员路由框架（用户列表、历史查看）。前端已有管理员路由占位、API 定义和权限守卫，但均未实现具体功能。

---

## 一、总体架构设计

### 1.1 管理员端功能模块

| 模块 | 功能 | 优先级 |
|------|------|--------|
| **数据看板** | 今日新增用户数、在线用户数、总用户数、总植物数、识别/诊断统计、近期动态 | P0 |
| **用户账户管理** | 用户列表、搜索/筛选、封禁/解封、重置密码、删除用户、查看用户盆栽/记录 | P0 |
| **操作日志审计** | 管理员操作记录、登录日志、操作类型/时间/IP 记录、日志筛选与搜索 | P0 |
| **系统状态监控** | 服务器健康检查、数据库连接状态、Neo4j 状态、AI 模型状态、系统指标(CPU/内存) | P1 |
| **权限与角色管理** | 角色 CRUD、角色权限配置、用户角色分配 | P1 |
| **知识库管理** | 知识图谱中的植物/病害/虫害数据管理（扩展已有框架） | P2 |

### 1.2 技术选型补充

- **图表库**：前端新增 `echarts` 或 `@element-plus/charts` 用于看板图表
- **操作日志存储**：后端新增 `OperationLog` 模型，记录到 MySQL（不依赖外部日志系统）
- **系统监控**：后端通过 `psutil` 库获取系统指标，定期采样或实时查询

---

## 二、子任务分解（按顺序执行）

---

### 🔴 阶段一：基础建设与数据看板（P0）

#### 任务 1.1 — 后端新增数据库模型

**涉及文件**：
- `backend/app/api/models/operation_log.py`（新建）
- `backend/app/api/models/login_log.py`（新建）
- `backend/app/api/models/__init__.py`（修改，注册新模型）

**说明**：
1. 创建 `OperationLog` 模型，包含字段：
   - `id` (PK), `admin_id` (FK→user.id), `username`, `action` (操作类型如 `ban_user/unban_user/reset_password/delete_user` 等), `target_type` (操作对象类型如 `user/plant/reminder`), `target_id`, `detail` (JSON 详细描述), `ip_address`, `created_at`
2. 创建 `LoginLog` 模型，包含字段：
   - `id` (PK), `user_id` (FK→user.id), `username`, `ip_address`, `user_agent`, `login_time`, `success` (Boolean)

#### 任务 1.2 — 后端实现操作日志记录中间件/工具函数

**涉及文件**：
- `backend/app/api/services/admin_log_service.py`（新建）
- `backend/app/api/models/__init__.py`（修改）

**说明**：
- 创建 `log_admin_action()` 工具函数，供管理员端点统一调用记录操作日志
- 创建 `get_client_ip()` 工具函数从 request 中提取客户端 IP

#### 任务 1.3 — 后端管理员统计看板 API

**涉及文件**：
- `backend/app/api/v1/endpoints/admin_dashboard.py`（新建）
- `backend/app/api/v1/__init__.py`（修改，注册新路由）

**端点**：
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/admin/dashboard/overview` | 总览统计（总用户数、总植物数、总识别/诊断数） |
| GET | `/admin/dashboard/today-stats` | 今日数据（今日注册用户、今日登录用户、今日识别/诊断、今日创建植物） |
| GET | `/admin/dashboard/recent-activity` | 近期动态（最近注册用户、最近操作） |
| GET | `/admin/dashboard/chart-data` | 图表数据（近7/30天用户增长趋势、识别/诊断趋势） |

#### 任务 1.4 — 前端新增依赖与基础配置

**涉及文件**：
- `frontend/package.json`（修改，新增 `echarts` 和 `vue-echarts` 或 `@element-plus/icons-vue`）

**说明**：
- 安装 ECharts 和 Vue-ECharts 用于看板图表渲染
- 配置按需引入

#### 任务 1.5 — 前端管理员 API 扩展

**涉及文件**：
- `frontend/src/api/modules/admin.ts`（重写/扩展）

**说明**：
- 补充完整的管理员 API 方法：
  - `getDashboardOverview()`, `getTodayStats()`, `getRecentActivity()`, `getChartData(params)`
  - `getOperationLogs(params)`, `getLoginLogs(params)`
  - `resetPassword(userId, newPassword)`, `getUserDetail(userId)`
  - `getSystemStatus()`, `getSystemMetrics()`
  - `getRoles(params)`, `createRole(data)`, `updateRole(id, data)`, `deleteRole(id)`, `assignUserRole(userId, role)`

#### 任务 1.6 — 前端数据看板页面

**涉及文件**：
- `frontend/src/views/admin/Dashboard.vue`（新建）
- `frontend/src/router/routes.ts`（修改，添加 `/admin/dashboard` 路由）

**功能要求**：
- 顶部统计卡片行：总用户数、总植物数、今日新增用户、今日活跃用户、总识别次数、总诊断次数
- 用户增长趋势折线图（近7天/30天切换）
- 识别与诊断趋势对比图
- 近期动态列表（最近注册用户、最近操作）
- 使用 Element Plus Card + ECharts 实现响应式布局

---

### 🟠 阶段二：用户账户管理（P0）

#### 任务 2.1 — 后端用户管理 API 扩展

**涉及文件**：
- `backend/app/api/v1/endpoints/admin.py`（修改/扩展）

**新增端点**：
| 方法 | 路径 | 功能 |
|------|------|------|
| PUT | `/admin/users/{user_id}/status` | 封禁/解封用户（切换 status 0/1） |
| DELETE | `/admin/users/{user_id}` | 删除用户（软删除/硬删除，关联数据清理） |
| POST | `/admin/users/{user_id}/reset-password` | 重置用户密码 |
| GET | `/admin/users/{user_id}/detail` | 获取用户详细信息（含统计） |
| GET | `/admin/users/{user_id}/plants` | 获取用户盆栽列表 |
| GET | `/admin/users/{user_id}/records` | 获取用户活动记录（识别/诊断/浇水/养护） |

**注意**：调用各端点时需通过 `log_admin_action()` 记录操作日志。

#### 任务 2.2 — 前端用户管理页面

**涉及文件**：
- `frontend/src/views/admin/UserManage.vue`（重写，替换占位符）

**功能要求**：
- 用户表格展示：ID、用户名、邮箱、手机号、角色(标签)、状态(启用/禁用标签)、注册时间、最后登录时间
- 顶部搜索栏：关键词搜索（用户名/邮箱/手机号）
- 筛选条件：角色筛选、状态筛选、注册时间范围
- 操作列：查看详情、封禁/解封按钮（带确认框）、重置密码（弹窗输入新密码）、删除用户（带确认框）
- 分页组件
- 点击用户行可展开或跳转到用户详情页

#### 任务 2.3 — 前端用户盆栽查看页面

**涉及文件**：
- `frontend/src/views/admin/UserPlants.vue`（重写，替换占位符）

**功能要求**：
- 显示指定用户的所有盆栽列表（卡片或表格形式）
- 卡片展示：植物名、昵称、照片、种植日期、状态、最近浇水时间
- 只读模式（不可编辑），但可查看详情

#### 任务 2.4 — 前端用户记录查看页面

**涉及文件**：
- `frontend/src/views/admin/UserRecords.vue`（重写，替换占位符）

**功能要求**：
- Tab 切换：识别记录 / 诊断记录 / 浇水记录 / 养护记录
- 每个 Tab 下展示对应记录列表（表格或卡片）
- 支持按日期范围筛选
- 只读模式

---

### 🟡 阶段三：操作日志审计（P0）

#### 任务 3.1 — 后端操作日志 API

**涉及文件**：
- `backend/app/api/v1/endpoints/admin_logs.py`（新建）
- `backend/app/api/v1/__init__.py`（修改，注册新路由）

**端点**：
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/admin/logs/operations` | 操作日志列表（分页、按操作类型筛选、按时间范围筛选、按管理员筛选） |
| GET | `/admin/logs/operations/export` | 导出操作日志（CSV） |
| GET | `/admin/logs/login` | 登录日志列表（分页、按时间筛选、按成功/失败筛选） |
| GET | `/admin/logs/login/export` | 导出登录日志（CSV） |

#### 任务 3.2 — 前端操作日志审计页面

**涉及文件**：
- `frontend/src/views/admin/OperationLog.vue`（新建）
- `frontend/src/router/routes.ts`（修改，添加路由）

**功能要求**：
- Tab 切换：操作日志 / 登录日志
- **操作日志**：表格展示时间、管理员、操作类型(中文标签)、操作对象、IP 地址
  - 筛选：操作类型下拉、时间范围选择器、管理员搜索
  - 详情可展开查看完整 JSON 详情
  - 导出按钮
- **登录日志**：表格展示时间、用户名、IP 地址、登录结果(成功/失败标签)
  - 筛选：时间范围、成功/失败

---

### 🔵 阶段四：系统状态监控（P1）

#### 任务 4.1 — 后端系统监控 API

**涉及文件**：
- `backend/app/api/v1/endpoints/admin_system.py`（新建）
- `backend/app/api/v1/__init__.py`（修改，注册新路由）
- `backend/requirements.txt`（修改，新增 `psutil`）

**端点**：
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/admin/system/status` | 系统各组件健康状态（API服务、MySQL、Neo4j、Redis、AI模型、磁盘空间） |
| GET | `/admin/system/metrics` | 系统资源指标（CPU使用率、内存使用率、磁盘使用率、Python进程内存） |
| GET | `/admin/system/db-stats` | 数据库统计（各表记录数、数据库大小） |

#### 任务 4.2 — 前端系统监控页面

**涉及文件**：
- `frontend/src/views/admin/SystemMonitor.vue`（新建）
- `frontend/src/router/routes.ts`（修改，添加路由）

**功能要求**：
- 顶部状态卡片：各组件健康状态灯（绿色=正常/红色=异常/灰色=未配置）
  - API 服务、MySQL、Neo4j、Redis（如有）、AI 模型
- 系统资源仪表盘：
  - CPU 使用率（环形进度条）
  - 内存使用率（环形进度条）
  - 磁盘使用率（环形进度条）
  - Python 进程内存占用
- 数据库统计信息：各主要表的数据量
- 定时刷新（可配置刷新间隔，默认 30 秒）
- 手动刷新按钮

---

### 🟢 阶段五：权限与角色管理（P1）

#### 任务 5.1 — 后端角色管理 API

**涉及文件**：
- `backend/app/api/models/role.py`（新建，角色模型）
- `backend/app/api/models/__init__.py`（修改）
- `backend/app/api/v1/endpoints/admin_roles.py`（新建）
- `backend/app/api/v1/__init__.py`（修改，注册新路由）

**数据库模型**：
1. `Role` 表：`id`, `name`(角色名), `code`(角色编码如 `admin/editor/viewer`), `description`, `permissions`(JSON 权限列表), `is_system`(系统内置不可删除), `created_at`, `updated_at`
2. `UserRole` 表（或在 User 模型扩展多角色）：`id`, `user_id`(FK), `role_id`(FK)

**端点**：
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/admin/roles` | 角色列表 |
| POST | `/admin/roles` | 创建角色 |
| PUT | `/admin/roles/{id}` | 更新角色 |
| DELETE | `/admin/roles/{id}` | 删除角色（非系统角色） |
| GET | `/admin/roles/permissions` | 获取所有可用权限列表 |
| PUT | `/admin/users/{id}/role` | 修改用户角色 |

**权限粒度**：
```
user:view, user:ban, user:delete, user:reset_password
plant:view, plant:delete
log:view, log:export
system:view, system:manage
role:view, role:create, role:edit, role:delete
knowledge:view, knowledge:edit
model:retrain
```

#### 任务 5.2 — 前端角色管理页面

**涉及文件**：
- `frontend/src/views/admin/RoleManage.vue`（新建）
- `frontend/src/router/routes.ts`（修改，添加路由）

**功能要求**：
- 角色列表：角色名、编码、描述、用户数、是否系统角色、操作
- 新建/编辑角色对话框：
  - 角色名、编码、描述输入
  - 权限树选择器（使用 el-tree，按模块分组勾选）
- 删除角色确认（系统角色禁用删除）
- 用户角色分配：在用户管理页面增加角色下拉选择

---

### 🟣 阶段六：导航与布局整合（P0-P1 贯穿）

#### 任务 6.1 — 前端侧边栏/底部导航扩展

**涉及文件**：
- `frontend/src/views/Layout.vue`（修改）

**说明**：
- 管理员菜单扩展为：
  - 📊 数据看板 `/admin/dashboard`
  - 👥 用户管理 `/admin/users`
  - 📋 操作日志 `/admin/logs`
  - ⚙️ 系统监控 `/admin/system`
  - 🔐 角色管理 `/admin/roles`
- 使用 `el-sub-menu` 分组（可选）
- 移动端底部导航栏同步扩展

#### 任务 6.2 — 前端路由表完善

**涉及文件**：
- `frontend/src/router/routes.ts`（修改）

**新增路由**：
```
/admin/dashboard       → Dashboard.vue      (requiresAdmin)
/admin/users           → UserManage.vue      (requiresAdmin) [已有]
/admin/users/:id/plants → UserPlants.vue    (requiresAdmin) [已有]
/admin/users/:id/records → UserRecords.vue  (requiresAdmin) [已有]
/admin/logs            → OperationLog.vue    (requiresAdmin)
/admin/system          → SystemMonitor.vue   (requiresAdmin)
/admin/roles           → RoleManage.vue      (requiresAdmin)
```

#### 任务 6.3 — 前端类型定义完善

**涉及文件**：
- `frontend/src/types/api.d.ts`（修改）
- `frontend/src/types/models.d.ts`（修改）

**新增类型**：
- `UserDetail`（含统计信息）
- `OperationLog`, `LoginLog`
- `SystemStatus`, `SystemMetrics`
- `Role`, `Permission`
- `DashboardOverview`, `TodayStats`, `ChartData`
- `AdminActivity`

---

### ⚪ 阶段七：知识库管理增强（P2，可选）

#### 任务 7.1 — 后端知识库管理 API 完善

**涉及文件**：
- `backend/app/api/v1/endpoints/admin.py`（修改 `update_knowledge` 端点）

**说明**：
- 将现有的框架性知识库端点具体化
- 对接 Neo4j 实现植物/病害/虫害的 CRUD
- 支持知识库数据的批量导入/导出

#### 任务 7.2 — 前端知识库管理页面（可选）

**涉及文件**：
- `frontend/src/views/admin/KnowledgeBase.vue`（新建）

---

## 三、依赖变更汇总

### 后端新增依赖
| 包名 | 用途 |
|------|------|
| `psutil` | 系统资源监控（CPU/内存/磁盘） |

### 前端新增依赖
| 包名 | 用途 |
|------|------|
| `echarts` ^5.5.0 | 图表库 |
| `vue-echarts` ^7.0.0 | Vue 3 ECharts 封装 |

---

## 四、文件变更清单汇总

### 后端新增文件（8个）
```
backend/app/api/models/operation_log.py
backend/app/api/models/login_log.py
backend/app/api/models/role.py
backend/app/api/services/admin_log_service.py
backend/app/api/v1/endpoints/admin_dashboard.py
backend/app/api/v1/endpoints/admin_logs.py
backend/app/api/v1/endpoints/admin_system.py
backend/app/api/v1/endpoints/admin_roles.py
```

### 后端修改文件（4个）
```
backend/app/api/models/__init__.py        # 注册新模型
backend/app/api/v1/__init__.py            # 注册新路由
backend/app/api/v1/endpoints/admin.py     # 扩展用户管理端点
backend/requirements.txt                  # 添加 psutil
```

### 前端新增文件（6个）
```
frontend/src/views/admin/Dashboard.vue
frontend/src/views/admin/OperationLog.vue
frontend/src/views/admin/SystemMonitor.vue
frontend/src/views/admin/RoleManage.vue
frontend/src/stores/modules/admin.ts
frontend/src/api/modules/admin.ts         # 重写扩展
```

### 前端修改文件（6个）
```
frontend/src/router/routes.ts             # 添加新路由
frontend/src/views/Layout.vue             # 扩展管理员菜单
frontend/src/views/admin/UserManage.vue   # 重写实现
frontend/src/views/admin/UserPlants.vue   # 重写实现
frontend/src/views/admin/UserRecords.vue  # 重写实现
frontend/src/types/models.d.ts            # 新增类型定义
frontend/src/types/api.d.ts               # 新增 API 响应类型
frontend/package.json                     # 添加 echarts 依赖
```

---

## 五、执行顺序建议

```
阶段一（基础建设+数据看板） ← 优先完成，奠定基础
    ↓
阶段二（用户账户管理） ← 核心功能，紧接实现
    ↓
阶段三（操作日志审计） ← 依赖阶段一二的日志记录
    ↓
阶段四（系统状态监控） ← 独立可并行
    ↓
阶段五（权限与角色管理）← 依赖阶段二的用户管理
    ↓
阶段六（导航与布局整合）← 贯穿各阶段，可在阶段一二后开始
    ↓
阶段七（知识库管理增强）← 可选，最后进行
```

> **建议**：阶段一至三为核心功能（P0），建议优先完成后再进入阶段四至五（P1）。阶段六可随着前三个阶段逐步推进而非一次性完成。

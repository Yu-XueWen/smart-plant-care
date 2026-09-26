<template>
  <div class="role-manage">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>角色权限管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建角色
          </el-button>
        </div>
      </template>

      <!-- 角色列表 -->
      <el-table :data="roles" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="permissions" label="权限" min-width="300">
          <template #default="{ row }">
            <el-tag
              v-for="perm in row.permissions.slice(0, 5)"
              :key="perm"
              size="small"
              class="permission-tag"
            >
              {{ perm }}
            </el-tag>
            <el-tag v-if="row.permissions.length > 5" size="small" type="info">
              +{{ row.permissions.length - 5 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="用户数" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @change="fetchRoles"
        class="pagination"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入角色描述" />
        </el-form-item>
        <el-form-item label="权限配置" prop="permissions">
          <el-tree
            ref="treeRef"
            :data="permissionTree"
            :props="{ label: 'label', children: 'children' }"
            node-key="value"
            show-checkbox
            default-expand-all
            :default-checked-keys="form.permissions"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { adminApi } from '@/api/modules/admin'
import type { Role } from '@/types/models'

const loading = ref(false)
const roles = ref<Role[]>([])
const dialogVisible = ref(false)
const dialogTitle = computed(() => form.value.id ? '编辑角色' : '新建角色')
const formRef = ref()
const treeRef = ref()
const submitting = ref(false)

const form = ref<Partial<Role>>({
  name: '',
  description: '',
  permissions: []
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 权限树配置
const permissionTree = [
  {
    label: '用户管理',
    value: 'user',
    children: [
      { label: '查看用户', value: 'user:view' },
      { label: '禁用/启用用户', value: 'user:ban' },
      { label: '删除用户', value: 'user:delete' },
      { label: '重置密码', value: 'user:reset_password' },
    ]
  },
  {
    label: '植物管理',
    value: 'plant',
    children: [
      { label: '查看植物', value: 'plant:view' },
      { label: '删除植物', value: 'plant:delete' },
    ]
  },
  {
    label: '日志管理',
    value: 'log',
    children: [
      { label: '查看日志', value: 'log:view' },
      { label: '导出日志', value: 'log:export' },
    ]
  },
  {
    label: '系统管理',
    value: 'system',
    children: [
      { label: '查看系统状态', value: 'system:view' },
      { label: '管理系统配置', value: 'system:manage' },
    ]
  },
  {
    label: '角色管理',
    value: 'role',
    children: [
      { label: '查看角色', value: 'role:view' },
      { label: '创建角色', value: 'role:create' },
      { label: '编辑角色', value: 'role:edit' },
      { label: '删除角色', value: 'role:delete' },
    ]
  },
  {
    label: '知识库管理',
    value: 'knowledge',
    children: [
      { label: '查看知识库', value: 'knowledge:view' },
      { label: '编辑知识库', value: 'knowledge:edit' },
    ]
  },
  {
    label: '模型管理',
    value: 'model',
    children: [
      { label: '重新训练模型', value: 'model:retrain' },
    ]
  }
]

const fetchRoles = async () => {
  loading.value = true
  try {
    const res = await adminApi.getRoles({
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    })
    roles.value = res.items
    pagination.value.total = res.total
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  form.value = { name: '', description: '', permissions: [] }
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除角色"${row.name}"吗？`, '提示', {
      type: 'warning'
    })
    await adminApi.deleteRole(row.id)
    ElMessage.success('删除成功')
    fetchRoles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 获取选中的权限
    const checkedKeys = treeRef.value.getCheckedKeys()
    const halfCheckedKeys = treeRef.value.getHalfCheckedKeys()
    form.value.permissions = [...checkedKeys, ...halfCheckedKeys] as string[]
    
    if (form.value.id) {
      await adminApi.updateRole(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await adminApi.createRole(form.value)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchRoles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchRoles()
})
</script>

<style scoped lang="scss">
.role-manage {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .permission-tag {
    margin-right: 4px;
    margin-bottom: 4px;
  }

  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
}
</style>

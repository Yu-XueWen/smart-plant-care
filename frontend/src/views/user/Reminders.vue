<template>
  <div class="reminders-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>🔔 提醒管理</h2>
      <p class="subtitle">自定义养护提醒，智能同步记录</p>
    </div>

    <!-- 操作栏 -->
    <el-card class="action-card">
      <div class="action-bar">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建提醒
        </el-button>
        
        <el-button 
          :type="notificationPermission === 'granted' ? 'success' : 'warning'"
          @click="handleNotificationPermission"
        >
          <el-icon><Bell /></el-icon>
          {{ notificationPermission === 'granted' ? '通知已启用' : '启用通知' }}
        </el-button>
        
        <el-button 
          type="info"
          @click="handleCheckMissingReminders"
          :loading="checkingMissing"
        >
          <el-icon><MagicStick /></el-icon>
          检查缺失提醒
        </el-button>
        
        <el-select 
          v-model="filterType" 
          placeholder="类型筛选" 
          clearable
          style="width: 150px"
          @change="handleFilterChange"
        >
          <el-option label="全部" value="" />
          <el-option label="浇水" value="water" />
          <el-option label="施肥" value="fertilize" />
          <el-option label="施药" value="pesticide" />
          <el-option label="修剪" value="prune" />
          <el-option label="其他" value="other" />
        </el-select>
        
        <el-select 
          v-model="filterStatus" 
          placeholder="状态筛选" 
          clearable
          style="width: 150px"
          @change="handleFilterChange"
        >
          <el-option label="全部" value="" />
          <el-option label="待执行" value="pending" />
          <el-option label="已完成" value="completed" />
        </el-select>
      </div>
    </el-card>

    <!-- 提醒列表 -->
    <el-card class="reminders-card">
      <!-- 统计卡片 -->
      <div class="stats-section">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="6" v-for="stat in reminderStats" :key="stat.type">
            <div class="stat-card" :class="stat.class">
              <div class="stat-icon">
                <el-icon :size="24">
                  <component :is="stat.icon" />
                </el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">{{ stat.label }}</div>
                <div class="stat-value">
                  <span class="stat-number">{{ stat.count }}</span>
                  <span class="stat-unit">个提醒</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 浇水提醒特殊显示：卡片式 -->
      <div v-if="showWateringCards && wateringReminders.length > 0" class="watering-cards-section">
        <h3 class="section-title">💧 今日待浇水</h3>
        <div class="watering-cards-list">
          <el-card 
            v-for="reminder in wateringReminders" 
            :key="reminder.id"
            class="watering-reminder-card"
          >
            <div class="card-header-custom">
              <div class="plant-info">
                <h3 class="plant-name">{{ reminder.plant_name }}</h3>
                <span class="nickname" v-if="reminder.nickname">({{ reminder.nickname }})</span>
              </div>
            </div>

            <!-- 时间段显示 -->
            <div class="time-slots">
              <div class="slot-label">提醒时间：</div>
              <div class="slots">
                <div class="time-slot active">
                  <span class="slot-time">07:50</span>
                  <span class="slot-label-text">早上</span>
                </div>
                <div class="time-slot">
                  <span class="slot-time">12:00</span>
                  <span class="slot-label-text">中午</span>
                </div>
                <div class="time-slot">
                  <span class="slot-time">18:00</span>
                  <span class="slot-label-text">晚上</span>
                </div>
              </div>
            </div>

            <!-- 剩余时间显示 -->
            <div class="countdown-info">
              <el-icon class="countdown-icon"><Clock /></el-icon>
              <span class="countdown-text" :class="getCountdownClass(reminder.scheduled_date)">
                {{ getCountdownText(reminder.scheduled_date) }}
              </span>
            </div>

            <!-- 操作按钮 -->
            <div class="reminder-actions">
              <el-button 
                type="success" 
                size="large"
                @click="handleComplete(reminder)"
              >
                <el-icon><Select /></el-icon>
                已经浇过水啦
              </el-button>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 其他类型提醒：表格显示 -->
      <div v-if="otherReminders.length > 0 || !showWateringCards" class="table-section">
        <el-table 
          :data="displayReminders" 
          v-loading="loading"
          style="width: 100%"
        >
        <el-table-column prop="plant_name" label="植物" width="150">
          <template #default="{ row }">
            <div class="plant-cell">
              <strong>{{ row.plant_name || '未关联' }}</strong>
              <span v-if="row.nickname" class="nickname">({{ row.nickname }})</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.remind_type)" size="small">
              {{ getTypeLabel(row.remind_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="频率" width="120" align="center">
          <template #default="{ row }">
            <span class="frequency-text">
              {{ getFrequencyText(row as CareReminder) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="scheduled_date" label="计划日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.scheduled_date) }}
          </template>
        </el-table-column>
        
        <el-table-column label="剩余时间" width="130" align="center">
          <template #default="{ row }">
            <div class="countdown-cell">
              <el-icon class="countdown-cell-icon"><Clock /></el-icon>
              <span class="countdown-cell-text" :class="getCountdownClass(row.scheduled_date)">
                {{ getCountdownText(row.scheduled_date) }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="产品/水量" min-width="120">
          <template #default="{ row }">
            {{ row.product_name || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="用量" width="100">
          <template #default="{ row }">
            {{ row.dosage || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType((row as CareReminder).status || 'unknown')" size="small">
              {{ getStatusLabel((row as CareReminder).status || 'unknown') }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'pending' || row.status === 'today'"
              type="success" 
              size="small"
              @click="handleComplete(row as CareReminder)"
            >
              确认完成
            </el-button>
            <el-button 
              type="primary" 
              size="small" 
              link
              @click="handleEdit(row as CareReminder)"
            >
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              link
              @click="handleDelete(row as CareReminder)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchReminders"
          @current-change="fetchReminders"
        />
      </div>

      <el-empty v-if="!loading && displayReminders.length === 0 && !showWateringCards" description="暂无提醒" />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑提醒' : '新建提醒'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="关联植物" prop="plant_id">
          <el-select 
            v-model="formData.plant_id" 
            placeholder="选择植物（可选）"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="plant in plants"
              :key="plant.id"
              :label="`${plant.plant_name}${plant.nickname ? '(' + plant.nickname + ')' : ''}`"
              :value="plant.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="提醒类型" prop="remind_type">
          <el-radio-group v-model="formData.remind_type">
            <el-radio value="water">浇水</el-radio>
            <el-radio value="fertilize">施肥</el-radio>
            <el-radio value="pesticide">施药</el-radio>
            <el-radio value="prune">修剪</el-radio>
            <el-radio value="other">其他</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="计划日期" prop="scheduled_date">
          <el-date-picker
            v-model="formData.scheduled_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item :label="formData.remind_type === 'water' ? '水量' : '产品/药品'" prop="product_name">
          <el-input 
            v-model="formData.product_name" 
            :placeholder="formData.remind_type === 'water' ? '例如：200ml' : '例如：复合肥、多菌灵'"
          />
        </el-form-item>

        <el-form-item label="用量" prop="dosage">
          <el-input 
            v-model="formData.dosage" 
            placeholder="例如：10g、500ml"
          />
        </el-form-item>

        <el-form-item label="备注" prop="notes">
          <el-input 
            v-model="formData.notes" 
            type="textarea"
            :rows="3"
            placeholder="输入备注信息"
          />
        </el-form-item>

        <el-form-item label="频率类型">
          <el-select v-model="formData.frequency_type" style="width: 100%" @change="handleFrequencyChange">
            <el-option label="仅一次" value="one_time" />
            <el-option label="自定义间隔" value="interval" />
            <el-option label="每天" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
          </el-select>
        </el-form-item>

        <el-form-item 
          v-if="formData.frequency_type === 'interval'" 
          label="间隔天数" 
          prop="interval_days"
        >
          <el-input-number 
            v-model="formData.interval_days" 
            :min="1" 
            :max="365"
            placeholder="输入间隔天数"
            style="width: 100%"
          />
          <div class="form-tip">每隔 {{ formData.interval_days || 7 }} 天提醒一次</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 确认完成对话框 -->
    <el-dialog
      v-model="completeDialogVisible"
      title="确认完成提醒"
      width="500px"
    >
      <el-alert
        title="确认后，该提醒将同步到养护记录表中"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-form
        ref="completeFormRef"
        :model="completeFormData"
        label-width="100px"
      >
        <el-form-item label="实际日期">
          <el-date-picker
            v-model="completeFormData.actual_date"
            type="date"
            placeholder="选择实际执行日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item :label="currentReminder?.remind_type === 'water' ? '实际水量' : '实际产品'">
          <el-input 
            v-model="completeFormData.actual_product" 
            :placeholder="currentReminder?.remind_type === 'water' ? '默认为提醒中的水量' : '默认为提醒中的产品'"
          />
        </el-form-item>

        <el-form-item label="实际用量">
          <el-input 
            v-model="completeFormData.actual_dosage" 
            placeholder="默认为提醒中的用量"
          />
        </el-form-item>

        <el-form-item label="补充备注">
          <el-input 
            v-model="completeFormData.actual_notes" 
            type="textarea"
            :rows="2"
            placeholder="可选，将与原备注合并"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="completeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmComplete" :loading="completing">
          确认完成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Select, Clock, Watermelon, MagicStick, Crop, Bell } from '@element-plus/icons-vue'
import { careReminderApi, type CareReminder, type CreateCareReminderRequest } from '@/api/modules/careReminder'
import { plantApi } from '@/api/modules/plant'
import { getNotificationPermission, showPermissionGuide } from '@/utils/notification'

const loading = ref(false)
const submitting = ref(false)
const completing = ref(false)
const checkingMissing = ref(false) // 检查缺失提醒的加载状态
const dialogVisible = ref(false)
const completeDialogVisible = ref(false)
const isEdit = ref(false)
const currentReminderId = ref<number | null>(null)
const currentReminder = ref<CareReminder | null>(null)

// 通知权限状态
const notificationPermission = ref<NotificationPermission>('default')

// 列表数据
const reminders = ref<CareReminder[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const filterType = ref('')
const filterStatus = ref('')

// 植物列表
const plants = ref<any[]>([])

// 计算属性 - 分离浇水提醒和其他提醒
const wateringReminders = computed(() => {
  return reminders.value.filter(r => r.remind_type === 'water')
})

const otherReminders = computed(() => {
  return reminders.value.filter(r => r.remind_type !== 'water')
})

// 是否显示浇水卡片（当筛选为浇水或没有筛选时）
const showWateringCards = computed(() => {
  return !filterType.value || filterType.value === 'water'
})

// 显示的提醒列表（表格中只显示非浇水类型）
const displayReminders = computed(() => {
  if (filterType.value === 'water') {
    return [] // 如果筛选浇水，表格不显示
  }
  return otherReminders.value
})

// 统计卡片数据
const reminderStats = computed(() => {
  return [
    {
      type: 'water',
      label: '浇水提醒',
      count: wateringReminders.value.length,
      icon: Watermelon,
      class: 'stat-water'
    },
    {
      type: 'fertilize',
      label: '施肥提醒',
      count: reminders.value.filter(r => r.remind_type === 'fertilize').length,
      icon: MagicStick,
      class: 'stat-fertilize'
    },
    {
      type: 'prune',
      label: '修剪提醒',
      count: reminders.value.filter(r => r.remind_type === 'prune').length,
      icon: Crop,
      class: 'stat-prune'
    },
    {
      type: 'other',
      label: '其他提醒',
      count: reminders.value.filter(r => !['water', 'fertilize', 'prune'].includes(r.remind_type)).length,
      icon: Clock,
      class: 'stat-other'
    }
  ]
})

// 表单数据
const formRef = ref<FormInstance>()
const formData = reactive<CreateCareReminderRequest>({
  remind_type: 'fertilize',
  scheduled_date: new Date().toISOString().split('T')[0],
  product_name: '',
  dosage: '',
  notes: '',
  frequency_type: 'one_time',
  interval_days: 7,
  repeat_interval: 0,
  is_enabled: true
})

// 完成提醒表单
const completeFormRef = ref<FormInstance>()
const completeFormData = reactive({
  actual_date: '',
  actual_product: '',
  actual_dosage: '',
  actual_notes: ''
})

// 表单验证规则
const formRules: FormRules = {
  remind_type: [
    { required: true, message: '请选择提醒类型', trigger: 'change' }
  ],
  scheduled_date: [
    { required: true, message: '请选择计划日期', trigger: 'change' }
  ],
  interval_days: [
    { 
      validator: (_rule, value, callback) => {
        if (formData.frequency_type === 'interval' && (!value || value < 1)) {
          callback(new Error('请输入有效的间隔天数'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 获取提醒列表
async function fetchReminders() {
  loading.value = true
  try {
    const response = await careReminderApi.getReminders({
      page: currentPage.value,
      page_size: pageSize.value,
      remind_type: filterType.value || undefined,
      status_filter: (filterStatus.value || undefined) as 'pending' | 'completed' | undefined
    })
    
    reminders.value = response.items
    total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取提醒列表失败')
  } finally {
    loading.value = false
  }
}

// 获取植物列表
async function fetchPlants() {
  try {
    const response = await plantApi.getMyPlants({ page: 1, page_size: 100 })
    plants.value = response.items || []
  } catch (error) {
    console.error('获取植物列表失败:', error)
  }
}

// 显示创建对话框
function showCreateDialog() {
  isEdit.value = false
  currentReminderId.value = null
  resetForm()
  dialogVisible.value = true
}

// 编辑提醒
function handleEdit(reminder: CareReminder) {
  isEdit.value = true
  currentReminderId.value = reminder.id
  
  formData.remind_type = reminder.remind_type
  formData.scheduled_date = reminder.scheduled_date
  formData.plant_id = reminder.plant_id
  formData.product_name = reminder.product_name || ''
  formData.dosage = reminder.dosage || ''
  formData.notes = reminder.notes || ''
  formData.frequency_type = reminder.frequency_type
  formData.interval_days = reminder.interval_days || 7
  formData.repeat_interval = reminder.repeat_interval || 0
  formData.is_enabled = reminder.is_enabled
  
  dialogVisible.value = true
}

// 频率类型变化处理
function handleFrequencyChange(value: string) {
  // 如果切换到自定义间隔，设置默认值
  if (value === 'interval' && !formData.interval_days) {
    formData.interval_days = 7
  }
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value && currentReminderId.value) {
        await careReminderApi.updateReminder(currentReminderId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await careReminderApi.createReminder(formData)
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      fetchReminders()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 删除提醒
async function handleDelete(reminder: CareReminder) {
  try {
    await ElMessageBox.confirm('确定要删除这个提醒吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await careReminderApi.deleteReminder(reminder.id)
    ElMessage.success('删除成功')
    fetchReminders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 显示完成对话框
function handleComplete(reminder: CareReminder) {
  currentReminderId.value = reminder.id
  currentReminder.value = reminder
  completeFormData.actual_date = reminder.scheduled_date
  completeFormData.actual_product = reminder.product_name || ''
  completeFormData.actual_dosage = reminder.dosage || ''
  completeFormData.actual_notes = ''
  completeDialogVisible.value = true
}

// 确认完成并同步
async function handleConfirmComplete() {
  if (!currentReminderId.value) return
  
  completing.value = true
  try {
    const response = await careReminderApi.completeAndSync(
      currentReminderId.value,
      {
        actual_date: completeFormData.actual_date || undefined,
        actual_product: completeFormData.actual_product || undefined,
        actual_dosage: completeFormData.actual_dosage || undefined,
        actual_notes: completeFormData.actual_notes || undefined
      }
    )
    
    ElMessage.success(response.message)
    completeDialogVisible.value = false
    fetchReminders()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    completing.value = false
  }
}

// 重置表单
function resetForm() {
  formData.remind_type = 'fertilize'
  formData.scheduled_date = new Date().toISOString().split('T')[0]
  formData.plant_id = undefined
  formData.product_name = ''
  formData.dosage = ''
  formData.notes = ''
  formData.frequency_type = 'one_time'
  formData.interval_days = 7
  formData.repeat_interval = 0
  formData.is_enabled = true
  
  formRef.value?.clearValidate()
}

// 筛选变化
function handleFilterChange() {
  currentPage.value = 1
  fetchReminders()
}

// 处理通知权限
function handleNotificationPermission() {
  showPermissionGuide()
}

// 检查缺失提醒并自动创建
async function handleCheckMissingReminders() {
  try {
    await ElMessageBox.confirm(
      '系统将检查所有活跃植物是否有浇水提醒，并为没有提醒的植物自动创建。是否继续？',
      '检查缺失提醒',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    checkingMissing.value = true
    const response = await careReminderApi.checkMissingWateringReminders()
    
    const { created_count, skipped_count, total_plants } = response
    
    // 显示详细结果
    let message = `检查完成！\n`
    message += `总计：${total_plants} 个活跃植物\n`
    message += `✅ 创建了 ${created_count} 个新提醒\n`
    message += `⏭️ 跳过了 ${skipped_count} 个已有提醒的植物`
    
    ElMessage.success({
      message,
      duration: 5000,
      showClose: true
    })
    
    // 刷新提醒列表
    fetchReminders()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '检查失败')
    }
  } finally {
    checkingMissing.value = false
  }
}

// 更新通知权限状态
function updateNotificationPermission() {
  notificationPermission.value = getNotificationPermission()
}

// 格式化日期
function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

// 获取类型标签
function getTypeLabel(type: string): string {
  const map: Record<string, string> = {
    water: '浇水',
    fertilize: '施肥',
    pesticide: '施药',
    prune: '修剪',
    other: '其他'
  }
  return map[type] || type
}

// 获取类型标签样式
function getTypeTagType(type: string): 'success' | 'warning' | 'danger' | 'info' | 'primary' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'primary'> = {
    water: 'primary',
    fertilize: 'success',
    pesticide: 'danger',
    prune: 'warning',
    other: 'info'
  }
  return map[type] || 'info'
}

// 获取状态标签
function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: '待执行',
    today: '今天',
    completed: '已完成',
    overdue: '已逾期',
    unknown: '未知'
  }
  return map[status] || status
}

// 获取状态标签样式
function getStatusTagType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    pending: 'warning',
    today: 'danger',
    completed: 'success',
    overdue: 'danger',
    unknown: 'info'
  }
  return map[status] || 'info'
}

// 获取频率文本
function getFrequencyText(reminder: CareReminder): string {
  const { frequency_type, interval_days } = reminder
  
  switch (frequency_type) {
    case 'one_time':
      return '仅一次'
    case 'daily':
      return '每天'
    case 'weekly':
      return '每周'
    case 'monthly':
      return '每月'
    case 'interval':
      return `每${interval_days || 7}天`
    default:
      return '-'
  }
}

// 计算剩余天数
function getDaysRemaining(dateStr: string): number {
  if (!dateStr) return 0
  const targetDate = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  targetDate.setHours(0, 0, 0, 0)
  
  const diffTime = targetDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

// 获取剩余时间文本
function getCountdownText(dateStr: string): string {
  const days = getDaysRemaining(dateStr)
  
  if (days < 0) {
    return `已逾期 ${Math.abs(days)} 天`
  } else if (days === 0) {
    return '今天需要养护'
  } else if (days === 1) {
    return '明天需要养护'
  } else {
    return `还有 ${days} 天`
  }
}

// 获取剩余时间样式类
function getCountdownClass(dateStr: string): string {
  const days = getDaysRemaining(dateStr)
  
  if (days < 0) {
    return 'countdown-overdue'
  } else if (days === 0) {
    return 'countdown-today'
  } else if (days <= 3) {
    return 'countdown-warning'
  } else {
    return 'countdown-normal'
  }
}

// 初始化
onMounted(() => {
  fetchReminders()
  fetchPlants()
  updateNotificationPermission() // 初始化通知权限状态
})
</script>

<style scoped lang="scss">
.reminders-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 24px;

    h2 {
      font-size: 28px;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .action-card {
    margin-bottom: 20px;

    .action-bar {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .reminders-card {
    // 浇水卡片区域
    .watering-cards-section {
      margin-bottom: 24px;

      .section-title {
        font-size: 20px;
        color: #303133;
        margin: 0 0 16px 0;
        padding-left: 8px;
      }

      .watering-cards-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 16px;

        .watering-reminder-card {
          border: 2px solid #e6f7ff;
          transition: all 0.3s;

          &:hover {
            border-color: #409eff;
            box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
          }

          .card-header-custom {
            margin-bottom: 16px;

            .plant-info {
              display: flex;
              align-items: baseline;
              gap: 8px;

              .plant-name {
                font-size: 18px;
                color: #303133;
                margin: 0;
                font-weight: 600;
              }

              .nickname {
                font-size: 14px;
                color: #909399;
              }
            }
          }

          // 时间段显示
          .time-slots {
            margin-bottom: 16px;
            padding: 12px;
            background: #f5f7fa;
            border-radius: 8px;

            .slot-label {
              font-size: 13px;
              color: #606266;
              margin-bottom: 8px;
            }

            .slots {
              display: flex;
              gap: 12px;

              .time-slot {
                flex: 1;
                padding: 8px 12px;
                background: white;
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                text-align: center;
                transition: all 0.3s;

                &.active {
                  background: #e6f7ff;
                  border-color: #409eff;
                  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
                }

                .slot-time {
                  display: block;
                  font-size: 16px;
                  font-weight: 600;
                  color: #303133;
                  margin-bottom: 4px;
                }

                .slot-label-text {
                  display: block;
                  font-size: 12px;
                  color: #909399;
                }
              }
            }
          }

          // 操作按钮
          .reminder-actions {
            display: flex;
            justify-content: center;
            margin-top: 12px;

            .el-button {
              min-width: 160px;
            }
          }

          // 倒计时显示
          .countdown-info {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px;
            background: #f9fafb;
            border-radius: 6px;
            margin-top: 12px;

            .countdown-icon {
              font-size: 18px;
              color: #606266;
            }

            .countdown-text {
              font-size: 15px;
              font-weight: 600;

              &.countdown-overdue {
                color: #f56c6c;
              }

              &.countdown-today {
                color: #e6a23c;
              }

              &.countdown-warning {
                color: #f59e42;
              }

              &.countdown-normal {
                color: #67c23a;
              }
            }
          }
        }
      }
    }

    // 表格区域
    .table-section {
      .plant-cell {
        display: flex;
        flex-direction: column;
        gap: 2px;

        strong {
          font-size: 14px;
          color: #303133;
        }

        .nickname {
          font-size: 12px;
          color: #909399;
        }
      }

      // 倒计时单元格
      .countdown-cell {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;

        .countdown-cell-icon {
          font-size: 14px;
          color: #909399;
        }

        .countdown-cell-text {
          font-size: 13px;
          font-weight: 600;

          &.countdown-overdue {
            color: #f56c6c;
          }

          &.countdown-today {
            color: #e6a23c;
          }

          &.countdown-warning {
            color: #f59e42;
          }

          &.countdown-normal {
            color: #67c23a;
          }
        }
      }

      // 频率文本
      .frequency-text {
        font-size: 13px;
        color: #606266;
        font-weight: 500;
      }

      .pagination-container {
        margin-top: 20px;
        display: flex;
        justify-content: flex-end;
      }
    }
  }

  // 表单提示文本
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
    line-height: 1.5;
  }
}

@media (max-width: 768px) {
  .reminders-page {
    padding: 12px;

    .action-card {
      .action-bar {
        flex-direction: column;
        
        .el-button,
        .el-select {
          width: 100%;
        }
      }
    }
  }
}
</style>

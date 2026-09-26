/**
 * 提醒逻辑组合式函数
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { reminderApi } from '@/api/modules/reminder'

export function useReminder() {
  const reminders = ref<any[]>([])
  const loading = ref(false)
  
  /**
   * 获取提醒列表
   */
  async function fetchReminders(params?: any) {
    try {
      loading.value = true
      const response = await reminderApi.getReminders(params)
      reminders.value = response.items || []
    } catch (error) {
      console.error('获取提醒列表失败:', error)
      ElMessage.error('获取提醒列表失败')
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 创建提醒
   */
  async function createReminder(data: any) {
    try {
      loading.value = true
      await reminderApi.createReminder(data)
      ElMessage.success('创建提醒成功')
      await fetchReminders()
      return true
    } catch (error) {
      console.error('创建提醒失败:', error)
      ElMessage.error('创建提醒失败')
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 更新提醒
   */
  async function updateReminder(id: number, data: any) {
    try {
      loading.value = true
      await reminderApi.updateReminder(id, data)
      ElMessage.success('更新提醒成功')
      await fetchReminders()
      return true
    } catch (error) {
      console.error('更新提醒失败:', error)
      ElMessage.error('更新提醒失败')
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 删除提醒
   */
  async function deleteReminder(id: number) {
    try {
      loading.value = true
      await reminderApi.deleteReminder(id)
      ElMessage.success('删除提醒成功')
      await fetchReminders()
      return true
    } catch (error) {
      console.error('删除提醒失败:', error)
      ElMessage.error('删除提醒失败')
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 标记提醒为已完成
   */
  async function completeReminder(id: number) {
    try {
      loading.value = true
      await reminderApi.completeReminder(id)
      ElMessage.success('标记完成成功')
      await fetchReminders()
      return true
    } catch (error) {
      console.error('标记完成失败:', error)
      ElMessage.error('标记完成失败')
      return false
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取待完成的提醒数量
   */
  const pendingCount = computed(() => {
    return reminders.value.filter(r => !r.completed).length
  })
  
  return {
    reminders,
    loading,
    pendingCount,
    fetchReminders,
    createReminder,
    updateReminder,
    deleteReminder,
    completeReminder
  }
}

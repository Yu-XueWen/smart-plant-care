/**
 * 分页逻辑组合式函数
 */
import { ref, computed, watch } from 'vue'
import { PAGINATION_DEFAULTS } from '@/utils/constants'

export interface PaginationOptions {
  page?: number
  pageSize?: number
  total?: number
}

export function usePagination(options: PaginationOptions = {}) {
  const page = ref(options.page || PAGINATION_DEFAULTS.PAGE)
  const pageSize = ref(options.pageSize || PAGINATION_DEFAULTS.PAGE_SIZE)
  const total = ref(options.total || 0)
  
  /**
   * 计算总页数
   */
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  
  /**
   * 是否有上一页
   */
  const hasPrev = computed(() => page.value > 1)
  
  /**
   * 是否有下一页
   */
  const hasNext = computed(() => page.value < totalPages.value)
  
  /**
   * 页码列表（用于显示）
   */
  const pages = computed(() => {
    const pages = []
    const start = Math.max(1, page.value - 2)
    const end = Math.min(totalPages.value, page.value + 2)
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    
    return pages
  })
  
  /**
   * 跳转到指定页
   */
  function goToPage(p: number) {
    if (p < 1 || p > totalPages.value) return
    page.value = p
  }
  
  /**
   * 上一页
   */
  function prevPage() {
    if (hasPrev.value) {
      page.value--
    }
  }
  
  /**
   * 下一页
   */
  function nextPage() {
    if (hasNext.value) {
      page.value++
    }
  }
  
  /**
   * 跳转到第一页
   */
  function firstPage() {
    page.value = 1
  }
  
  /**
   * 跳转到最后一页
   */
  function lastPage() {
    page.value = totalPages.value
  }
  
  /**
   * 重置分页
   */
  function reset() {
    page.value = 1
    pageSize.value = PAGINATION_DEFAULTS.PAGE_SIZE
    total.value = 0
  }
  
  /**
   * 设置总数
   */
  function setTotal(t: number) {
    total.value = t
    // 如果当前页超过总页数，跳转到最后一页
    if (page.value > totalPages.value && totalPages.value > 0) {
      page.value = totalPages.value
    }
  }
  
  /**
   * 获取分页参数
   */
  function getParams() {
    return {
      page: page.value,
      page_size: pageSize.value
    }
  }
  
  // 监听 pageSize 变化，重置到第一页
  watch(pageSize, () => {
    page.value = 1
  })
  
  return {
    page,
    pageSize,
    total,
    totalPages,
    hasPrev,
    hasNext,
    pages,
    pageSizes: PAGINATION_DEFAULTS.PAGE_SIZES,
    goToPage,
    prevPage,
    nextPage,
    firstPage,
    lastPage,
    reset,
    setTotal,
    getParams
  }
}

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/modules/user'

// 响应数据结构
interface ResponseData<T = any> {
  code: number
  message: string
  data: T
}

class Request {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        const userStore = useUserStore()
        if (userStore.token) {
          config.headers.Authorization = `Bearer ${userStore.token}`
          console.log('[Request] 添加 Authorization header')
        } else {
          console.warn('[Request] 没有 token')
        }
        console.log('[Request]', config.method?.toUpperCase(), config.url)
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse<ResponseData>) => {
        const { code, message, data } = response.data

        if (code === 200) {
          return data
        }

        // 401 未授权
        if (code === 401) {
          const userStore = useUserStore()
          userStore.logout()
          window.location.href = '/login'
          return Promise.reject(new Error('请重新登录'))
        }

        ElMessage.error(message || '请求失败')
        return Promise.reject(new Error(message))
      },
      (error) => {
        if (error.response) {
          const { status } = error.response
          if (status === 401) {
            const userStore = useUserStore()
            userStore.logout()
            window.location.href = '/login'
          } else if (status === 403) {
            ElMessage.error('权限不足')
          } else if (status === 404) {
            ElMessage.error('请求资源不存在')
          } else if (status === 500) {
            ElMessage.error('服务器错误')
          } else {
            ElMessage.error(error.response.data?.message || '请求失败')
          }
        } else if (error.request) {
          ElMessage.error('网络连接失败')
        } else {
          ElMessage.error(error.message || '请求失败')
        }
        return Promise.reject(error)
      }
    )
  }

  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.get(url, config)
  }

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.post(url, data, config)
  }

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.put(url, data, config)
  }

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.delete(url, config)
  }

  upload<T = any>(url: string, file: File, fieldName = 'image'): Promise<T> {
    const formData = new FormData()
    formData.append(fieldName, file)
    
    console.log('[Upload] 开始上传文件:', {
      url,
      fieldName,
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type
    })
    
    // 关键：不要设置 Content-Type，让浏览器自动添加 boundary
    // 使用 this.instance 以保留请求拦截器（添加 token）
    return this.instance.post(url, formData, {
      // 不设置 headers，让浏览器自动处理
      transformRequest: [(data) => data]  // 防止 Axios 转换 FormData
    })
  }
}

export const request = new Request()
export default request
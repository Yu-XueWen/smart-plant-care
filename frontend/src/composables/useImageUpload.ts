/**
 * 图片上传组合式函数
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UPLOAD_LIMITS } from '@/utils/constants'

export function useImageUpload() {
  const uploading = ref(false)
  const imageUrl = ref<string>('')
  
  /**
   * 验证图片文件
   */
  function validateImage(file: File): boolean {
    // 检查文件类型
    if (!UPLOAD_LIMITS.ACCEPT_TYPES.includes(file.type)) {
      ElMessage.error('只支持 JPG、PNG、GIF 格式的图片')
      return false
    }
    
    // 检查文件大小
    if (file.size > UPLOAD_LIMITS.MAX_SIZE) {
      ElMessage.error('图片大小不能超过 10MB')
      return false
    }
    
    return true
  }
  
  /**
   * 上传图片
   */
  async function uploadImage(file: File, uploadUrl: string): Promise<string> {
    if (!validateImage(file)) {
      throw new Error('图片验证失败')
    }
    
    try {
      uploading.value = true
      
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error('上传失败')
      }
      
      const data = await response.json()
      imageUrl.value = data.url
      
      ElMessage.success('上传成功')
      return data.url
    } catch (error) {
      console.error('上传失败:', error)
      ElMessage.error('上传失败，请重试')
      throw error
    } finally {
      uploading.value = false
    }
  }
  
  /**
   * 清除图片
   */
  function clearImage() {
    imageUrl.value = ''
  }
  
  /**
   * 预览图片
   */
  function previewImage(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!validateImage(file)) {
        reject(new Error('图片验证失败'))
        return
      }
      
      const reader = new FileReader()
      reader.onload = (e) => {
        resolve(e.target?.result as string)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }
  
  return {
    uploading,
    imageUrl,
    uploadImage,
    clearImage,
    previewImage,
    validateImage
  }
}

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { plantApi } from '@/api/modules/plant'
import type { Plant } from '@/types/models'
import type { PlantCreateData } from '@/api/modules/plant'

export const usePlantsStore = defineStore('plants', () => {
  const plants = ref<Plant[]>([])
  const currentPlant = ref<Plant | null>(null)
  const loading = ref(false)
  const total = ref(0)

  // 获取我的盆栽列表
  async function fetchMyPlants(page = 1, pageSize = 10) {
    loading.value = true
    try {
      const res = await plantApi.getMyPlants({ page, page_size: pageSize })
      plants.value = res.items
      total.value = res.total
      return res
    } catch (error) {
      console.error('获取盆栽列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取盆栽详情
  async function fetchPlantDetail(id: number) {
    loading.value = true
    try {
      const plant = await plantApi.getPlantDetail(id)
      currentPlant.value = plant
      return plant
    } catch (error) {
      console.error('获取盆栽详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建盆栽
  async function createPlant(data: Partial<Plant>) {
    try {
      const plantData: PlantCreateData = {
        plant_name: data.name || '',
        species_id: data.species,
        nickname: data.name,
        notes: data.notes
      }
      const plant = await plantApi.createPlant(plantData)
      plants.value.unshift(plant)
      return plant
    } catch (error) {
      console.error('创建盆栽失败:', error)
      throw error
    }
  }

  // 更新盆栽
  async function updatePlant(id: number, data: Partial<Plant>) {
    try {
      const plantData: Partial<PlantCreateData> = {
        plant_name: data.name,
        species_id: data.species,
        nickname: data.name,
        notes: data.notes
      }
      const plant = await plantApi.updatePlant(id, plantData)
      const index = plants.value.findIndex(p => p.id === id)
      if (index !== -1) {
        plants.value[index] = plant
      }
      if (currentPlant.value?.id === id) {
        currentPlant.value = plant
      }
      return plant
    } catch (error) {
      console.error('更新盆栽失败:', error)
      throw error
    }
  }

  // 删除盆栽
  async function deletePlant(id: number) {
    try {
      await plantApi.deletePlant(id)
      const index = plants.value.findIndex(p => p.id === id)
      if (index !== -1) {
        plants.value.splice(index, 1)
      }
      if (currentPlant.value?.id === id) {
        currentPlant.value = null
      }
    } catch (error) {
      console.error('删除盆栽失败:', error)
      throw error
    }
  }

  // 清除当前盆栽
  function clearCurrentPlant() {
    currentPlant.value = null
  }

  return {
    plants,
    currentPlant,
    loading,
    total,
    fetchMyPlants,
    fetchPlantDetail,
    createPlant,
    updatePlant,
    deletePlant,
    clearCurrentPlant,
  }
})

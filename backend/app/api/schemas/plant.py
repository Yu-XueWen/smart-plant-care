# backend/app/schemas/plant.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime

# ========== 植物档案 ==========

class PlantCreate(BaseModel):
    """创建植物档案请求"""
    plant_name: str = Field(..., max_length=100, description="植物名称")
    species_id: Optional[str] = Field(None, max_length=50, description="知识图谱物种ID")
    nickname: Optional[str] = Field(None, max_length=50, description="植物昵称")
    planting_date: Optional[date] = Field(None, description="栽种日期")
    source: Optional[str] = Field(None, max_length=50, description="来源")
    initial_photos: Optional[List[str]] = Field(None, description="初始照片URL数组")
    notes: Optional[str] = Field(None, description="备注")

class PlantUpdate(BaseModel):
    """更新植物档案请求"""
    plant_name: Optional[str] = Field(None, max_length=100)
    nickname: Optional[str] = Field(None, max_length=50)
    planting_date: Optional[date] = None
    source: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class PlantResponse(BaseModel):
    """植物档案响应"""
    id: int
    plant_name: str
    nickname: Optional[str] = None
    species_id: Optional[str] = None
    planting_date: Optional[date] = None
    source: Optional[str] = None
    status: int
    notes: Optional[str] = None
    initial_photos: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PlantDetailResponse(PlantResponse):
    """植物档案详情响应（含记录）"""
    watering_records: List['WateringResponse'] = []
    treatment_records: List['TreatmentResponse'] = []

# ========== 浇水记录 ==========

class WateringCreate(BaseModel):
    """创建浇水记录请求"""
    watering_date: date = Field(..., description="浇水日期")
    water_amount: Optional[str] = Field(None, max_length=20, description="浇水量")
    notes: Optional[str] = Field(None, max_length=255, description="备注")

class WateringResponse(BaseModel):
    """浇水记录响应"""
    id: int
    date: date
    amount: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# ========== 养护记录 ==========

class TreatmentCreate(BaseModel):
    """创建养护记录请求"""
    treatment_type: str = Field(..., description="类型: fertilize/pesticide/prune/other")
    product_name: Optional[str] = Field(None, max_length=100, description="肥料/药品名称")
    dosage: Optional[str] = Field(None, max_length=50, description="用量")
    application_date: date = Field(..., description="操作日期")
    notes: Optional[str] = Field(None, description="备注")

    @field_validator('treatment_type')
    @classmethod
    def validate_type(cls, v):
        allowed = ['fertilize', 'pesticide', 'prune', 'other']
        if v not in allowed:
            raise ValueError(f'类型必须是 {allowed} 之一')
        return v

class TreatmentResponse(BaseModel):
    """养护记录响应"""
    id: int
    type: str
    product_name: Optional[str] = None
    dosage: Optional[str] = None
    date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# 解决循环引用
PlantDetailResponse.model_rebuild()
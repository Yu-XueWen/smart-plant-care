# backend/app/schemas/ai.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# ========== 植物识别 ==========

class IdentifyRequest(BaseModel):
    """植物识别请求"""
    image_url: str = Field(..., description="图片URL")
    save_history: bool = Field(True, description="是否保存历史")

class CareGuide(BaseModel):
    """养护指南"""
    water_frequency: Optional[str] = None
    light_requirement: Optional[str] = None
    fertilization: Optional[str] = None
    soil_requirement: Optional[str] = None
    temperature_requirement: Optional[str] = None

class PlantResult(BaseModel):
    """单个植物识别结果"""
    plant_name: str
    scientific_name: Optional[str] = None
    family: Optional[str] = None
    confidence: float
    species_id: Optional[str] = None
    care_guide: Optional[CareGuide] = None

class IdentifyResponse(BaseModel):
    """植物识别响应"""
    top1: PlantResult
    top5: List[PlantResult]
    history_id: Optional[int] = None
    image_url: str

# ========== 病害诊断 ==========

class DiagnoseRequest(BaseModel):
    """病害诊断请求"""
    image_url: str = Field(..., description="图片URL")
    plant_id: Optional[int] = Field(None, description="关联植物ID")
    save_history: bool = Field(True, description="是否保存历史")

class TreatmentPlan(BaseModel):
    """防治方案"""
    chemical: Optional[str] = None
    organic: Optional[str] = None
    prevention: Optional[str] = None

class DiagnoseResult(BaseModel):
    """病害诊断结果"""
    primary_disease: str
    disease_id: Optional[str] = None
    confidence: float
    symptoms: str
    cause: Optional[str] = None
    treatment: TreatmentPlan

class DiagnoseResponse(BaseModel):
    """病害诊断响应"""
    primary_disease: str
    confidence: float
    symptoms: str
    treatment: TreatmentPlan
    history_id: Optional[int] = None
    image_url: str

# ========== 植物主体检测 ==========

class DetectionBox(BaseModel):
    """检测框"""
    bbox: List[int]  # [x_min, y_min, x_max, y_max]
    confidence: float
    class_name: str
    cropped_image_url: Optional[str] = None

class DetectPlantResponse(BaseModel):
    """植物主体检测响应"""
    detections: List[DetectionBox]
    processing_time_ms: float
    original_size: List[int]  # [width, height]

# ========== 保存到植物档案 ==========

class SaveToPlantRequest(BaseModel):
    """保存识别/诊断结果到植物档案请求"""
    history_type: str = Field(..., description="identify/diagnose")
    history_id: int
    plant_id: int
    action: Optional[str] = Field(None, description="create_reminder")
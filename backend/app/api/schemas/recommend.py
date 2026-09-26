from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 问卷相关 ==========

class QuestionnaireRequest(BaseModel):
    """养花推荐问卷请求"""
    experience_level: str = Field(..., description="经验水平: beginner/intermediate/advanced")
    light_condition: str = Field(..., description="光照条件: low/medium/high/full_sun")
    space_size: str = Field(..., description="空间大小: small/medium/large")
    time_availability: str = Field(..., description="可用时间: little/moderate/much")
    preferences: List[str] = Field(default=[], description="偏好标签，如：开花、观叶、多肉、空气净化等")
    climate_zone: Optional[str] = Field(None, description="气候区域")


# ========== 植物推荐结果 ==========

class PlantRecommendation(BaseModel):
    """单个植物推荐结果"""
    plant_name: str = Field(..., description="植物名称")
    scientific_name: Optional[str] = Field(None, description="学名")
    family: Optional[str] = Field(None, description="科")
    match_score: float = Field(..., description="匹配度分数(0-100)")
    reasons: List[str] = Field(default=[], description="推荐理由")
    
    # 养护信息
    care_difficulty: str = Field(..., description="养护难度: easy/medium/hard")
    light_requirement: str = Field(..., description="光照需求")
    water_frequency: str = Field(..., description="浇水频率")
    temperature_range: str = Field(..., description="温度范围")
    humidity_range: str = Field(..., description="湿度范围")
    
    # 其他信息
    tags: List[str] = Field(default=[], description="特性标签")
    benefits: List[str] = Field(default=[], description="功效")
    description: Optional[str] = Field(None, description="植物描述")
    care_tips: Optional[str] = Field(None, description="养护技巧")
    image_url: Optional[str] = Field(None, description="图片URL")
    popularity_score: float = Field(default=50.0, description="受欢迎程度")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    recommendations: List[PlantRecommendation] = Field(..., description="推荐的植物列表(TOP 10)")
    questionnaire_summary: dict = Field(default={}, description="问卷摘要")
    total_matches: int = Field(..., description="匹配的植物总数")


# ========== 植物物种管理（管理员用）==========

class PlantSpeciesCreate(BaseModel):
    """创建植物物种"""
    plant_name: str = Field(..., max_length=100)
    scientific_name: Optional[str] = Field(None, max_length=100)
    family: Optional[str] = Field(None, max_length=50)
    genus: Optional[str] = Field(None, max_length=50)
    care_difficulty: str = Field("medium", description="easy/medium/hard")
    light_requirement: Optional[str] = Field(None, max_length=50)
    water_frequency: Optional[str] = Field(None, max_length=50)
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    humidity_min: Optional[float] = None
    humidity_max: Optional[float] = None
    mature_height_min: Optional[float] = None
    mature_height_max: Optional[float] = None
    space_requirement: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = []
    benefits: Optional[List[str]] = []
    description: Optional[str] = None
    care_tips: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=255)
    popularity_score: float = Field(50.0, ge=0, le=100)
    beginner_friendly: int = Field(1, ge=0, le=1)


class PlantSpeciesUpdate(BaseModel):
    """更新植物物种"""
    plant_name: Optional[str] = Field(None, max_length=100)
    scientific_name: Optional[str] = Field(None, max_length=100)
    family: Optional[str] = Field(None, max_length=50)
    genus: Optional[str] = Field(None, max_length=50)
    care_difficulty: Optional[str] = None
    light_requirement: Optional[str] = Field(None, max_length=50)
    water_frequency: Optional[str] = Field(None, max_length=50)
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    humidity_min: Optional[float] = None
    humidity_max: Optional[float] = None
    mature_height_min: Optional[float] = None
    mature_height_max: Optional[float] = None
    space_requirement: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    description: Optional[str] = None
    care_tips: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=255)
    popularity_score: Optional[float] = Field(None, ge=0, le=100)
    beginner_friendly: Optional[int] = Field(None, ge=0, le=1)


class PlantSpeciesResponse(BaseModel):
    """植物物种响应"""
    id: int
    plant_name: str
    scientific_name: Optional[str] = None
    family: Optional[str] = None
    genus: Optional[str] = None
    care_difficulty: str
    light_requirement: Optional[str] = None
    water_frequency: Optional[str] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    humidity_min: Optional[float] = None
    humidity_max: Optional[float] = None
    mature_height_min: Optional[float] = None
    mature_height_max: Optional[float] = None
    space_requirement: Optional[str] = None
    tags: Optional[List[str]] = []
    benefits: Optional[List[str]] = []
    description: Optional[str] = None
    care_tips: Optional[str] = None
    image_url: Optional[str] = None
    popularity_score: float
    beginner_friendly: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

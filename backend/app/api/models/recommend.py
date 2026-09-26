from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.api.core.database import Base


class PlantSpecies(Base):
    """植物物种库 - 用于推荐的植物数据库"""
    __tablename__ = "plant_species"

    id = Column(Integer, primary_key=True, index=True)
    plant_name = Column(String(100), nullable=False, comment="植物名称")
    scientific_name = Column(String(100), comment="学名")
    family = Column(String(50), comment="科")
    genus = Column(String(50), comment="属")
    
    # 养护难度
    care_difficulty = Column(String(20), default="medium", comment="养护难度: easy/medium/hard")
    
    # 环境需求
    light_requirement = Column(String(50), comment="光照需求: low/medium/high/full_sun")
    water_frequency = Column(String(50), comment="浇水频率: daily/every_2_days/weekly/biweekly/monthly")
    temperature_min = Column(Float, comment="最低温度(°C)")
    temperature_max = Column(Float, comment="最高温度(°C)")
    humidity_min = Column(Float, comment="最低湿度(%)")
    humidity_max = Column(Float, comment="最高湿度(%)")
    
    # 空间需求
    mature_height_min = Column(Float, comment="成熟高度最小值(cm)")
    mature_height_max = Column(Float, comment="成熟高度最大值(cm)")
    space_requirement = Column(String(50), comment="空间需求: small/medium/large")
    
    # 特性标签
    tags = Column(JSON, comment="特性标签数组，如：开花、观叶、多肉、空气净化等")
    benefits = Column(JSON, comment="功效数组，如：净化空气、药用、食用等")
    
    # 描述信息
    description = Column(Text, comment="植物描述")
    care_tips = Column(Text, comment="养护技巧")
    
    # 图片
    image_url = Column(String(255), comment="植物图片URL")
    
    # 推荐权重
    popularity_score = Column(Float, default=50.0, comment="受欢迎程度(0-100)")
    beginner_friendly = Column(Integer, default=1, comment="是否适合新手: 0/1")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RecommendationHistory(Base):
    """推荐历史记录"""
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    questionnaire_data = Column(JSON, comment="问卷答案数据")
    recommended_plants = Column(JSON, comment="推荐的植物列表")
    created_at = Column(DateTime, server_default=func.now())

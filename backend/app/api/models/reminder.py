from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, SmallInteger, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from app.api.core.database import Base

class RemindConfig(Base):
    """提醒配置表"""
    __tablename__ = "remind_config"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user_plant_id = Column(Integer, ForeignKey("user_plant.id", ondelete="SET NULL"))
    remind_type = Column(Enum('water', 'fertilize', 'pesticide', 'prune', 'other'), nullable=False)
    frequency_type = Column(Enum('daily', 'weekly', 'monthly', 'interval', 'one_time', 'seasonal'), nullable=False)
    interval_days = Column(Integer, default=0)  # 浇水间隔天数（用于季节性浇水）
    scheduled_date = Column(Date)  # 下次提醒日期
    repeat_interval = Column(Integer, default=0)
    custom_message = Column(String(255))
    is_enabled = Column(Boolean, default=True)
    
    # 养护提醒专用字段
    product_name = Column(String(100))  # 产品/药品名称
    dosage = Column(String(50))  # 用量
    application_date = Column(Date)  # 应用日期（施肥/施药/修剪日期）
    notes = Column(Text)  # 备注
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class WateringReminder(Base):
    """浇水提醒记录表 - 记录每日的提醒状态"""
    __tablename__ = "watering_reminder"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user_plant_id = Column(Integer, ForeignKey("user_plant.id", ondelete="CASCADE"), nullable=False)
    reminder_date = Column(Date, nullable=False)  # 提醒日期
    status = Column(Enum('pending', 'completed', 'postponed'), default='pending')  # 提醒状态
    completed_at = Column(DateTime)  # 完成时间
    completed_time_slot = Column(Enum('morning', 'noon', 'evening'))  # 完成时间段
    postpone_count = Column(Integer, default=0)  # 推迟次数
    notes = Column(Text)  # 备注
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
# backend/app/schemas/reminder.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime

class ReminderCreate(BaseModel):
    """创建提醒请求"""
    plant_id: Optional[int] = Field(None, description="关联植物档案ID")
    remind_type: str = Field(..., description="类型: water/fertilize/pesticide/prune/other")
    frequency_type: str = Field(..., description="周期: daily/weekly/monthly/interval/one_time")
    interval_days: Optional[int] = Field(0, ge=0, description="间隔天数")
    start_date: Optional[date] = Field(None, description="开始日期")
    repeat_interval: Optional[int] = Field(0, ge=0, description="重复间隔(天)")
    custom_message: Optional[str] = Field(None, max_length=255, description="自定义消息")

    @validator('remind_type')
    def validate_remind_type(cls, v):
        allowed = ['water', 'fertilize', 'pesticide', 'prune', 'other']
        if v not in allowed:
            raise ValueError(f'类型必须是 {allowed} 之一')
        return v

    @validator('frequency_type')
    def validate_frequency_type(cls, v):
        allowed = ['daily', 'weekly', 'monthly', 'interval', 'one_time']
        if v not in allowed:
            raise ValueError(f'周期类型必须是 {allowed} 之一')
        return v

class ReminderUpdate(BaseModel):
    """更新提醒请求"""
    remind_type: Optional[str] = None
    frequency_type: Optional[str] = None
    interval_days: Optional[int] = Field(None, ge=0)
    scheduled_date: Optional[date] = None
    repeat_interval: Optional[int] = Field(None, ge=0)
    custom_message: Optional[str] = Field(None, max_length=255)
    is_enabled: Optional[bool] = None

class ReminderResponse(BaseModel):
    """提醒响应"""
    id: int
    plant_id: Optional[int] = None
    plant_nickname: Optional[str] = None
    plant_name: Optional[str] = None
    remind_type: str
    frequency_type: str
    interval_days: int
    scheduled_date: Optional[date] = None
    next_date: Optional[date] = None
    custom_message: Optional[str] = None
    is_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TodayReminderResponse(BaseModel):
    """今日提醒响应"""
    id: int
    user_id: int
    plant_nickname: Optional[str] = None
    remind_type: str
    message: str
    scheduled_date: date
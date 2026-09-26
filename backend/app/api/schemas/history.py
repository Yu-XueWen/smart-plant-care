# backend/app/schemas/history.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class HistoryItem(BaseModel):
    """历史记录项"""
    id: int
    image_url: str
    created_at: datetime

class IdentifyHistoryItem(HistoryItem):
    """识花历史记录项"""
    plant_name: str
    confidence: Optional[float] = None

class DiagnoseHistoryItem(HistoryItem):
    """诊断历史记录项"""
    disease_name: str
    confidence: Optional[float] = None

class IdentifyHistoryDetail(IdentifyHistoryItem):
    """识花历史详情"""
    result_detail: Dict[str, Any]

class DiagnoseHistoryDetail(DiagnoseHistoryItem):
    """诊断历史详情"""
    symptoms: Optional[str] = None
    treatment: Optional[Dict[str, Any]] = None

class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    total: int
    items: List[HistoryItem]
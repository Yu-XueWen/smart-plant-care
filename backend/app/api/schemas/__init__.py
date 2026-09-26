# backend/app/schemas/__init__.py
from .common import ResponseModel, ErrorResponse
from .user import UserRegister, UserLogin, UserResponse, TokenResponse
from .plant import (
    PlantCreate, PlantUpdate, PlantResponse,
    WateringCreate, WateringResponse,
    TreatmentCreate, TreatmentResponse
)
from .reminder import ReminderCreate, ReminderUpdate, ReminderResponse
from .ai import (
    IdentifyRequest, IdentifyResponse,
    DiagnoseRequest, DiagnoseResponse,
    DetectPlantResponse
)
from .history import HistoryItem, HistoryListResponse

__all__ = [
    "ResponseModel", "ErrorResponse",
    "UserCreate", "UserLogin", "UserResponse", "TokenResponse",
    "PlantCreate", "PlantUpdate", "PlantResponse",
    "WateringCreate", "WateringResponse",
    "TreatmentCreate", "TreatmentResponse",
    "ReminderCreate", "ReminderUpdate", "ReminderResponse",
    "IdentifyRequest", "IdentifyResponse", "IdentifyResult",
    "DiagnoseRequest", "DiagnoseResponse", "DiagnoseResult",
    "DetectPlantResponse",
    "HistoryItem", "HistoryListResponse"
]
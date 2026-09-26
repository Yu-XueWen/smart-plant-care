file_path = r"d:\Improve\smart-plant-care\backend\app\api\models\__init__.py"

content = """# 导入所有模型以确保它们被注册到Base.metadata
from app.api.models.user import User
from app.api.models.plant import UserPlant, WateringRecord, TreatmentRecord
from app.api.models.reminder import RemindConfig
from app.api.models.history import IdentifyHistory, DiagnoseHistory
from app.api.models.recommend import PlantSpecies, RecommendationHistory

from app.api.models.operation_log import OperationLog
from app.api.models.login_log import LoginLog

__all__ = [
    "User",
    "UserPlant",
    "WateringRecord",
    "TreatmentRecord",
    "RemindConfig",
    "IdentifyHistory",
    "DiagnoseHistory",
    "PlantSpecies",
    "RecommendationHistory",
    "OperationLog",
    "LoginLog"
]
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {file_path}")
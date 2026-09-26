# backend/app/services/plant_service.py
import logging
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.models.plant import UserPlant, WateringRecord, TreatmentRecord
from app.api.models.reminder import RemindConfig

logger = logging.getLogger(__name__)


class PlantService:
    """植物档案业务服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_plants_summary(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户植物摘要（用于首页）"""
        plants = self.db.query(UserPlant).filter(
            UserPlant.user_id == user_id,
            UserPlant.status == 1
        ).all()

        today = date.today()
        result = []

        for plant in plants:
            # 最近浇水天数
            last_water = self.db.query(WateringRecord).filter(
                WateringRecord.user_plant_id == plant.id
            ).order_by(desc(WateringRecord.watering_date)).first()

            last_water_days = (today - last_water.watering_date).days if last_water else None

            # 最近给药天数
            last_treatment = self.db.query(TreatmentRecord).filter(
                TreatmentRecord.user_plant_id == plant.id,
                TreatmentRecord.treatment_type == "pesticide"
            ).order_by(desc(TreatmentRecord.application_date)).first()

            last_treatment_days = (today - last_treatment.application_date).days if last_treatment else None

            # 获取待办提醒数量
            pending_reminders = self.db.query(RemindConfig).filter(
                RemindConfig.user_plant_id == plant.id,
                RemindConfig.is_enabled == True,
                RemindConfig.scheduled_date <= today
            ).count()

            result.append({
                "id": plant.id,
                "nickname": plant.nickname or plant.plant_name,
                "plant_name": plant.plant_name,
                "thumbnail": plant.initial_photos[0] if plant.initial_photos else None,
                "last_water_days": last_water_days,
                "last_treatment_days": last_treatment_days,
                "pending_reminders": pending_reminders,
                "status": "warning" if (last_water_days and last_water_days > 7) else "normal"
            })

        return result

    def get_plant_statistics(self, plant_id: int, user_id: int) -> Dict[str, Any]:
        """获取植物统计信息"""
        plant = self.db.query(UserPlant).filter(
            UserPlant.id == plant_id,
            UserPlant.user_id == user_id
        ).first()

        if not plant:
            return {}

        today = date.today()
        month_start = date(today.year, today.month, 1)

        # 浇水统计
        water_count = self.db.query(WateringRecord).filter(
            WateringRecord.user_plant_id == plant_id
        ).count()

        water_this_month = self.db.query(WateringRecord).filter(
            WateringRecord.user_plant_id == plant_id,
            WateringRecord.watering_date >= month_start
        ).count()

        # 养护统计
        treatment_count = self.db.query(TreatmentRecord).filter(
            TreatmentRecord.user_plant_id == plant_id
        ).count()

        # 提醒统计
        reminder_count = self.db.query(RemindConfig).filter(
            RemindConfig.user_plant_id == plant_id,
            RemindConfig.is_enabled == True
        ).count()

        # 栽种天数
        planting_days = (today - plant.planting_date).days if plant.planting_date else None

        return {
            "planting_days": planting_days,
            "total_watering": water_count,
            "watering_this_month": water_this_month,
            "total_treatments": treatment_count,
            "active_reminders": reminder_count,
            "avg_watering_interval": self._calc_avg_watering_interval(plant_id)
        }

    def _calc_avg_watering_interval(self, plant_id: int) -> Optional[float]:
        """计算平均浇水间隔"""
        records = self.db.query(WateringRecord).filter(
            WateringRecord.user_plant_id == plant_id
        ).order_by(WateringRecord.watering_date).all()

        if len(records) < 2:
            return None

        intervals = []
        for i in range(1, len(records)):
            interval = (records[i].watering_date - records[i - 1].watering_date).days
            intervals.append(interval)

        return sum(intervals) / len(intervals) if intervals else None


# 工厂函数
def get_plant_service(db: Session) -> PlantService:
    return PlantService(db)
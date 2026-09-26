# backend/app/services/reminder_service.py
import logging
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.api.models.reminder import RemindConfig
from app.api.models.plant import UserPlant

logger = logging.getLogger(__name__)


class ReminderService:
    """提醒服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_due_reminders(self, target_date: Optional[date] = None) -> List[RemindConfig]:
        """获取到期的提醒"""
        if target_date is None:
            target_date = date.today()

        reminders = self.db.query(RemindConfig).filter(
            RemindConfig.is_enabled == True,
            RemindConfig.scheduled_date <= target_date
        ).all()

        return reminders

    def update_next_reminder_date(self, reminder: RemindConfig) -> Optional[date]:
        """更新下次提醒日期"""
        if reminder.repeat_interval > 0:
            next_date = reminder.scheduled_date + timedelta(days=reminder.repeat_interval)
            reminder.scheduled_date = next_date
            self.db.commit()
            return next_date
        else:
            reminder.is_enabled = False
            self.db.commit()
            return None

    def process_due_reminders(self) -> List[Dict[str, Any]]:
        """处理所有到期的提醒"""
        due_reminders = self.get_due_reminders()
        result = []

        for reminder in due_reminders:
            plant = None
            if reminder.user_plant_id:
                plant = self.db.query(UserPlant).filter(
                    UserPlant.id == reminder.user_plant_id
                ).first()

            plant_name = plant.nickname or plant.plant_name if plant else "我的植物"
            message = reminder.custom_message or self._get_default_message(
                reminder.remind_type, plant_name
            )

            result.append({
                "id": reminder.id,
                "user_id": reminder.user_id,
                "plant_id": reminder.user_plant_id,
                "plant_name": plant_name,
                "remind_type": reminder.remind_type,
                "message": message,
                "scheduled_date": reminder.scheduled_date.isoformat() if reminder.scheduled_date else None
            })

            self.update_next_reminder_date(reminder)

        return result

    def _get_default_message(self, remind_type: str, plant_name: str) -> str:
        """获取默认提醒消息"""
        messages = {
            "water": f"💧 该给 {plant_name} 浇水啦！",
            "fertilize": f"🌱 该给 {plant_name} 施肥了！",
            "pesticide": f"🛡️ 该给 {plant_name} 进行病虫害防治了！",
            "prune": f"✂️ 该给 {plant_name} 修剪了！",
            "other": f"📋 {plant_name} 有新的养护任务！"
        }
        return messages.get(remind_type, f"📋 {plant_name} 有新的养护任务！")

    def get_upcoming_reminders(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """获取用户近期待办提醒"""
        today = date.today()
        future_date = today + timedelta(days=days)

        reminders = self.db.query(RemindConfig).filter(
            RemindConfig.user_id == user_id,
            RemindConfig.is_enabled == True,
            RemindConfig.scheduled_date.between(today, future_date)
        ).order_by(RemindConfig.scheduled_date).all()

        result = []
        for r in reminders:
            plant = self.db.query(UserPlant).filter(UserPlant.id == r.user_plant_id).first()
            plant_name = plant.nickname or plant.plant_name if plant else "未知植物"
            days_left = (r.scheduled_date - today).days

            result.append({
                "id": r.id,
                "plant_name": plant_name,
                "remind_type": r.remind_type,
                "due_date": r.scheduled_date.isoformat(),
                "days_left": days_left,
                "message": r.custom_message or self._get_default_message(r.remind_type, plant_name)
            })

        return result


# 单例实例（需要 db session 时请使用 get_reminder_service）
# reminder_service = None  # 移除，因为需要 db session

# 工厂函数
def get_reminder_service(db: Session) -> ReminderService:
    return ReminderService(db)
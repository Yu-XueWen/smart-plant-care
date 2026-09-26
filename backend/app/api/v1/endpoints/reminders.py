# backend/app/api/v1/endpoints/reminders.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, date, timedelta
from typing import Optional
from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.api.models.user import User
from app.api.models.plant import UserPlant
from app.api.models.reminder import RemindConfig
from app.api.schemas.reminder import ReminderCreate, ReminderUpdate, ReminderResponse
from app.api.schemas.common import ResponseModel
from app.api.services.scheduler import trigger_immediate_check

router = APIRouter()


@router.get("", response_model=ResponseModel)
def get_reminders(
        plant_id: Optional[int] = Query(None),
        is_enabled: Optional[bool] = Query(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    query = db.query(RemindConfig).filter(RemindConfig.user_id == current_user.id)

    if plant_id:
        query = query.filter(RemindConfig.user_plant_id == plant_id)
    if is_enabled is not None:
        query = query.filter(RemindConfig.is_enabled == is_enabled)

    items = query.order_by(desc(RemindConfig.created_at)).all()

    result = []
    for r in items:
        plant = db.query(UserPlant).filter(UserPlant.id == r.user_plant_id).first()
        result.append({
            "id": r.id,
            "plant_id": r.user_plant_id,
            "plant_nickname": plant.nickname if plant else None,
            "plant_name": plant.plant_name if plant else None,
            "remind_type": r.remind_type,
            "frequency_type": r.frequency_type,
            "interval_days": r.interval_days,
            "scheduled_date": r.scheduled_date.isoformat() if r.scheduled_date else None,
            "next_date": r.scheduled_date.isoformat() if r.scheduled_date else None,
            "custom_message": r.custom_message,
            "is_enabled": r.is_enabled,
            "created_at": r.created_at.isoformat()
        })

    return ResponseModel(data={"items": result})


@router.post("", response_model=ResponseModel)
def create_reminder(
        reminder_data: ReminderCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 验证植物存在（如果指定了）
    if reminder_data.plant_id:
        plant = db.query(UserPlant).filter(
            UserPlant.id == reminder_data.plant_id,
            UserPlant.user_id == current_user.id
        ).first()
        if not plant:
            raise HTTPException(status_code=404, detail="植物档案不存在")

    # 计算下次提醒日期
    scheduled_date = reminder_data.start_date or date.today()
    if reminder_data.frequency_type == "interval" and reminder_data.interval_days:
        scheduled_date = date.today() + timedelta(days=reminder_data.interval_days)

    new_reminder = RemindConfig(
        user_id=current_user.id,
        user_plant_id=reminder_data.plant_id,
        remind_type=reminder_data.remind_type,
        frequency_type=reminder_data.frequency_type,
        interval_days=reminder_data.interval_days or 0,
        scheduled_date=scheduled_date,
        repeat_interval=reminder_data.repeat_interval or 0,
        custom_message=reminder_data.custom_message,
        is_enabled=True,
        created_at=datetime.now()
    )
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)

    # 立即触发一次提醒检查（如果新创建的提醒已到期，即刻通知）
    if scheduled_date <= date.today():
        trigger_immediate_check()

    return ResponseModel(data={"reminder_id": new_reminder.id})


@router.put("/{reminder_id}", response_model=ResponseModel)
def update_reminder(
        reminder_id: int,
        reminder_data: ReminderUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reminder = db.query(RemindConfig).filter(
        RemindConfig.id == reminder_id,
        RemindConfig.user_id == current_user.id
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")

    update_data = reminder_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reminder, key, value)

    reminder.updated_at = datetime.now()
    db.commit()

    return ResponseModel(message="更新成功")


@router.delete("/{reminder_id}", response_model=ResponseModel)
def delete_reminder(
        reminder_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reminder = db.query(RemindConfig).filter(
        RemindConfig.id == reminder_id,
        RemindConfig.user_id == current_user.id
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")

    db.delete(reminder)
    db.commit()

    return ResponseModel(message="删除成功")


@router.get("/today", response_model=ResponseModel)
def get_today_reminders(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取今日待发送提醒（供内部定时任务调用）"""
    today = date.today()
    reminders = db.query(RemindConfig).filter(
        RemindConfig.user_id == current_user.id,
        RemindConfig.is_enabled == True,
        RemindConfig.scheduled_date <= today
    ).all()

    result = []
    for r in reminders:
        plant = db.query(UserPlant).filter(UserPlant.id == r.user_plant_id).first()
        result.append({
            "id": r.id,
            "user_id": r.user_id,
            "plant_nickname": plant.nickname if plant else None,
            "remind_type": r.remind_type,
            "message": r.custom_message or f"记得{get_remind_type_name(r.remind_type)}{plant.nickname or ''}",
            "scheduled_date": r.scheduled_date.isoformat()
        })

    return ResponseModel(data={"items": result})


def get_remind_type_name(remind_type: str) -> str:
    types = {"water": "浇水", "fertilize": "施肥", "pesticide": "施药", "prune": "修剪", "other": "养护"}
    return types.get(remind_type, "养护")
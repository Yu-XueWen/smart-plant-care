# backend/app/api/v1/endpoints/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Dict, Any

from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.api.models.user import User
from app.api.models.plant import UserPlant, WateringRecord, TreatmentRecord
from app.api.models.reminder import RemindConfig
from app.api.schemas.common import ResponseModel

router = APIRouter()


@router.get("/summary", response_model=ResponseModel)
def get_dashboard_summary(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取首页概览数据"""
    # 植物总数
    total_plants = db.query(UserPlant).filter(
        UserPlant.user_id == current_user.id,
        UserPlant.status == 1
    ).count()

    # 本月浇水次数
    today = date.today()
    month_start = date(today.year, today.month, 1)
    water_this_month = db.query(WateringRecord).join(UserPlant).filter(
        UserPlant.user_id == current_user.id,
        WateringRecord.watering_date >= month_start
    ).count()

    # 待办提醒数
    pending_reminders = db.query(RemindConfig).filter(
        RemindConfig.user_id == current_user.id,
        RemindConfig.is_enabled == True,
        RemindConfig.scheduled_date <= today
    ).count()

    # 识别历史数
    from app.models.history import IdentifyHistory
    identify_count = db.query(IdentifyHistory).filter(
        IdentifyHistory.user_id == current_user.id
    ).count()

    return ResponseModel(data={
        "total_plants": total_plants,
        "water_this_month": water_this_month,
        "pending_reminders": pending_reminders,
        "identify_count": identify_count
    })


@router.get("/plants", response_model=ResponseModel)
def get_dashboard_plants(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取首页植物档案摘要"""
    plants = db.query(UserPlant).filter(
        UserPlant.user_id == current_user.id,
        UserPlant.status == 1
    ).all()

    today = date.today()
    result = []

    for plant in plants:
        # 最近浇水
        last_water = db.query(WateringRecord).filter(
            WateringRecord.user_plant_id == plant.id
        ).order_by(WateringRecord.watering_date.desc()).first()

        last_water_days = (today - last_water.watering_date).days if last_water else None

        # 最近给药
        last_treatment = db.query(TreatmentRecord).filter(
            TreatmentRecord.user_plant_id == plant.id,
            TreatmentRecord.treatment_type == "pesticide"
        ).order_by(TreatmentRecord.application_date.desc()).first()

        last_treatment_days = (today - last_treatment.application_date).days if last_treatment else None

        result.append({
            "id": plant.id,
            "nickname": plant.nickname or plant.plant_name,
            "plant_name": plant.plant_name,
            "thumbnail": plant.initial_photos[0] if plant.initial_photos else None,
            "last_water_days": last_water_days,
            "last_treatment_days": last_treatment_days,
            "status": "warning" if (last_water_days and last_water_days > 7) else "normal"
        })

    return ResponseModel(data={
        "total_plants": len(plants),
        "plants": result
    })


@router.get("/tasks", response_model=ResponseModel)
def get_dashboard_tasks(
        days: int = Query(7, ge=1, le=30, description="未来天数"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取近期待办提醒"""
    today = date.today()
    future_date = today + timedelta(days=days)

    reminders = db.query(RemindConfig).filter(
        RemindConfig.user_id == current_user.id,
        RemindConfig.is_enabled == True,
        RemindConfig.scheduled_date.between(today, future_date)
    ).order_by(RemindConfig.scheduled_date).limit(20).all()

    result = []
    type_names = {"water": "浇水", "fertilize": "施肥", "pesticide": "施药", "prune": "修剪", "other": "养护"}

    for r in reminders:
        plant = db.query(UserPlant).filter(UserPlant.id == r.user_plant_id).first()
        plant_name = plant.nickname or plant.plant_name if plant else "未知植物"
        days_left = (r.scheduled_date - today).days

        result.append({
            "id": r.id,
            "plant_name": plant_name,
            "type": r.remind_type,
            "type_name": type_names.get(r.remind_type, "养护"),
            "due_date": r.scheduled_date.isoformat(),
            "days_left": days_left
        })

    return ResponseModel(data={"tasks": result})
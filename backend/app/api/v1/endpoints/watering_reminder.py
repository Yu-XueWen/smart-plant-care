"""
浇水提醒管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
import logging

from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.api.models.user import User
from app.api.schemas.common import ResponseModel
from app.api.services.watering_reminder_service import WateringReminderService
from app.api.services.scheduler import trigger_immediate_check

logger = logging.getLogger(__name__)

router = APIRouter()
reminder_service = WateringReminderService()


@router.post("/plants/{plant_id}/setup-reminder", response_model=ResponseModel)
def setup_watering_reminder(
    plant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为植物设置浇水提醒
    
    Args:
        plant_id: 植物ID
        
    Returns:
        提醒配置信息
    """
    try:
        logger.info(f"收到设置浇水提醒请求: plant_id={plant_id}, user_id={current_user.id}")
        result = reminder_service.create_or_update_watering_reminder(
            db=db,
            user_id=current_user.id,
            plant_id=plant_id
        )
        logger.info(f"设置浇水提醒成功: {result}")
        
        # 立即触发一次提醒检查（确保刚设置的提醒能即时生效）
        trigger_immediate_check()
        
        return ResponseModel(
            code=200,
            message="浇水提醒设置成功",
            data=result
        )
    except ValueError as e:
        logger.error(f"设置浇水提醒失败(404): {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"设置浇水提醒异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"设置提醒失败: {str(e)}")


@router.get("/today", response_model=ResponseModel)
def get_today_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取今日的浇水提醒列表
    
    Returns:
        今日需要浇水的植物列表
    """
    try:
        reminders = reminder_service.get_today_reminders(
            db=db,
            user_id=current_user.id
        )
        
        return ResponseModel(
            code=200,
            message="查询成功",
            data={
                "date": date.today().isoformat(),
                "count": len(reminders),
                "reminders": reminders
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/{reminder_id}/complete", response_model=ResponseModel)
def complete_watering_reminder(
    reminder_id: int,
    time_slot: str = "morning",  # morning, noon, evening
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    完成浇水提醒
    
    Args:
        reminder_id: 提醒ID
        time_slot: 时间段 (morning/noon/evening)
        
    Returns:
        操作结果
    """
    if time_slot not in ['morning', 'noon', 'evening']:
        raise HTTPException(status_code=400, detail="无效的时间段")
    
    try:
        result = reminder_service.complete_watering_reminder(
            db=db,
            user_id=current_user.id,
            reminder_id=reminder_id,
            time_slot=time_slot
        )
        
        return ResponseModel(
            code=200,
            message=result["message"],
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.post("/{reminder_id}/postpone", response_model=ResponseModel)
def postpone_watering_reminder(
    reminder_id: int,
    postpone_hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    推迟浇水提醒
    
    Args:
        reminder_id: 提醒ID
        postpone_hours: 推迟小时数，默认24小时
        
    Returns:
        操作结果
    """
    try:
        result = reminder_service.postpone_watering_reminder(
            db=db,
            user_id=current_user.id,
            reminder_id=reminder_id,
            postpone_hours=postpone_hours
        )
        
        return ResponseModel(
            code=200,
            message=result["message"],
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.get("/config/{plant_id}", response_model=ResponseModel)
def get_reminder_config(
    plant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取植物的浇水提醒配置
    
    Args:
        plant_id: 植物ID
        
    Returns:
        提醒配置信息，包括最近一次浇水日期
    """
    from app.api.models.reminder import RemindConfig
    from app.api.models.plant import WateringRecord
    
    config = db.query(RemindConfig).filter(
        RemindConfig.user_id == current_user.id,
        RemindConfig.user_plant_id == plant_id,
        RemindConfig.remind_type == 'water'
    ).first()
    
    # 查询最近一次浇水记录
    latest_watering = db.query(WateringRecord).filter(
        WateringRecord.user_plant_id == plant_id
    ).order_by(WateringRecord.watering_date.desc()).first()
    
    if not config:
        return ResponseModel(
            code=200,
            message="未找到提醒配置",
            data=None
        )
    
    return ResponseModel(
        code=200,
        message="查询成功",
        data={
            "id": config.id,
            "interval_days": config.interval_days,
            "scheduled_date": config.scheduled_date.isoformat() if config.scheduled_date else None,
            "frequency_type": config.frequency_type,
            "is_enabled": config.is_enabled,
            "current_season": reminder_service.get_current_season(),
            "season_name": reminder_service.get_season_name_cn(reminder_service.get_current_season()),
            "last_watering_date": latest_watering.watering_date.isoformat() if latest_watering else None
        }
    )

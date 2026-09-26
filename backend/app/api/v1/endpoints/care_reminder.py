"""
养护提醒管理API（施肥、施药、修剪等）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import logging

from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.api.models.user import User
from app.api.schemas.common import ResponseModel
from app.api.services.care_reminder_service import CareReminderService
from app.api.services.scheduler import trigger_immediate_check

logger = logging.getLogger(__name__)

router = APIRouter()
care_service = CareReminderService()


@router.post("", response_model=ResponseModel)
def create_care_reminder(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建养护提醒
    
    Args:
        data: 提醒数据
            - plant_id: 植物ID (可选)
            - remind_type: 类型 (fertilize/pesticide/prune/other)
            - scheduled_date: 计划日期 (YYYY-MM-DD)
            - product_name: 产品/药品名称 (可选)
            - dosage: 用量 (可选)
            - notes: 备注 (可选)
            - frequency_type: 频率类型 (one_time/daily/weekly/monthly)
            - is_enabled: 是否启用
            
    Returns:
        创建的提醒信息
    """
    try:
        logger.info(f"收到创建养护提醒请求: user_id={current_user.id}")
        
        result = care_service.create_care_reminder(
            db=db,
            user_id=current_user.id,
            data=data
        )
        
        # 立即触发一次提醒检查（如果新创建的提醒已到期，即刻通知）
        from datetime import date
        scheduled_str = data.get('scheduled_date', '')
        if scheduled_str:
            try:
                scheduled_date = date.fromisoformat(scheduled_str) if isinstance(scheduled_str, str) else scheduled_str
                if scheduled_date <= date.today():
                    trigger_immediate_check()
            except (ValueError, TypeError):
                pass
        
        return ResponseModel(
            code=200,
            message="养护提醒创建成功",
            data=result
        )
    except ValueError as e:
        logger.error(f"创建养护提醒失败(404): {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"创建养护提醒异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("", response_model=ResponseModel)
def get_care_reminders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    remind_type: Optional[str] = Query(None, description="提醒类型过滤"),
    status_filter: Optional[str] = Query(None, description="状态过滤: pending/completed"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取养护提醒列表
    
    Returns:
        提醒列表和分页信息
    """
    try:
        result = care_service.get_user_reminders(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            remind_type=remind_type,
            status_filter=status_filter
        )
        
        return ResponseModel(
            code=200,
            message="查询成功",
            data=result
        )
    except Exception as e:
        logger.error(f"查询养护提醒失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/{reminder_id}", response_model=ResponseModel)
def get_reminder_detail(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取提醒详情
    
    Args:
        reminder_id: 提醒ID
        
    Returns:
        提醒详情
    """
    try:
        result = care_service.get_reminder_detail(
            db=db,
            user_id=current_user.id,
            reminder_id=reminder_id
        )
        
        return ResponseModel(
            code=200,
            message="查询成功",
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.put("/{reminder_id}", response_model=ResponseModel)
def update_reminder(
    reminder_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新提醒
    
    Args:
        reminder_id: 提醒ID
        data: 更新数据
        
    Returns:
        更新后的提醒信息
    """
    try:
        result = care_service.update_reminder(
            db=db,
            user_id=current_user.id,
            reminder_id=reminder_id,
            data=data
        )
        
        return ResponseModel(
            code=200,
            message="更新成功",
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/{reminder_id}", response_model=ResponseModel)
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除提醒
    
    Args:
        reminder_id: 提醒ID
        
    Returns:
        操作结果
    """
    try:
        care_service.delete_reminder(
            db=db,
            user_id=current_user.id,
            reminder_id=reminder_id
        )
        
        return ResponseModel(
            code=200,
            message="删除成功"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/{reminder_id}/complete", response_model=ResponseModel)
def complete_reminder_and_sync(
    reminder_id: int,
    actual_date: Optional[str] = Query(None, description="实际执行日期 YYYY-MM-DD"),
    actual_product: Optional[str] = Query(None, description="实际使用的产品"),
    actual_dosage: Optional[str] = Query(None, description="实际用量"),
    actual_notes: Optional[str] = Query(None, description="实际备注"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    完成提醒并同步到养护记录表
    
    Args:
        reminder_id: 提醒ID
        actual_date: 实际执行日期（默认使用提醒的计划日期）
        actual_product: 实际使用的产品（默认使用提醒中的产品）
        actual_dosage: 实际用量（默认使用提醒中的用量）
        actual_notes: 实际备注（会与提醒备注合并）
        
    Returns:
        操作结果和创建的养护记录信息
    """
    try:
        # 解析日期
        execution_date = None
        if actual_date:
            execution_date = date.fromisoformat(actual_date)
        
        result = care_service.complete_and_sync_to_treatment(
            db=db,
            user_id=current_user.id,
            reminder_id=reminder_id,
            actual_date=execution_date,
            actual_product=actual_product,
            actual_dosage=actual_dosage,
            actual_notes=actual_notes
        )
        
        return ResponseModel(
            code=200,
            message=result["message"],
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"完成提醒失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")

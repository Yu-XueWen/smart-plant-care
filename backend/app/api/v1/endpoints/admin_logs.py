# backend/app/api/v1/endpoints/admin_logs.py
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta

from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_admin
from app.api.models.user import User
from app.api.models.operation_log import OperationLog
from app.api.models.login_log import LoginLog
from app.api.schemas.common import ResponseModel

router = APIRouter()


@router.get("/operations", response_model=ResponseModel)
def get_operation_logs(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        action: Optional[str] = Query(None, description="操作类型筛选"),
        admin_id: Optional[int] = Query(None, description="管理员ID筛选"),
        start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
        end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """获取操作日志列表"""
    query = db.query(OperationLog)
    
    if action:
        query = query.filter(OperationLog.action == action)
    if admin_id:
        query = query.filter(OperationLog.admin_id == admin_id)
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(OperationLog.created_at >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(OperationLog.created_at <= end)
    
    total = query.count()
    items = query.order_by(desc(OperationLog.created_at)) \
        .offset((page - 1) * page_size).limit(page_size).all()
    
    # 操作类型中文映射
    action_map = {
        'ban_user': '禁用用户',
        'unban_user': '启用用户',
        'reset_password': '重置密码',
        'delete_user': '删除用户',
        'create_role': '创建角色',
        'update_role': '更新角色',
        'delete_role': '删除角色',
        'assign_role': '分配角色',
        'view_dashboard': '查看看板',
        'view_logs': '查看日志',
        'view_system': '查看系统',
        'retrain_model': '重训练模型',
        'toggle_user_status': '切换用户状态'
    }
    
    return ResponseModel(data={
        "total": total,
        "items": [
            {
                "id": op.id,
                "admin_id": op.admin_id,
                "username": op.username,
                "action": op.action,
                "action_label": action_map.get(op.action, op.action),
                "target_type": op.target_type,
                "target_id": op.target_id,
                "detail": op.detail,
                "ip_address": op.ip_address,
                "created_at": op.created_at.isoformat()
            }
            for op in items
        ]
    })


@router.get("/login", response_model=ResponseModel)
def get_login_logs(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        username: Optional[str] = Query(None, description="用户名筛选"),
        success: Optional[bool] = Query(None, description="登录成功筛选"),
        start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
        end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """获取登录日志列表"""
    query = db.query(LoginLog)
    
    if username:
        query = query.filter(LoginLog.username.like(f"%{username}%"))
    if success is not None:
        query = query.filter(LoginLog.success == success)
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(LoginLog.login_time >= start)
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(LoginLog.login_time <= end)
    
    total = query.count()
    items = query.order_by(desc(LoginLog.login_time)) \
        .offset((page - 1) * page_size).limit(page_size).all()
    
    return ResponseModel(data={
        "total": total,
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "username": log.username,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "login_time": log.login_time.isoformat() if log.login_time else None,
                "logout_time": log.logout_time.isoformat() if log.logout_time else None,
                "duration_seconds": log.duration_seconds,
                "success": log.success
            }
            for log in items
        ]
    })

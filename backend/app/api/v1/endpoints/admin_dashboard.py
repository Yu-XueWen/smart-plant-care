from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_admin
from app.api.models.user import User
from app.api.models.plant import UserPlant
from app.api.models.history import IdentifyHistory, DiagnoseHistory
from app.api.models.operation_log import OperationLog
from app.api.models.login_log import LoginLog
from app.api.schemas.common import ResponseModel

router = APIRouter()


@router.get("/overview", response_model=ResponseModel)
def get_dashboard_overview(
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """获取管理员总览统计"""
    # 总用户数（不含管理员）
    total_users = db.query(User).filter(User.role != 'admin').count()
    
    # 总植物数
    total_plants = db.query(UserPlant).filter(UserPlant.status == 1).count()
    
    # 识别次数
    identify_count = db.query(IdentifyHistory).count()
    
    # 诊断次数
    diagnose_count = db.query(DiagnoseHistory).count()
    
    # 近期操作日志（最近 24 小时）
    today = datetime.now()
    twenty_four_hours_ago = today - timedelta(hours=24)
    recent_operation_logs = db.query(OperationLog).filter(
        OperationLog.created_at >= twenty_four_hours_ago
    ).count()
    
    return ResponseModel(data={
        "total_users": total_users,
        "total_plants": total_plants,
        "identify_count": identify_count,
        "diagnose_count": diagnose_count,
        "recent_operation_logs": recent_operation_logs,
        "timestamp": today.isoformat()
    })


@router.get("/today-stats", response_model=ResponseModel)
def get_today_stats(
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """获取今日统计数据"""
    today = datetime.now()
    start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)
    
    # 今日注册用户数
    new_users_today = db.query(User).filter(
        User.role != 'admin',
        User.created_at >= start_of_day
    ).count()
    
    # 今日登录用户数（成功登录）
    login_today = db.query(LoginLog).filter(
        LoginLog.login_time >= start_of_day,
        LoginLog.success == True
    ).distinct(LoginLog.username).count()
    
    # 今日识别次数
    identify_today = db.query(IdentifyHistory).filter(
        IdentifyHistory.created_at >= start_of_day
    ).count()
    
    # 今日诊断次数
    diagnose_today = db.query(DiagnoseHistory).filter(
        DiagnoseHistory.created_at >= start_of_day
    ).count()
    
    # 今日创建植物数
    plants_today = db.query(UserPlant).filter(
        UserPlant.status == 1,
        UserPlant.created_at >= start_of_day
    ).count()
    
    return ResponseModel(data={
        "new_users_today": new_users_today,
        "login_today": login_today,
        "identify_today": identify_today,
        "diagnose_today": diagnose_today,
        "plants_today": plants_today,
        "timestamp": today.isoformat()
    })


@router.get("/recent-activity", response_model=ResponseModel)
def get_recent_activity(
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=100)
):
    """获取近期动态"""
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    
    # 最近注册用户
    recent_users = db.query(User).filter(
        User.role != 'admin',
        User.created_at >= seven_days_ago
    ).order_by(User.created_at.desc()).limit(limit).all()
    
    # 最近管理员操作
    recent_operations = db.query(OperationLog).filter(
        OperationLog.created_at >= seven_days_ago
    ).order_by(OperationLog.created_at.desc()).limit(limit).all()
    
    return ResponseModel(data={
        "recent_users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "created_at": u.created_at.isoformat()
            } for u in recent_users
        ],
        "recent_operations": [
            {
                "id": op.id,
                "username": op.username,
                "action": op.action,
                "target_type": op.target_type,
                "detail": op.detail,
                "created_at": op.created_at.isoformat()
            } for op in recent_operations
        ]
    })


@router.get("/chart-data", response_model=ResponseModel)
def get_chart_data(
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        period: str = Query("7", description="7 or 30"),
        metric: str = Query("users", description="user_growth, identify_diagnose")
):
    """获取图表数据"""
    days = int(period)
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    if metric == "user_growth":
        # 每日新用户数
        data = []
        current = start_date
        while current <= today:
            user_count = db.query(User).filter(
                User.role != 'admin',
                User.created_at >= current.date(),
                User.created_at < current.date() + timedelta(days=1)
            ).count()
            data.append({
                "date": current.strftime("%Y-%m-%d"),
                "value": user_count
            })
            current += timedelta(days=1)
        
        return ResponseModel(data={
            "metric": "user_growth",
            "data": data
        })
    
    elif metric == "identify_diagnose":
        # 每日识别和诊断次数
        identify_data = []
        diagnose_data = []
        current = start_date
        while current <= today:
            identify_count = db.query(IdentifyHistory).filter(
                IdentifyHistory.created_at >= current.date(),
                IdentifyHistory.created_at < current.date() + timedelta(days=1)
            ).count()
            diagnose_count = db.query(DiagnoseHistory).filter(
                DiagnoseHistory.created_at >= current.date(),
                DiagnoseHistory.created_at < current.date() + timedelta(days=1)
            ).count()
            identify_data.append({
                "date": current.strftime("%Y-%m-%d"),
                "value": identify_count
            })
            diagnose_data.append({
                "date": current.strftime("%Y-%m-%d"),
                "value": diagnose_count
            })
            current += timedelta(days=1)
        
        return ResponseModel(data={
            "metric": "identify_diagnose",
            "identify": identify_data,
            "diagnose": diagnose_data
        })
    
    else:
        raise ValueError(f"Invalid metric: {metric}")

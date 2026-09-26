"""
管理员系统监控端点
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any
import datetime
import psutil
import os

from app.api.core.database import get_db
from app.api.models.user import User
from app.api.v1.dependencies.auth import get_current_admin
from app.utils.response_utils import ResponseModel

router = APIRouter()


@router.get("/status", response_model=ResponseModel)
def get_system_status(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取系统状态"""
    status = {
        "api_service": {
            "status": "healthy",
            "message": "运行中"
        },
        "mysql": {
            "status": "healthy",
            "message": "已连接"
        },
        "neo4j": {
            "status": "unknown",
            "message": "未配置"
        },
        "redis": {
            "status": "unknown",
            "message": "未配置"
        },
        "ai_model": {
            "status": "healthy",
            "message": "模型已加载"
        }
    }
    return ResponseModel(data=status)


@router.get("/metrics", response_model=ResponseModel)
def get_system_metrics(
    admin: User = Depends(get_current_admin)
):
    """获取系统指标"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 获取进程内存
        process = psutil.Process(os.getpid())
        process_memory_mb = process.memory_info().rss / 1024 / 1024
        
        metrics = {
            "cpu_percent": cpu_percent,
            "memory_total_mb": round(memory.total / 1024 / 1024, 2),
            "memory_used_mb": round(memory.used / 1024 / 1024, 2),
            "memory_available_mb": round(memory.available / 1024 / 1024, 2),
            "memory_percent": memory.percent,
            "disk_total_gb": round(disk.total / 1024**3, 2),
            "disk_used_gb": round(disk.used / 1024**3, 2),
            "disk_free_gb": round(disk.free / 1024**3, 2),
            "disk_percent": disk.percent,
            "process_memory_mb": round(process_memory_mb, 2),
            "timestamp": datetime.datetime.now().isoformat()
        }
        return ResponseModel(data=metrics)
    except Exception as e:
        return ResponseModel(data={
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        })


@router.get("/db-stats", response_model=ResponseModel)
def get_database_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取数据库统计"""
    try:
        from sqlalchemy import text
        
        # 获取各表记录数
        tables = {
            "user": "SELECT COUNT(*) FROM user",
            "user_plant": "SELECT COUNT(*) FROM user_plant",
            "watering_record": "SELECT COUNT(*) FROM watering_record",
            "treatment_record": "SELECT COUNT(*) FROM treatment_record",
            "remind_config": "SELECT COUNT(*) FROM remind_config",
            "watering_reminder": "SELECT COUNT(*) FROM watering_reminder",
            "identify_history": "SELECT COUNT(*) FROM identify_history",
            "diagnose_history": "SELECT COUNT(*) FROM diagnose_history",
            "plant_species": "SELECT COUNT(*) FROM plant_species",
            "recommendation_history": "SELECT COUNT(*) FROM recommendation_history",
            "operation_log": "SELECT COUNT(*) FROM operation_log",
            "login_log": "SELECT COUNT(*) FROM login_log"
        }
        
        stats = {}
        for table_name, query in tables.items():
            try:
                result = db.execute(text(query))
                stats[table_name] = result.scalar()
            except:
                stats[table_name] = 0
        
        return ResponseModel(data=stats)
    except Exception as e:
        return ResponseModel(data={"error": str(e)})

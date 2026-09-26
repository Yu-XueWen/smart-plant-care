# backend/app/api/v1/endpoints/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_admin
from app.api.models.user import User
from app.api.models.plant import UserPlant
from app.api.models.reminder import RemindConfig
from app.api.models.history import IdentifyHistory, DiagnoseHistory
from app.api.schemas.common import ResponseModel
from app.api.models.operation_log import OperationLog
from app.api.models.login_log import LoginLog
from datetime import datetime, timedelta
from app.api.services.admin_log_service import log_admin_action
from app.api.core.security import get_password_hash, verify_password

router = APIRouter()


@router.get("/users", response_model=ResponseModel)
def get_users(
        keyword: str = Query(None, description="用户名/邮箱/手机号模糊搜索"),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    query = db.query(User)

    if keyword:
        query = query.filter(
            or_(
                User.username.like(f"%{keyword}%"),
                User.email.like(f"%{keyword}%"),
                User.phone.like(f"%{keyword}%")
            )
        )

    total = query.count()
    items = query.order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return ResponseModel(data={
        "total": total,
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "phone": u.phone,
                "role": u.role,
                "status": u.status,
                "created_at": u.created_at.isoformat()
            }
            for u in items
        ]
    })


@router.get("/users/{user_id}/history", response_model=ResponseModel)
def get_user_history(
        user_id: int,
        history_type: str = Query(..., description="identify/diagnose"),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=50),
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    # 验证用户存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if history_type == "identify":
        query = db.query(IdentifyHistory).filter(IdentifyHistory.user_id == user_id)
        total = query.count()
        items = query.order_by(desc(IdentifyHistory.created_at)) \
            .offset((page - 1) * page_size).limit(page_size).all()

        return ResponseModel(data={
            "total": total,
            "items": [
                {"id": h.id, "image_url": h.image_url, "plant_name": h.plant_name,
                 "confidence": float(h.confidence) if h.confidence else None, "created_at": h.created_at.isoformat()}
                for h in items
            ]
        })

    elif history_type == "diagnose":
        query = db.query(DiagnoseHistory).filter(DiagnoseHistory.user_id == user_id)
        total = query.count()
        items = query.order_by(desc(DiagnoseHistory.created_at)) \
            .offset((page - 1) * page_size).limit(page_size).all()

        return ResponseModel(data={
            "total": total,
            "items": [
                {"id": h.id, "image_url": h.image_url, "disease_name": h.disease_name,
                 "confidence": float(h.confidence) if h.confidence else None, "created_at": h.created_at.isoformat()}
                for h in items
            ]
        })

    else:
        raise HTTPException(status_code=400, detail="无效的历史类型")


@router.post("/knowledge/{knowledge_type}/{item_id}", response_model=ResponseModel)
def update_knowledge(
        knowledge_type: str,
        item_id: str,
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """知识库管理（植物/病害的增删改查）"""
    # 实际实现需要与Neo4j交互
    # 这里仅作为框架
    return ResponseModel(message=f"{knowledge_type} {item_id} 更新成功")


@router.post("/models/retrain", response_model=ResponseModel)
def trigger_retrain(
        model_type: str,
        dataset_version: str = "latest",
        admin: User = Depends(get_current_admin)
):
    """触发模型重训练（异步任务）"""
    # 实际实现需要调用Celery任务
    task_id = f"retrain_{model_type}_{dataset_version}"
    return ResponseModel(data={"task_id": task_id})


@router.get("/dashboard/summary", response_model=ResponseModel)
def get_admin_dashboard_summary(
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """获取管理员系统总览数据"""
    today = datetime.now()
    twenty_four_hours_ago = today - timedelta(hours=24)

    # 总用户数（不含管理员自己）
    total_users = db.query(User).filter(User.role != 'admin').count()

    # 总植物数
    total_plants = db.query(UserPlant).filter(UserPlant.status == 1).count()

    # 总提醒数
    total_reminders = db.query(RemindConfig).count()

    # 最近24小时操作日志数
    recent_operation_logs = db.query(OperationLog).filter(
        OperationLog.created_at >= twenty_four_hours_ago
    ).count()

    # 最近24小时登录日志数
    recent_login_logs = db.query(LoginLog).filter(
        LoginLog.login_time >= twenty_four_hours_ago
    ).count()

    # 活跃管理员数（基于登录日志估算）
    active_admins = db.query(LoginLog).filter(
        LoginLog.login_time >= twenty_four_hours_ago,
        LoginLog.success == True
    ).count()

    return ResponseModel(data={
        "total_users": total_users,
        "total_plants": total_plants,
        "total_reminders": total_reminders,
        "recent_operation_logs": recent_operation_logs,
        "recent_login_logs": recent_login_logs,
        "active_admins": active_admins,
        "timestamp": today.isoformat()
    })


@router.get("/today-stats", response_model=ResponseModel)
def get_today_stats(
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """获取今日统计数据"""
    from app.api.models.plant import UserPlant
    from app.api.models.history import IdentifyHistory, DiagnoseHistory
    
    today = datetime.now()
    start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)
    
    new_users_today = db.query(User).filter(
        User.role != 'admin',
        User.created_at >= start_of_day
    ).count()
    
    login_today = db.query(LoginLog).filter(
        LoginLog.login_time >= start_of_day,
        LoginLog.success == True
    ).distinct(LoginLog.username).count()
    
    identify_today = db.query(IdentifyHistory).filter(
        IdentifyHistory.created_at >= start_of_day
    ).count()
    
    diagnose_today = db.query(DiagnoseHistory).filter(
        DiagnoseHistory.created_at >= start_of_day
    ).count()
    
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
    from app.api.models.operation_log import OperationLog
    
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    
    recent_users = db.query(User).filter(
        User.role != 'admin',
        User.created_at >= seven_days_ago
    ).order_by(User.created_at.desc()).limit(limit).all()
    
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


@router.put("/users/{user_id}/status", response_model=ResponseModel)
def toggle_user_status(
        user_id: int,
        status: int = Query(..., description="0禁用 1启用"),
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        request: Request = None
):
    """禁用/启用用户"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    old_status = target_user.status
    target_user.status = status
    
    db.commit()
    db.refresh(target_user)
    
    # 记录操作日志
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="toggle_user_status",
        target_type="user",
        target_id=user_id,
        detail={
            "user_id": user_id,
            "username": target_user.username,
            "old_status": old_status,
            "new_status": status
        },
        ip_address=request.client.host  # 从请求中获取IP
    )
    
    return ResponseModel(data=target_user.to_dict())


@router.delete("/users/{user_id}", response_model=ResponseModel)
def delete_user(
        user_id: int,
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        request: Request = None
):
    """删除用户"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能删除管理员自己或超级管理员
    if target_user.role == 'admin' and admin.id != user_id:
        raise HTTPException(status_code=403, detail="不允许删除其他管理员")
    
    username = target_user.username
    db.delete(target_user)
    db.commit()
    
    # 记录操作日志
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="delete_user",
        target_type="user",
        target_id=user_id,
        detail={"username": username},
        ip_address=request.client.host
    )
    
    return ResponseModel(message=f"用户 {username} 已删除")


@router.post("/users/{user_id}/reset-password", response_model=ResponseModel)
def reset_user_password(
        user_id: int,
        new_password: str = Query(..., description="新密码"),
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        request: Request = None
):
    """重置用户密码"""
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    password_hash = hash_password(new_password)
    target_user.password_hash = password_hash
    
    db.commit()
    db.refresh(target_user)
    
    # 记录操作日志
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="reset_password",
        target_type="user",
        target_id=user_id,
        detail={"user_id": user_id},
        ip_address=request.client.host
    )
    
    return ResponseModel(message="密码重置成功")


@router.get("/users/{user_id}/detail", response_model=ResponseModel)
def get_user_detail(
        user_id: int,
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        request: Request = None
):
    """获取用户详情"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 记录操作日志（只读操作）
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="view_user_detail",
        target_type="user",
        target_id=user_id,
        detail={},
        ip_address=request.client.host
    )
    
    return ResponseModel(data=target_user.to_dict())


@router.get("/users/{user_id}/plants", response_model=ResponseModel)
def get_user_plants(
        user_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        request: Request = None
):
    """获取用户植物列表"""
    from app.api.models.plant import UserPlant
    
    # 验证用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    query = db.query(UserPlant).filter(UserPlant.user_id == user_id, UserPlant.status == 1)
    total = query.count()
    items = query.order_by(desc(UserPlant.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    # 记录操作日志
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="view_user_plants",
        target_type="user",
        target_id=user_id,
        detail={"plant_count": total},
        ip_address=request.client.host
    )
    
    return ResponseModel(data={
        "total": total,
        "items": [p.to_dict() for p in items]
    })


@router.get("/users/{user_id}/records", response_model=ResponseModel)
def get_user_records(
        user_id: int,
        record_type: str = Query(None, description="identify/diagnose/all"),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db),
        request: Request = None
):
    """获取用户操作记录"""
    from app.api.models.history import IdentifyHistory, DiagnoseHistory
    
    # 验证用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if record_type == "identify":
        query = db.query(IdentifyHistory).filter(IdentifyHistory.user_id == user_id)
        total = query.count()
        items = query.order_by(desc(IdentifyHistory.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        return ResponseModel(data={
            "total": total,
            "items": [
                {"id": h.id, "image_url": h.image_url, "plant_name": h.plant_name,
                 "confidence": float(h.confidence) if h.confidence else None, "created_at": h.created_at.isoformat()}
                for h in items
            ]
        })
    
    elif record_type == "diagnose":
        query = db.query(DiagnoseHistory).filter(DiagnoseHistory.user_id == user_id)
        total = query.count()
        items = query.order_by(desc(DiagnoseHistory.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        return ResponseModel(data={
            "total": total,
            "items": [
                {"id": h.id, "image_url": h.image_url, "disease_name": h.disease_name,
                 "confidence": float(h.confidence) if h.confidence else None, "created_at": h.created_at.isoformat()}
                for h in items
            ]
        })
    
    else:
        # 获取所有记录（识别+诊断）
        identify_query = db.query(IdentifyHistory).filter(IdentifyHistory.user_id == user_id)
        diagnose_query = db.query(DiagnoseHistory).filter(DiagnoseHistory.user_id == user_id)
        
        identify_total = identify_query.count()
        diagnose_total = diagnose_query.count()
        
        identify_items = identify_query.order_by(desc(IdentifyHistory.created_at)).limit(page_size).all()
        diagnose_items = diagnose_query.order_by(desc(DiagnoseHistory.created_at)).limit(page_size).all()
        
        all_items = identify_items + diagnose_items
        all_items.sort(key=lambda x: x.created_at, reverse=True)
        
        # 记录操作日志
        log_admin_action(
            db=db,
            admin_id=admin.id,
            username=admin.username,
            action="view_user_records",
            target_type="user",
            target_id=user_id,
            detail={
                "identify_count": identify_total,
                "diagnose_count": diagnose_total,
                "total_records": len(all_items)
            },
            ip_address=request.client.host
        )
        
        return ResponseModel(data={
            "total": len(all_items),
            "items": [
                {"id": item.id, "type": "identify" if hasattr(item, 'plant_name') else "diagnose",
                 "image_url": item.image_url,
                 "plant_name": item.plant_name if hasattr(item, 'plant_name') else None,
                 "disease_name": item.disease_name if hasattr(item, 'disease_name') else None,
                 "confidence": float(item.confidence) if item.confidence else None,
                 "created_at": item.created_at.isoformat()}
                for item in all_items
            ]
        })
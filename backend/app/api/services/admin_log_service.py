from typing import Optional, Dict, Any
from fastapi import Request
from sqlalchemy.orm import Session
from app.api.models.operation_log import OperationLog
from app.api.models.login_log import LoginLog
from app.api.core.database import Base
import ipaddress


def get_client_ip(request: Request) -> str:
    """从请求中获取客户端IP地址"""
    # 如果请求中有 X-Forwarded-For 头（通常用于代理/负载均衡）
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # 取第一个IP（可能是真实客户端IP）
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        # 直接从连接获取
        ip = request.client.host
    
    # 验证IP地址格式
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return "127.0.0.1"  # 默认回环地址


def log_admin_action(
    db: Session,
    admin_id: int,
    username: str,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    detail: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    request: Optional[Request] = None
) -> OperationLog:
    """
    记录管理员操作日志
    
    Args:
        db: 数据库会话
        admin_id: 操作用户ID
        username: 操作用户名
        action: 操作类型（如 ban_user, unban_user, reset_password 等）
        target_type: 操作对象类型（user/plant/reminder/role 等）
        target_id: 操作对象ID
        detail: 操作详情描述（字典）
        ip_address: 客户端IP地址（可选，如果提供了request则自动获取）
        request: FastAPI请求对象（可选，用于自动获取IP）
    
    Returns:
        创建的OperationLog对象
    """
    if ip_address is None and request is not None:
        ip_address = get_client_ip(request)
    
    if detail is None:
        detail = {}
    
    operation_log = OperationLog(
        admin_id=admin_id,
        username=username,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=ip_address
    )
    
    db.add(operation_log)
    db.commit()
    db.refresh(operation_log)
    
    return operation_log


def log_login_action(
    db: Session,
    user_id: Optional[int],
    username: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    logout_time: Optional[Any] = None,
    duration_seconds: Optional[int] = None
) -> LoginLog:
    """
    记录用户登录/登出日志
    
    Args:
        db: 数据库会话
        user_id: 用户ID（如果存在）
        username: 用户名
        ip_address: IP地址
        user_agent: User-Agent字符串
        success: 是否成功
        logout_time: 登出时间（可选）
        duration_seconds: 登录时长（秒，可选）
    
    Returns:
        创建的LoginLog对象
    """
    login_log = LoginLog(
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        logout_time=logout_time,
        duration_seconds=duration_seconds
    )
    
    db.add(login_log)
    db.commit()
    db.refresh(login_log)
    
    return login_log


def get_operation_logs(
    db: Session,
    admin_id: Optional[int] = None,
    username: Optional[str] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    start_date: Optional[Any] = None,
    end_date: Optional[Any] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    查询操作日志列表
    
    Returns:
        {total: int, items: list}
    """
    query = db.query(OperationLog)
    
    if admin_id:
        query = query.filter(OperationLog.admin_id == admin_id)
    if username:
        query = query.filter(OperationLog.username.like(f"%{username}%"))
    if action:
        query = query.filter(OperationLog.action == action)
    if target_type:
        query = query.filter(OperationLog.target_type == target_type)
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)
    
    total = query.count()
    items = query.order_by(OperationLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "items": [log.to_dict() for log in items]
    }


def get_login_logs(
    db: Session,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    start_date: Optional[Any] = None,
    end_date: Optional[Any] = None,
    success: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    查询登录日志列表
    
    Returns:
        {total: int, items: list}
    """
    query = db.query(LoginLog)
    
    if user_id:
        query = query.filter(LoginLog.user_id == user_id)
    if username:
        query = query.filter(LoginLog.username.like(f"%{username}%"))
    if start_date:
        query = query.filter(LoginLog.login_time >= start_date)
    if end_date:
        query = query.filter(LoginLog.login_time <= end_date)
    if success is not None:
        query = query.filter(LoginLog.success == success)
    
    total = query.count()
    items = query.order_by(LoginLog.login_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "items": [log.to_dict() for log in items]
    }
# backend/app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from .security import verify_token
from .config import settings
from .exceptions import UnauthorizedException, ForbiddenException

# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
):
    """
    获取当前登录用户（依赖注入）
    用法:
        @app.get("/profile")
        def get_profile(current_user: User = Depends(get_current_user)):
            ...
    """
    if credentials is None:
        raise UnauthorizedException("未提供认证凭证")

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise UnauthorizedException("无效的认证凭证或已过期")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("无效的认证凭证")

    # 导入模型（避免循环导入）
    from ..models.user import User

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise UnauthorizedException("用户不存在")

    if user.status != 1:
        raise ForbiddenException("账号已被禁用")

    return user


async def get_current_admin(
        current_user=Depends(get_current_user)
):
    """
    获取当前管理员用户（依赖注入）
    用法:
        @app.get("/admin/users")
        def get_users(admin: User = Depends(get_current_admin)):
            ...
    """
    if current_user.role != "admin":
        raise ForbiddenException("需要管理员权限")

    return current_user


async def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
):
    """
    获取当前登录用户（可选，未登录返回 None）
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    from ..models.user import User
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None or user.status != 1:
        return None

    return user
# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from app.api.core.database import get_db
from app.api.core.security import create_access_token, verify_password, get_password_hash
from app.api.core.config import settings
from app.api.models.user import User
from app.api.v1.dependencies.auth import get_current_user
from app.api.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.api.schemas.common import ResponseModel

router = APIRouter()


@router.post("/register", response_model=ResponseModel)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        # 检查用户名是否存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否存在（如果提供了邮箱）
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 检查手机号是否存在（如果提供了手机号）
        if user_data.phone:
            existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
            if existing_phone:
                raise HTTPException(status_code=400, detail="手机号已被注册")

        # 创建新用户
        new_user = User(
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            email=user_data.email,
            phone=user_data.phone,
            role="user",
            status=1
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return ResponseModel(
            code=200,
            message="注册成功",
            data={"user_id": new_user.id, "username": new_user.username}
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败：{str(e)}")


@router.post("/login", response_model=ResponseModel)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        # 查询用户
        user = db.query(User).filter(User.username == user_data.username).first()
        
        # 验证用户是否存在和密码是否正确
        if not user or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 创建访问令牌和刷新令牌
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        refresh_token = create_access_token(
            data={"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=7)
        )

        return ResponseModel(
            code=200,
            message="登录成功",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": settings.access_token_expire_minutes * 60,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "role": user.role
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        # 记录详细错误信息
        import logging
        logger = logging.getLogger("plant_care")
        logger.error(f"登录失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"登录失败：{str(e)}")


@router.post("/refresh", response_model=ResponseModel)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    new_access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return ResponseModel(
        code=200,
        message="刷新成功",
        data={"access_token": new_access_token, "expires_in": settings.access_token_expire_minutes * 60}
    )


@router.get("/me", response_model=ResponseModel)
def get_me(current_user: User = Depends(get_current_user)):
    return ResponseModel(
        code=200,
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "phone": current_user.phone,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat()
        }
    )
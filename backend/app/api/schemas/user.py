# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    status: int
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    refresh_token: str
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str

class UpdateProfileRequest(BaseModel):
    """更新个人信息请求"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    password: Optional[str] = Field(None, min_length=6)

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=6)
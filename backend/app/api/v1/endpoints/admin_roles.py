"""
管理员角色管理端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import datetime

from app.api.core.database import get_db
from app.api.models.user import User
from app.api.models.operation_log import OperationLog
from app.api.v1.dependencies.auth import get_current_admin
from app.utils.response_utils import ResponseModel

router = APIRouter()

# 预定义权限列表
PERMISSIONS = {
    "user:view": "查看用户",
    "user:ban": "禁用/启用用户",
    "user:delete": "删除用户",
    "user:reset_password": "重置用户密码",
    "plant:view": "查看植物",
    "plant:delete": "删除植物",
    "log:view": "查看日志",
    "log:export": "导出日志",
    "system:view": "查看系统状态",
    "system:manage": "管理系统配置",
    "role:view": "查看角色",
    "role:create": "创建角色",
    "role:edit": "编辑角色",
    "role:delete": "删除角色",
    "knowledge:view": "查看知识库",
    "knowledge:edit": "编辑知识库",
    "model:retrain": "重新训练模型",
}


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    permissions: List[str]
    user_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class UserUpdateRole(BaseModel):
    role_id: int


# 模拟角色存储（实际项目中应使用数据库）
# 由于没有Role模型，我们使用内存存储
_roles = {
    1: RoleResponse(
        id=1,
        name="超级管理员",
        description="拥有所有权限",
        permissions=list(PERMISSIONS.keys()),
        user_count=0,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    ),
    2: RoleResponse(
        id=2,
        name="普通管理员",
        description="拥有大部分管理权限",
        permissions=[
            "user:view", "user:ban", "user:reset_password",
            "plant:view", "log:view", "system:view",
            "role:view", "knowledge:view", "model:retrain",
        ],
        user_count=0,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    ),
    3: RoleResponse(
        id=3,
        name="内容管理员",
        description="可以管理内容和知识库",
        permissions=[
            "user:view", "plant:view", "plant:delete",
            "log:view", "knowledge:view", "knowledge:edit",
        ],
        user_count=0,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    ),
}

_next_id = 4


@router.get("/permissions", response_model=ResponseModel)
def get_permissions(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有可用权限列表"""
    return ResponseModel(data={
        "permissions": PERMISSIONS,
        "total": len(PERMISSIONS)
    })


@router.get("", response_model=ResponseModel)
def get_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    # 统计每个角色的用户数
    for role in _roles.values():
        role.user_count = db.query(User).filter(User.role == role.name).count()
    
    items = list(_roles.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated_items
    })


@router.get("/{role_id}", response_model=ResponseModel)
def get_role(
    role_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取单个角色详情"""
    role = _roles.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 更新用户数
    role.user_count = db.query(User).filter(User.role == role.name).count()
    
    return ResponseModel(data=role)


@router.post("", response_model=ResponseModel)
def create_role(
    role_data: RoleCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建新角色"""
    # 检查权限（仅当用户拥有细粒度 permissions 属性时才校验，管理员默认放行）
    if hasattr(admin, 'permissions') and "role:create" not in admin.permissions:
        raise HTTPException(status_code=403, detail="无权创建角色")
    
    global _next_id
    new_role = RoleResponse(
        id=_next_id,
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions,
        user_count=0,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    _roles[_next_id] = new_role
    _next_id += 1
    
    # 记录操作日志
    from app.api.services.admin_log_service import log_admin_action
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="create_role",
        target_type="role",
        target_id=new_role.id,
        detail={"name": new_role.name, "permissions": new_role.permissions}
    )
    
    return ResponseModel(data=new_role, message="角色创建成功")


@router.put("/{role_id}", response_model=ResponseModel)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新角色"""
    role = _roles.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 检查权限（仅当用户拥有细粒度 permissions 属性时才校验，管理员默认放行）
    if hasattr(admin, 'permissions') and "role:edit" not in admin.permissions:
        raise HTTPException(status_code=403, detail="无权编辑角色")
    
    if role_data.name:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.permissions is not None:
        role.permissions = role_data.permissions
    role.updated_at = datetime.datetime.now()
    
    # 记录操作日志
    from app.api.services.admin_log_service import log_admin_action
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="update_role",
        target_type="role",
        target_id=role_id,
        detail={"name": role.name, "permissions": role.permissions}
    )
    
    return ResponseModel(data=role, message="角色更新成功")


@router.delete("/{role_id}", response_model=ResponseModel)
def delete_role(
    role_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除角色"""
    role = _roles.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 检查权限（仅当用户拥有细粒度 permissions 属性时才校验，管理员默认放行）
    if hasattr(admin, 'permissions') and "role:delete" not in admin.permissions:
        raise HTTPException(status_code=403, detail="无权删除角色")
    
    # 检查是否有用户使用该角色
    user_count = db.query(User).filter(User.role == role.name).count()
    if user_count > 0:
        raise HTTPException(status_code=400, detail=f"该角色下有 {user_count} 个用户，无法删除")
    
    del _roles[role_id]
    
    # 记录操作日志
    from app.api.services.admin_log_service import log_admin_action
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="delete_role",
        target_type="role",
        target_id=role_id,
        detail={"name": role.name}
    )
    
    return ResponseModel(message="角色删除成功")


@router.put("/users/{user_id}/role", response_model=ResponseModel)
def update_user_role(
    user_id: int,
    role_data: UserUpdateRole,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新用户角色"""
    # 检查权限（仅当用户拥有细粒度 permissions 属性时才校验，管理员默认放行）
    if hasattr(admin, 'permissions') and "role:assign" not in admin.permissions:
        raise HTTPException(status_code=403, detail="无权分配角色")
    
    # 验证用户存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证角色存在
    role = _roles.get(role_data.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 更新用户角色
    old_role = user.role
    user.role = role.name  # 简化处理，实际应使用role_id
    db.commit()
    
    # 记录操作日志
    from app.api.services.admin_log_service import log_admin_action
    log_admin_action(
        db=db,
        admin_id=admin.id,
        username=admin.username,
        action="assign_role",
        target_type="user",
        target_id=user_id,
        detail={"old_role": old_role, "new_role": role.name}
    )
    
    return ResponseModel(message="用户角色更新成功")

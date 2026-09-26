from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from sqlalchemy.sql import func
from app.api.core.database import Base


class OperationLog(Base):
    """管理员操作日志"""
    __tablename__ = "operation_log"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, nullable=False)  # 操作用户ID
    username = Column(String(50), nullable=False)  # 操作用户名
    action = Column(Enum('ban_user', 'unban_user', 'reset_password', 'delete_user',
                         'create_role', 'update_role', 'delete_role',
                         'assign_role', 'view_dashboard', 'view_logs',
                         'view_system', 'retrain_model',
                         'create_plant', 'update_plant', 'delete_plant',
                         'create_reminder', 'update_reminder', 'delete_reminder'),
                    nullable=False)  # 操作类型
    target_type = Column(String(50))  # 操作对象类型（user/plant/reminder/role等）
    target_id = Column(Integer)  # 操作对象ID
    detail = Column(JSON)  # 操作详情描述
    ip_address = Column(String(45))  # 客户端IP地址（IPv6支持）
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'username': self.username,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'detail': self.detail,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.api.core.database import Base


class LoginLog(Base):
    """用户登录日志"""
    __tablename__ = "login_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # 用户ID
    username = Column(String(50), nullable=False)  # 用户名
    ip_address = Column(String(45))  # 客户端IP地址（IPv6支持）
    user_agent = Column(Text)  # User-Agent字符串
    login_time = Column(DateTime, server_default=func.now())  # 登录时间
    success = Column(Boolean, nullable=False)  # 是否成功
    logout_time = Column(DateTime, nullable=True)  # 登出时间
    duration_seconds = Column(Integer, nullable=True)  # 登录时长（秒）

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'duration_seconds': self.duration_seconds,
            'success': self.success
        }
# backend/app/services/base_service.py
import logging
from typing import Optional, TypeVar, Generic, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseService:
    """基础服务类，提供通用数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def safe_execute(self, func, error_msg: str = "操作失败") -> Any:
        """安全执行数据库操作"""
        try:
            result = func()
            self.db.commit()
            return result
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"{error_msg}: {str(e)}")
            raise e

    def paginate(self, query, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """分页查询"""
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }


class CacheService:
    """缓存服务基类"""

    def __init__(self, redis_client=None):
        self.redis = redis_client

    def get_cache_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"

    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        if self.redis:
            return await self.redis.get(key)
        return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """设置缓存"""
        if self.redis:
            return await self.redis.setex(key, ttl, value)
        return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if self.redis:
            return await self.redis.delete(key)
        return False
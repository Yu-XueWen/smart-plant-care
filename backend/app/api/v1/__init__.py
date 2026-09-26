# backend/app/api/v1/__init__.py
from fastapi import APIRouter
from .endpoints.auth import router as auth_router
from .endpoints.plants import router as plants_router
from .endpoints.ai import router as ai_router
from .endpoints.reminders import router as reminders_router
from .endpoints.history import router as history_router
from .endpoints.dashboard import router as dashboard_router
from .endpoints.admin import router as admin_router
from .endpoints.recommend import router as recommend_router
from .endpoints.watering_reminder import router as watering_reminder_router
from .endpoints.care_reminder import router as care_reminder_router
from .endpoints.admin_dashboard import router as admin_dashboard_router
from .endpoints.admin_logs import router as admin_logs_router
from .endpoints.admin_system import router as admin_system_router
from .endpoints.admin_roles import router as admin_roles_router
from .endpoints.admin_knowledge import router as admin_knowledge_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(plants_router, prefix="/plants", tags=["植物档案"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI识别"])
api_router.include_router(reminders_router, prefix="/reminders", tags=["提醒管理"])
api_router.include_router(watering_reminder_router, prefix="/watering-reminders", tags=["浇水提醒"])
api_router.include_router(care_reminder_router, prefix="/care-reminders", tags=["养护提醒"])
api_router.include_router(history_router, prefix="/history", tags=["历史记录"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["首页看板"])
api_router.include_router(admin_router, prefix="/admin", tags=["管理员"])
api_router.include_router(admin_dashboard_router, prefix="/admin/dashboard", tags=["管理员看板"])
api_router.include_router(admin_logs_router, prefix="/admin/logs", tags=["管理员日志"])
api_router.include_router(admin_system_router, prefix="/admin/system", tags=["管理员系统"])
api_router.include_router(admin_roles_router, prefix="/admin/roles", tags=["管理员角色"])
api_router.include_router(admin_knowledge_router, prefix="/admin/knowledge", tags=["管理员知识库"])
api_router.include_router(recommend_router, tags=["植物推荐"])
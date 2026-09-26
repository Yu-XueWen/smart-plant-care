# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.api.core.config import settings
from app.api.core.database import init_db
from app.api.core.exceptions import BusinessException
from app.api.v1 import api_router
from app.utils.logger import setup_logger

# 设置日志
logger = setup_logger("plant_care", "DEBUG" if settings.debug else "INFO", "app.log")

# 启动时初始化数据库
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("正在初始化数据库...")
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    # 启动提醒定时任务调度器
    logger.info("正在启动提醒定时任务调度器...")
    try:
        from app.api.services.scheduler import init_scheduler
        init_scheduler()
        logger.info("提醒定时任务调度器启动成功")
    except Exception as e:
        logger.error(f"提醒定时任务调度器启动失败: {e}")
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭")
    try:
        from app.api.services.scheduler import shutdown_scheduler
        shutdown_scheduler()
        logger.info("提醒定时任务调度器已关闭")
    except Exception as e:
        logger.error(f"关闭提醒定时任务调度器失败: {e}")

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="智能植物养护系统 API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# 注册路由
app.include_router(api_router, prefix="/api/v1")

# 全局异常处理
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.warning(f"业务异常: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"系统异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误"}
    )

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}

# 根路径
@app.get("/")
def root():
    return {
        "message": f"欢迎使用 {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else None
    }

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
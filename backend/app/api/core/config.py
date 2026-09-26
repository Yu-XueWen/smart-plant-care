# backend/app/core/config.py
import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# backend 目录（基于此文件位置计算，确保无论从哪里运行都正确）
BACKEND_DIR = Path(__file__).parent.parent.parent.parent

# 加载 .env 文件
env_file = BACKEND_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)


class Settings:
    """应用配置类"""

    def __init__(self):
        # 应用基础配置
        self.app_name: str = os.getenv("APP_NAME", "智能植物养护系统")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"

        # 服务器配置
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))

        # CORS 配置
        self.cors_origins: List[str] = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000"
        ).split(",")

        # 数据库配置（必须通过环境变量设置）
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL 环境变量未设置")
        
        self.database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        self.database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
        self.database_pool_recycle: int = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

        # Redis 配置
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))

        # JWT 配置（必须通过环境变量设置）
        self.secret_key: str = os.getenv("SECRET_KEY")
        if not self.secret_key:
            raise ValueError("SECRET_KEY 环境变量未设置，请生成随机密钥并设置")
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "7200")
        )
        self.refresh_token_expire_days: int = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )

        # 密码加密配置
        self.bcrypt_rounds: int = int(os.getenv("BCRYPT_ROUNDS", "12"))

        # 文件上传配置 - 使用基于 backend 目录的绝对路径
        upload_dir_from_env = os.getenv("UPLOAD_DIR", "./uploads")
        # 如果是相对路径，转换为基于 backend 目录的绝对路径
        if os.path.isabs(upload_dir_from_env):
            self.upload_dir: str = upload_dir_from_env
        else:
            # 使用 Path 连接，正确处理 ../ 和 ./ 前缀
            self.upload_dir: str = str((BACKEND_DIR / upload_dir_from_env).resolve())
        self.max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
        self.allowed_image_extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

        # AI 模型配置 - 使用基于 backend 目录的绝对路径
        ai_models_dir_from_env = os.getenv("AI_MODELS_DIR", "../ai_models/models")
        if os.path.isabs(ai_models_dir_from_env):
            self.ai_models_dir: str = ai_models_dir_from_env
        else:
            # 使用 Path 连接，正确处理 ../ 和 ./ 前缀
            self.ai_models_dir: str = str((BACKEND_DIR / ai_models_dir_from_env).resolve())
        self.plant_detect_model: str = os.getenv("PLANT_DETECT_MODEL", "")
        # 处理模型相对路径
        classify_model = os.getenv("PLANT_CLASSIFY_MODEL", "")
        if classify_model and not os.path.isabs(classify_model):
            self.plant_classify_model: str = str((BACKEND_DIR / classify_model).resolve())
        else:
            self.plant_classify_model: str = classify_model
        
        disease_model = os.getenv("DISEASE_MODEL", "")
        if disease_model and not os.path.isabs(disease_model):
            self.disease_model: str = str((BACKEND_DIR / disease_model).resolve())
        else:
            self.disease_model: str = disease_model

        # Neo4j 知识图谱配置
        self.neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
        self.neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")

        # 创建上传目录
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    def get_database_url(self) -> str:
        """获取数据库URL"""
        return self.database_url

    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.debug

    def is_production(self) -> bool:
        """是否为生产环境"""
        return not self.debug


# 单例实例
settings = Settings()
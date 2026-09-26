# backend/test_core.py
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.api.core.config import settings
from app.api.core.security import get_password_hash, verify_password, create_access_token
from app.api.core.database import engine, Base


def test_config():
    """测试配置"""
    print(f"应用名称: {settings.app_name}")
    print(f"调试模式: {settings.debug}")
    print(f"数据库URL: {settings.database_url}")
    print(f"上传目录: {settings.upload_dir}")
    print("配置加载成功 ✓")


def test_security():
    """测试安全模块"""
    password = "test123456"
    hashed = get_password_hash(password)
    print(f"原始密码: {password}")
    print(f"哈希密码: {hashed}")
    print(f"密码验证: {verify_password(password, hashed)}")

    token = create_access_token({"sub": "1", "role": "user"})
    print(f"生成的Token: {token[:50]}...")
    print("安全模块测试成功 ✓")


def test_database():
    """测试数据库连接"""
    try:
        connection = engine.connect()
        print("数据库连接成功 ✓")
        connection.close()
    except Exception as e:
        print(f"数据库连接失败: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("测试 Core 层")
    print("=" * 50)

    test_config()
    print()
    test_security()
    print()
    test_database()
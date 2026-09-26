"""
创建浇水提醒相关数据表
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.api.core.database import engine, Base
from app.api.models.reminder import WateringReminder

def create_tables():
    """创建浇水提醒表"""
    print("正在创建浇水提醒表...")
    
    # 只创建 WateringReminder 表
    WateringReminder.__table__.create(engine, checkfirst=True)
    
    print("✓ 浇水提醒表创建成功!")
    print(f"  表名: {WateringReminder.__tablename__}")

if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

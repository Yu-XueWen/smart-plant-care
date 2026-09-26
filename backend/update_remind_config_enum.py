"""
更新 remind_config 表的 frequency_type 字段，添加 'seasonal' 选项
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.api.core.database import engine
import pymysql
from app.api.core.config import settings

def update_frequency_type_enum():
    """更新 frequency_type 的 ENUM 值"""
    print("正在更新 remind_config 表的 frequency_type 字段...")
    
    # 解析数据库URL
    db_url = settings.database_url
    # 格式: mysql+pymysql://user:pass@host:port/dbname
    from urllib.parse import urlparse
    parsed = urlparse(db_url.replace('mysql+pymysql://', 'mysql://'))
    
    conn = pymysql.connect(
        host=parsed.hostname or 'localhost',
        port=parsed.port or 3306,
        user=parsed.username or 'root',
        password=parsed.password or '',
        database=parsed.path.lstrip('/') or 'plant',
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor() as cursor:
            # 修改 ENUM 类型，添加 'seasonal'
            sql = """
            ALTER TABLE remind_config 
            MODIFY COLUMN frequency_type ENUM('daily', 'weekly', 'monthly', 'interval', 'one_time', 'seasonal') NOT NULL
            """
            cursor.execute(sql)
            conn.commit()
            print("✓ frequency_type 字段更新成功!")
            print("  新值: daily, weekly, monthly, interval, one_time, seasonal")
    except Exception as e:
        conn.rollback()
        print(f"✗ 更新失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        update_frequency_type_enum()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

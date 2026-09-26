"""删除旧的 admin 账户"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

import pymysql

DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'plant',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**DATABASE_CONFIG)
cur = conn.cursor()

# 删除 admin 账户
cur.execute("DELETE FROM user WHERE username = %s", ('admin',))
conn.commit()
print(f"已删除 admin 账户 (影响 {cur.rowcount} 行)")

conn.close()

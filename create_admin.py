"""创建管理员账户 - 使用 bcrypt 哈希"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

import pymysql
from app.api.core.security import get_password_hash

DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'plant',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**DATABASE_CONFIG)
cur = conn.cursor()

# 检查是否已存在
cur.execute("SELECT id FROM user WHERE username = %s", ('admin',))
if cur.fetchone():
    print("✗ 用户名 'admin' 已存在")
    conn.close()
    sys.exit(1)

# 使用 bcrypt 哈希密码
hashed_pw = get_password_hash('admin123')

# 插入新用户
sql = """
    INSERT INTO user (username, password_hash, email, role, status, created_at, updated_at)
    VALUES (%s, %s, %s, 'admin', 1, NOW(), NOW())
"""
cur.execute(sql, ('admin', hashed_pw, ''))
conn.commit()
print(f"✓ 管理员账户创建成功: admin")
print(f"  密码: admin123")

conn.close()

"""
管理员账户创建/升级脚本 - 简化版
用于在终端中创建管理员账户或升级现有用户为管理员
用法:
    python setup_admin.py create <username> <password> [email]
    python setup_admin.py upgrade <username>
    python setup_admin.py list
"""
import sys
from pathlib import Path

# 添加 backend 目录到路径
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.api.services.security import hash_password

# 数据库配置
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/plant?charset=utf8mb4"

def connect_db():
    """连接数据库"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            db_version = result.fetchone()[0]
            print(f"✓ 数据库连接成功 (MySQL {db_version})")
        return engine
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return None

def create_admin_user(engine, username: str, password: str, email: str = None):
    """创建新的管理员账户"""
    try:
        with engine.connect() as conn:
            # 检查用户名是否已存在
            result = conn.execute(text("SELECT id FROM user WHERE username = :username"), {"username": username})
            if result.fetchone():
                print(f"✗ 用户名 '{username}' 已存在")
                return False
            
            # 哈希密码
            hashed_pw = hash_password(password)
            
            # 插入新用户
            insert_sql = """
                INSERT INTO user (username, password_hash, email, role, status, created_at, updated_at)
                VALUES (:username, :password_hash, :email, 'admin', 1, NOW(), NOW())
            """
            conn.execute(text(insert_sql), {
                "username": username,
                "password_hash": hashed_pw,
                "email": email or ""
            })
            conn.commit()
            print(f"✓ 管理员账户创建成功: {username}")
            return True
    except Exception as e:
        print(f"✗ 创建管理员账户失败: {e}")
        return False

def upgrade_user_to_admin(engine, username: str):
    """将现有用户升级为管理员"""
    try:
        with engine.connect() as conn:
            # 检查用户是否存在
            result = conn.execute(text("SELECT id, role FROM user WHERE username = :username"), {"username": username})
            user = result.fetchone()
            
            if not user:
                print(f"✗ 用户 '{username}' 不存在")
                return False
            
            if user[1] == 'admin':
                print(f"ℹ 用户 '{username}' 已经是管理员")
                return True
            
            # 更新角色为 admin
            update_sql = "UPDATE user SET role = 'admin', updated_at = NOW() WHERE username = :username"
            conn.execute(text(update_sql), {"username": username})
            conn.commit()
            print(f"✓ 用户 '{username}' 已升级为管理员")
            return True
    except Exception as e:
        print(f"✗ 升级用户失败: {e}")
        return False

def list_users(engine):
    """列出所有用户"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, username, email, role, status, created_at FROM user ORDER BY id"))
            users = result.fetchall()
            
            if not users:
                print("ℹ 数据库中没有用户")
                return
            
            print("\n当前用户列表:")
            print("-" * 80)
            print(f"{'ID':<5} {'用户名':<20} {'邮箱':<30} {'角色':<8} {'状态':<6} {'创建时间'}")
            print("-" * 80)
            
            for u in users:
                status_str = "启用" if u[4] == 1 else "禁用"
                print(f"{u[0]:<5} {u[1]:<20} {u[2] or '-':<30} {u[3]:<8} {status_str:<6} {u[5]}")
            print("-" * 80)
            print(f"共 {len(users)} 个用户")
    except Exception as e:
        print(f"✗ 查询用户失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python setup_admin.py create <username> <password> [email]  - 创建管理员账户")
        print("  python setup_admin.py upgrade <username>                    - 升级用户为管理员")
        print("  python setup_admin.py list                                  - 列出所有用户")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # 连接数据库
    engine = connect_db()
    if not engine:
        sys.exit(1)
    
    if command == "create":
        if len(sys.argv) < 4:
            print("✗ 用法: python setup_admin.py create <username> <password> [email]")
            sys.exit(1)
        username = sys.argv[2]
        password = sys.argv[3]
        email = sys.argv[4] if len(sys.argv) > 4 else None
        create_admin_user(engine, username, password, email)
    
    elif command == "upgrade":
        if len(sys.argv) < 3:
            print("✗ 用法: python setup_admin.py upgrade <username>")
            sys.exit(1)
        username = sys.argv[2]
        upgrade_user_to_admin(engine, username)
    
    elif command == "list":
        list_users(engine)
    
    else:
        print(f"✗ 未知命令: {command}")
        print("可用命令: create, upgrade, list")
        sys.exit(1)

if __name__ == "__main__":
    main()

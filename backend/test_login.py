#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试管理员登录"""

from app.api.core.database import SessionLocal
from app.api.models.user import User
from app.api.core.security import verify_password, get_password_hash

db = SessionLocal()

# 测试 Yxw 账号
print("=" * 50)
print("测试 Yxw 账号")
print("=" * 50)
user = db.query(User).filter(User.username == 'Yxw').first()
if user:
    print(f"用户名: {user.username}")
    print(f"角色: {user.role}")
    print(f"状态: {user.status}")
    print(f"密码哈希: {user.password_hash}")
    
    # 测试常见密码
    passwords = ['admin123', 'Yxw123', '123456', 'password', 'admin']
    for pwd in passwords:
        result = verify_password(pwd, user.password_hash)
        print(f"  密码 '{pwd}': {'✓ 正确' if result else '✗ 错误'}")
else:
    print("用户不存在")

# 测试 admin 账号
print("\n" + "=" * 50)
print("测试 admin 账号")
print("=" * 50)
user = db.query(User).filter(User.username == 'admin').first()
if user:
    print(f"用户名: {user.username}")
    print(f"角色: {user.role}")
    print(f"状态: {user.status}")
    print(f"密码哈希: {user.password_hash}")
    
    # 测试常见密码
    passwords = ['admin123', 'admin', '123456', 'password']
    for pwd in passwords:
        result = verify_password(pwd, user.password_hash)
        print(f"  密码 '{pwd}': {'✓ 正确' if result else '✗ 错误'}")
else:
    print("用户不存在")

db.close()

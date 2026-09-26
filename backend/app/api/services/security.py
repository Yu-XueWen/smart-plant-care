import hashlib
import secrets

def hash_password(password: str) -> str:
    """
    对密码进行哈希处理。
    注意：在生产环境中应使用 bcrypt 或 argon2 等更安全的算法。
    这里使用 SHA256 + salt 作为示例。
    """
    # 生成随机盐
    salt = secrets.token_hex(16)
    # 组合密码和盐并哈希
    password_salt = password + salt
    hashed = hashlib.sha256(password_salt.encode('utf-8')).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, hashed: str) -> bool:
    """
    验证密码是否匹配哈希值。
    """
    if ':' not in hashed:
        return False
    salt, stored_hash = hashed.split(':', 1)
    password_salt = password + salt
    new_hash = hashlib.sha256(password_salt.encode('utf-8')).hexdigest()
    return new_hash == stored_hash

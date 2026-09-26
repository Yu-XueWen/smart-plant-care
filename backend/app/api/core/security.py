# backend/app/core/security.py
import bcrypt as bcrypt_lib
from jose import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .config import settings

# 密码加密配置
BCRYPT_ROUNDS = settings.bcrypt_rounds


def get_password_hash(password: str) -> str:
    """
    对密码进行哈希加密
    Args:
        password: 明文密码
    Returns:
        哈希后的密码
    """
    # bcrypt限制密码长度不能超过72字节，需要先截断
    password_bytes = password.encode('utf-8')[:72]
    
    # 生成盐值并哈希
    salt = bcrypt_lib.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt_lib.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
    Returns:
        是否正确
    """
    # bcrypt限制密码长度不能超过72字节，需要先截断
    password_bytes = plain_password.encode('utf-8')[:72]
    
    try:
        # 验证密码
        return bcrypt_lib.checkpw(
            password_bytes,
            hashed_password.encode('utf-8')
        )
    except ValueError as ve:
        # 处理bcrypt的已知bug：某些情况下即使密码<=72字节也会报错
        from app.utils.logger import setup_logger
        logger = setup_logger("security")
        logger.warning(f"bcrypt验证异常: {ve}，尝试重新编码后验证")
        try:
            # 尝试使用更严格的方式验证
            if isinstance(hashed_password, str):
                hashed_bytes = hashed_password.encode('utf-8')
            else:
                hashed_bytes = hashed_password
            return bcrypt_lib.checkpw(password_bytes, hashed_bytes)
        except Exception as e2:
            logger.error(f"密码验证失败(二次尝试): {e2}")
            return False
    except Exception as e:
        # 如果验证过程出现异常，返回False
        from app.utils.logger import setup_logger
        logger = setup_logger("security")
        logger.error(f"密码验证失败: {e}")
        return False


def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌
    Args:
        data: 要编码的数据
        expires_delta: 过期时间
    Returns:
        JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    创建刷新令牌
    Args:
        data: 要编码的数据
    Returns:
        刷新令牌
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码访问令牌
    Args:
        token: JWT token
    Returns:
        解码后的数据，解码失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # token 过期
    except jwt.InvalidTokenError:
        return None  # token 无效


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    验证 token 的有效性
    Args:
        token: JWT token
        token_type: token 类型 (access/refresh)
    Returns:
        解码后的数据，验证失败返回 None
    """
    payload = decode_access_token(token)

    if payload is None:
        return None

    # 验证 token 类型
    if token_type == "refresh" and payload.get("type") != "refresh":
        return None

    return payload
# backend/app/utils/image_utils.py
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException


def _detect_image_type(data: bytes) -> Optional[str]:
    """通过文件头魔术字节检测图片类型（替代已移除的 imghdr）"""
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if data[:2] == b'\xff\xd8':
        return 'jpeg'
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    if data[:2] == b'BM':
        return 'bmp'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'webp'
    return None

from app.api.core.config import settings

ALLOWED_EXTENSIONS = settings.allowed_image_extensions
MAX_FILE_SIZE = settings.max_upload_size


def validate_image(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    验证图片文件
    Args:
        file: 上传的文件
    Returns:
        (是否有效, 错误信息)
    """
    # 检查文件名
    filename = file.filename
    if not filename:
        return False, "文件名为空"

    # 检查扩展名
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"不支持的文件类型，仅支持 {', '.join(ALLOWED_EXTENSIONS)}"

    # 检查文件大小
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        return False, f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)"

    return True, None


def save_upload_file(file: UploadFile, subdir: str = "") -> str:
    """
    保存上传的文件
    Args:
        file: 上传的文件
        subdir: 子目录
    Returns:
        保存后的文件路径
    """
    # 验证文件
    is_valid, error = validate_image(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # 生成唯一文件名
    ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # 创建目标目录
    upload_dir = Path(settings.upload_dir)
    if subdir:
        upload_dir = upload_dir / subdir
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 保存文件
    file_path = upload_dir / unique_filename
    content = file.file.read()

    # 验证图片格式
    image_type = _detect_image_type(content)
    if image_type not in ['jpeg', 'png', 'gif', 'bmp', 'webp']:
        raise HTTPException(status_code=400, detail="无效的图片格式")

    with open(file_path, "wb") as f:
        f.write(content)

    # 返回访问 URL
    if subdir:
        return f"/uploads/{subdir}/{unique_filename}"
    return f"/uploads/{unique_filename}"


def delete_file(file_url: str) -> bool:
    """
    删除文件
    Args:
        file_url: 文件 URL
    Returns:
        是否删除成功
    """
    if not file_url.startswith("/uploads/"):
        return False

    relative_path = file_url.replace("/uploads/", "")
    file_path = Path(settings.upload_dir) / relative_path

    if file_path.exists():
        file_path.unlink()
        return True
    return False


def get_file_url(filename: str, subdir: str = "") -> str:
    """获取文件访问 URL"""
    if subdir:
        return f"/uploads/{subdir}/{filename}"
    return f"/uploads/{filename}"
# backend/app/utils/response_utils.py
from typing import Any, Optional, List, Dict
from app.api.schemas.common import ResponseModel

def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200
) -> ResponseModel:
    """成功响应"""
    return ResponseModel(code=code, message=message, data=data)

def error_response(
    message: str = "error",
    code: int = 400,
    detail: Any = None
) -> dict:
    """错误响应"""
    return {"code": code, "message": message, "detail": detail}

def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """分页响应"""
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }
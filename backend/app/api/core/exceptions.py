# backend/app/core/exceptions.py
from fastapi import HTTPException, status


class BusinessException(HTTPException):
    """业务异常基类"""

    def __init__(self, detail: str = "业务处理失败", code: int = 400):
        super().__init__(status_code=code, detail=detail)


class NotFoundException(BusinessException):
    """资源不存在异常"""

    def __init__(self, detail: str = "资源不存在"):
        super().__init__(detail=detail, code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(BusinessException):
    """未授权异常"""

    def __init__(self, detail: str = "未授权访问"):
        super().__init__(detail=detail, code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(BusinessException):
    """禁止访问异常"""

    def __init__(self, detail: str = "权限不足"):
        super().__init__(detail=detail, code=status.HTTP_403_FORBIDDEN)


class ValidationException(BusinessException):
    """参数验证异常"""

    def __init__(self, detail: str = "参数验证失败"):
        super().__init__(detail=detail, code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class DatabaseException(BusinessException):
    """数据库异常"""

    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(detail=detail, code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIServiceException(BusinessException):
    """AI服务异常"""

    def __init__(self, detail: str = "AI服务调用失败"):
        super().__init__(detail=detail, code=status.HTTP_503_SERVICE_UNAVAILABLE)


class FileUploadException(BusinessException):
    """文件上传异常"""

    def __init__(self, detail: str = "文件上传失败"):
        super().__init__(detail=detail, code=status.HTTP_400_BAD_REQUEST)
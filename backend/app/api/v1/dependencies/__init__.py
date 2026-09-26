# backend/app/api/v1/dependencies/__init__.py

from .auth import get_current_user, get_current_admin

__all__ = ["get_current_user", "get_current_admin"]

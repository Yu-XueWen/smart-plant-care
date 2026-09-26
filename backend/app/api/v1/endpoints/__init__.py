# backend/app/api/v1/endpoints/__init__.py
from . import auth, plants, ai, reminders, history, dashboard, admin, recommend, watering_reminder, care_reminder, admin_dashboard

__all__ = ["auth", "plants", "ai", "reminders", "history", "dashboard", "admin", "recommend", "watering_reminder", "care_reminder", "admin_dashboard"]
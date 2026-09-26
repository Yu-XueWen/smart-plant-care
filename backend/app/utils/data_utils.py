# backend/app/utils/date_utils.py
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

def format_date(d: Optional[date], fmt: str = "%Y-%m-%d") -> Optional[str]:
    """格式化日期"""
    if d is None:
        return None
    return d.strftime(fmt)

def parse_date(date_str: str, fmt: str = "%Y-%m-%d") -> Optional[date]:
    """解析日期字符串"""
    try:
        return datetime.strptime(date_str, fmt).date()
    except (ValueError, TypeError):
        return None

def get_date_range(days: int) -> Tuple[date, date]:
    """获取日期范围（今天往前推 days 天）"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def days_between(start_date: date, end_date: date) -> int:
    """计算两个日期之间的天数"""
    return (end_date - start_date).days

def is_today(target_date: date) -> bool:
    """判断是否是今天"""
    return target_date == date.today()

def is_past(target_date: date) -> bool:
    """判断是否已过期"""
    return target_date < date.today()

def get_week_start(date_obj: Optional[date] = None) -> date:
    """获取本周开始日期（周一）"""
    if date_obj is None:
        date_obj = date.today()
    start = date_obj - timedelta(days=date_obj.weekday())
    return start

def get_month_start(date_obj: Optional[date] = None) -> date:
    """获取本月开始日期"""
    if date_obj is None:
        date_obj = date.today()
    return date(date_obj.year, date_obj.month, 1)
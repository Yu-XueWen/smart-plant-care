import re

file_path = r"d:\Improve\smart-plant-care\backend\app\api\v1\endpoints\admin.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 删除 /today-stats 端点
today_stats_pattern = r'@router\.get\("/today-stats", response_model=ResponseModel\)[\s\S]*?^def get_today_stats[\s\S]*?^\n'
content = re.sub(today_stats_pattern, '', content, flags=re.MULTILINE)

# 删除 /recent-activity 端点
recent_activity_pattern = r'@router\.get\("/recent-activity", response_model=ResponseModel\)[\s\S]*?^def get_recent_activity[\s\S]*?^\n'
content = re.sub(recent_activity_pattern, '', content, flags=re.MULTILINE)

# 清理多余的空行
content = re.sub(r'\n\n+', '\n', content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {file_path}")
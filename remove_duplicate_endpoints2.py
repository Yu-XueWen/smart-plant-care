import re
import sys

file_path = r"d:\Improve\smart-plant-care\backend\app\api\v1\endpoints\admin.py"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 统计出现次数
    today_stats_count = content.count('/today-stats')
    recent_activity_count = content.count('/recent-activity')
    print(f"today-stats 出现次数: {today_stats_count}")
    print(f"recent-activity 出现次数: {recent_activity_count}")

    # 删除 /today-stats 端点（使用更宽松的模式）
    pattern_today = r'(@router\.get\("/today-stats"[^)]*\))[\s\S]*?(?=@router\.get|\Z)'
    new_content, count_today = re.subn(pattern_today, '', content, flags=re.MULTILINE)
    print(f"删除了 {count_today} 个 today-stats 端点")

    # 删除 /recent-activity 端点
    pattern_recent = r'(@router\.get\("/recent-activity"[^)]*\))[\s\S]*?(?=@router\.get|\Z)'
    new_content, count_recent = re.subn(pattern_recent, '', new_content, flags=re.MULTILINE)
    print(f"删除了 {count_recent} 个 recent-activity 端点")

    # 清理多余的空行
    new_content = re.sub(r'\n\n+', '\n', new_content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("文件更新完成")
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)
    sys.exit(1)
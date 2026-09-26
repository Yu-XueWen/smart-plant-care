file_path = r"d:\Improve\smart-plant-care\frontend\src\api\modules\admin.ts"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 替换路径
new_content = content.replace("/admin/statistics", "/admin/dashboard/summary")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Updated {file_path}")
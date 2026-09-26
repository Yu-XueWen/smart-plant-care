file_path = r"d:\Improve\smart-plant-care\backend\app\api\models\__init__.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 找到并替换 __all__ 行
new_lines = []
for line in lines:
    if line.strip().startswith("__all__"):
        # 替换为新的 __all__ 列表
        new_lines.append("__all__ = [\n")
        new_lines.append('    "User",\n')
        new_lines.append('    "UserPlant",\n')
        new_lines.append('    "WateringRecord",\n')
        new_lines.append('    "TreatmentRecord",\n')
        new_lines.append('    "RemindConfig",\n')
        new_lines.append('    "IdentifyHistory",\n')
        new_lines.append('    "DiagnoseHistory",\n')
        new_lines.append('    "PlantSpecies",\n')
        new_lines.append('    "RecommendationHistory",\n')
        new_lines.append('    "OperationLog",\n')
        new_lines.append('    "LoginLog"\n')
        new_lines.append("]\n")
    else:
        new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Updated {file_path}")
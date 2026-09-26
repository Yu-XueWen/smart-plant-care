import re

file_path = r"d:\Improve\smart-plant-care\backend\app\api\models\__init__.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 替换 __all__ 行
new_content = re.sub(
    r'__all__ = \[.*?\]',
    '__all__ = [\n    "User",\n    "UserPlant",\n    "WateringRecord",\n    "TreatmentRecord",\n    "RemindConfig",\n    "IdentifyHistory",\n    "DiagnoseHistory",\n    "PlantSpecies",\n    "RecommendationHistory",\n    "OperationLog",\n    "LoginLog"\n]',
    content,
    flags=re.DOTALL
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Updated {file_path}")
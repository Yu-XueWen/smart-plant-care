file_path = r"d:\Improve\smart-plant-care\frontend\src\views\admin\Dashboard.vue"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 修正拼写错误
content = content.replace("<el-despite", "<el-describe")
content = content.replace("</el-despite>", "</el-describe>")
content = content.replace("<el-desitem", "<el-describe-item")
content = content.replace("</el-desitem>", "</el-describe-item>")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Fixed {file_path}")
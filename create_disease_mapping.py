"""
创建病害名称中英文映射关系
"""
import os
import json

# 数据集路径
dataset_path = r"D:\Practicum\smart-plant-care\ai_models\data\New Plant Diseases Dataset\train"

# 获取所有类别文件夹
categories = sorted([d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))])

print(f"总共找到 {len(categories)} 个类别\n")
print("=" * 80)

# 创建中英文映射字典
disease_mapping = {}

for category in categories:
    print(f"{category}")

print("\n" + "=" * 80)
print("\n生成映射关系...")

# 完整的中英文映射（基于PlantVillage数据集）
disease_name_mapping = {
    # Apple (苹果)
    "Apple___Apple_scab": "苹果黑星病",
    "Apple___Black_rot": "苹果黑腐病",
    "Apple___Cedar_apple_rust": "苹果 cedar 锈病",
    "Apple___healthy": "苹果健康",
    
    # Blueberry (蓝莓)
    "Blueberry___healthy": "蓝莓健康",
    
    # Cherry (樱桃)
    "Cherry_(including_sour)___Powdery_mildew": "樱桃白粉病",
    "Cherry_(including_sour)___healthy": "樱桃健康",
    
    # Corn/Maize (玉米)
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "玉米灰斑病",
    "Corn_(maize)___Common_rust_": "玉米普通锈病",
    "Corn_(maize)___Northern_Leaf_Blight": "玉米北方叶枯病",
    "Corn_(maize)___healthy": "玉米健康",
    
    # Grape (葡萄)
    "Grape___Black_rot": "葡萄黑腐病",
    "Grape___Esca_(Black_Measles)": "葡萄埃斯卡病(黑麻疹)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "葡萄叶斑病",
    "Grape___healthy": "葡萄健康",
    
    # Orange (橙子/柑橘)
    "Orange___Haunglongbing_(Citrus_greening)": "柑橘黄龙病",
    
    # Peach (桃子)
    "Peach___Bacterial_spot": "桃细菌性斑点病",
    "Peach___healthy": "桃健康",
    
    # Pepper (辣椒)
    "Pepper,_bell___Bacterial_spot": "辣椒细菌性斑点病",
    "Pepper,_bell___healthy": "辣椒健康",
    
    # Potato (马铃薯)
    "Potato___Early_blight": "马铃薯早疫病",
    "Potato___Late_blight": "马铃薯晚疫病",
    "Potato___healthy": "马铃薯健康",
    
    # Raspberry (覆盆子)
    "Raspberry___healthy": "覆盆子健康",
    
    # Soybean (大豆)
    "Soybean___healthy": "大豆健康",
    
    # Squash (南瓜)
    "Squash___Powdery_mildew": "南瓜白粉病",
    
    # Strawberry (草莓)
    "Strawberry___Leaf_scorch": "草莓叶焦病",
    "Strawberry___healthy": "草莓健康",
    
    # Tomato (番茄)
    "Tomato___Bacterial_spot": "番茄细菌性斑点病",
    "Tomato___Early_blight": "番茄早疫病",
    "Tomato___Late_blight": "番茄晚疫病",
    "Tomato___Leaf_Mold": "番茄叶霉病",
    "Tomato___Septoria_leaf_spot": "番茄斑枯病",
    "Tomato___Spider_mites Two-spotted_spider_mite": "番茄二斑叶螨",
    "Tomato___Target_Spot": "番茄靶斑病",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "番茄黄化曲叶病毒病",
    "Tomato___Tomato_mosaic_virus": "番茄花叶病毒病",
    "Tomato___healthy": "番茄健康"
}

# 验证映射完整性
print("\n映射关系验证:")
print("-" * 80)

missing = []
for category in categories:
    if category not in disease_name_mapping:
        missing.append(category)
        print(f"❌ 缺少映射: {category}")
    else:
        print(f"✅ {category} -> {disease_name_mapping[category]}")

if missing:
    print(f"\n⚠️  警告: 有 {len(missing)} 个类别缺少映射")
else:
    print(f"\n✅ 所有 {len(categories)} 个类别都有映射")

# 保存映射到JSON文件
output_file = r"D:\Practicum\smart-plant-care\backend\disease_name_mapping.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(disease_name_mapping, f, ensure_ascii=False, indent=2)

print(f"\n💾 映射关系已保存到: {output_file}")
print(f"📊 共 {len(disease_name_mapping)} 个映射关系")

# 同时生成Python字典格式，方便直接复制使用
print("\n" + "=" * 80)
print("Python字典格式（可直接复制到代码中）:")
print("=" * 80)
print("DISEASE_NAME_MAPPING = {")
for eng, chi in disease_name_mapping.items():
    print(f'    "{eng}": "{chi}",')
print("}")

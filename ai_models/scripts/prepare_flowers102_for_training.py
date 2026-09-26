"""
准备 Flowers-102 数据集用于 YOLOv8 分类训练
将 flowers-102/train 和 flowers-102/val 复制到 processed/plant_classification
"""
import os
import shutil
from pathlib import Path
from tqdm import tqdm

def prepare_flowers102_dataset():
    """
    从 Flowers-102 数据集准备训练数据
    文件夹名称已经是英文花卉名（如 sunflower, rose 等）
    """
    # 源数据路径
    source_root = Path("../data/flowers-102")
    source_train = source_root / "train"
    source_val = source_root / "val"
    
    # 目标路径
    output_dir = Path("../processed/plant_classification")
    target_train = output_dir / "train"
    target_val = output_dir / "val"
    
    # 清理旧的训练数据
    if output_dir.exists():
        print(f"清理旧数据: {output_dir}")
        shutil.rmtree(output_dir)
    
    # 创建目录结构
    target_train.mkdir(parents=True, exist_ok=True)
    target_val.mkdir(parents=True, exist_ok=True)
    
    # 检查源目录是否存在
    if not source_train.exists():
        print(f"错误: 源训练目录不存在: {source_train}")
        return
    
    if not source_val.exists():
        print(f"错误: 源验证目录不存在: {source_val}")
        return
    
    print("=" * 60)
    print("开始准备 Flowers-102 数据集")
    print("=" * 60)
    
    # 复制训练集
    print("\n📁 复制训练集...")
    train_classes = list(source_train.iterdir())
    print(f"找到 {len(train_classes)} 个类别")
    
    for class_dir in tqdm(train_classes, desc="训练集"):
        if class_dir.is_dir():
            class_name = class_dir.name
            target_class_dir = target_train / class_name
            target_class_dir.mkdir(exist_ok=True)
            
            # 复制所有图片
            for img_file in class_dir.glob("*"):
                if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    shutil.copy2(img_file, target_class_dir / img_file.name)
    
    # 复制验证集
    print("\n📁 复制验证集...")
    val_classes = list(source_val.iterdir())
    print(f"找到 {len(val_classes)} 个类别")
    
    for class_dir in tqdm(val_classes, desc="验证集"):
        if class_dir.is_dir():
            class_name = class_dir.name
            target_class_dir = target_val / class_name
            target_class_dir.mkdir(exist_ok=True)
            
            # 复制所有图片
            for img_file in class_dir.glob("*"):
                if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    shutil.copy2(img_file, target_class_dir / img_file.name)
    
    # 统计信息
    print("\n" + "=" * 60)
    print("✅ 数据集准备完成！")
    print("=" * 60)
    print(f"\n训练集位置: {target_train}")
    print(f"验证集位置: {target_val}")
    print(f"\n训练集类别数: {len(list(target_train.iterdir()))}")
    print(f"验证集类别数: {len(list(target_val.iterdir()))}")
    
    # 显示前10个类别名称
    print("\n示例类别名称（前10个）:")
    for i, class_dir in enumerate(sorted(target_train.iterdir())[:10]):
        img_count = len(list(class_dir.glob("*")))
        print(f"  {i+1:3d}. {class_dir.name:40s} ({img_count:4d} 张图片)")
    
    print("\n⚠️  重要提示:")
    print("   现在模型的类别名称将是花卉的英文名称（如 'sunflower', 'rose'）")
    print("   训练完成后，需要通过 flower_name_mapping.json 转换为中文")

if __name__ == "__main__":
    prepare_flowers102_dataset()

import os
import shutil
from pathlib import Path
import yaml

def prepare_disease_dataset():
    # 原始数据路径
    script_dir = Path(__file__).parent
    data_root = script_dir / "../data/New Plant Diseases Dataset"
    train_dir = data_root / "train"
    valid_dir = data_root / "val"

    # 验证输入路径
    if not train_dir.exists():
        print(f"错误：训练数据目录不存在：{train_dir.absolute()}")
        return False
    if not valid_dir.exists():
        print(f"错误：验证数据目录不存在：{valid_dir.absolute()}")
        return False

    # 输出路径
    output_dir = script_dir / "../processed/disease_detection"
    images_dir = output_dir / "images"
    labels_dir = output_dir / "labels"
    print(f"输出目录：{output_dir.absolute()}")
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有类别（从 train 子文件夹名称）
    class_names = [d.name for d in train_dir.iterdir() if d.is_dir()]
    class_names.sort()
    class_to_id = {name: idx for idx, name in enumerate(class_names)}
    print(f"找到 {len(class_names)} 个植物病害类别")

    # 复制训练集和验证集图片，并生成标注
    image_count = 0
    label_count = 0
    for split in ["train", "val"]:
        src_dir = train_dir if split == "train" else valid_dir
        print(f"\n处理 {split} 数据集...")
        
        # 创建 train/val 子目录
        split_images_dir = output_dir / split / "images"
        split_labels_dir = output_dir / split / "labels"
        split_images_dir.mkdir(parents=True, exist_ok=True)
        split_labels_dir.mkdir(parents=True, exist_ok=True)
        
        for class_name in class_names:
            class_src = src_dir / class_name
            if not class_src.exists():
                continue
            class_id = class_to_id[class_name]
            for img_path in class_src.glob("*"):
                if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                    continue
                # 目标文件名：保持原名（避免重名冲突）
                dst_img = split_images_dir / f"{class_id}_{img_path.name}"
                shutil.copy(img_path, dst_img)
                image_count += 1

                # 获取图片尺寸（可选，这里假设已固定，或从原图读取）
                # 我们直接使用整图框（归一化坐标）
                yolo_line = f"{class_id} 0.5 0.5 1.0 1.0\n"
                label_file = split_labels_dir / dst_img.stem
                with open(label_file.with_suffix(".txt"), "w") as f:
                    f.write(yolo_line)
                label_count += 1

    # 生成 dataset.yaml
    dataset_yaml = {
        "path": str(output_dir.resolve()),  # 使用绝对路径
        "train": "train/images",
        "val": "val/images",
        "nc": len(class_names),
        "names": class_names
    }
    with open(output_dir / "dataset.yaml", "w") as f:
        yaml.dump(dataset_yaml, f, default_flow_style=False)
    
    print(f"\n{'='*50}")
    print(f"数据集准备完成！")
    print(f"{'='*50}")
    print(f"总类别数：{len(class_names)}")
    print(f"处理图片数：{image_count}")
    print(f"生成标签数：{label_count}")
    print(f"输出目录：{output_dir.resolve()}")
    
    return True

if __name__ == "__main__":
    prepare_disease_dataset()
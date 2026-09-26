import os
import shutil
from pathlib import Path
from ultralytics import YOLO
import torch

def train_plant_classifier():
    # 数据路径（YOLO 分类要求数据是 train 和 val 文件夹）
    data_dir = "../processed/plant_classification"   # 包含 train/ 和 val/
    # 输出路径
    project_dir = "runs/classify"
    exp_name = "plant_classifier"
    
    # 自动检测设备并设置参数
    device = '0' if torch.cuda.is_available() else 'cpu'
    num_workers = min(8, (os.cpu_count() or 4) // 2)  # 使用 CPU 核心数的一半，最多 8 个
    
    # 加载预训练分类模型（使用项目根目录的本地权重文件）
    model_path = Path(__file__).parent.parent.parent / "yolov8n-cls.pt"
    if not model_path.exists():
        raise FileNotFoundError(f"未找到模型权重文件：{model_path}")
    print(f"✓ 使用预训练模型: {model_path}")
    model = YOLO(str(model_path))  # 分类预训练权重

    # 训练参数
    results = model.train(
        # === 基础配置 ===
        data=data_dir,              # 数据集路径（包含 train/val 子目录）
        epochs=100,                 # 训练总轮数：完整遍历数据集的次数
        imgsz=224,                  # 输入图像尺寸：分类任务常用 224x224
        batch=32,                   # 批次大小：每批处理 32 张图像，适配 6GB 显存（RTX 4050）
        device=device,              # 训练设备：'0'使用 GPU 0，'cpu'使用 CPU
        workers=num_workers,        # 数据加载线程数：根据 CPU 核心数自适应
        
        # === 实验管理 ===
        project=project_dir,        # 项目保存路径：训练结果输出目录
        name=exp_name,              # 实验名称：本次训练的标识
        exist_ok=True,              # 覆盖已有实验：True 允许覆盖同名实验
        pretrained=True,            # 加载预训练权重：True 使用 ImageNet 预训练模型
        
        # === 优化器配置 ===
        optimizer="AdamW",          # 优化器类型：AdamW 收敛更快更稳定
        lr0=0.003,                  # 初始学习率：AdamW 分类任务推荐值
        lrf=0.01,                   # 最终学习率因子：结束时的学习率 = lr0 * lrf
        weight_decay=5e-4,          # 权重衰减：L2 正则化系数，防止过拟合
        
        # === 学习率调度 ===
        warmup_epochs=5,            # 预热轮数：前 5 轮线性增加学习率
        warmup_momentum=0.8,        # 预热动量：预热阶段使用的动量值
        warmup_bias_lr=0.1,         # 预热偏置学习率：bias 层的初始学习率
        
        # === 网络结构 ===
        dropout=0.2,                # Dropout 比率：全连接层丢弃率，防止过拟合
        
        # === 数据增强 - HSV 色彩空间 ===
        hsv_h=0.015,                # 色调增强：±1.5% 色相变化
        hsv_s=0.7,                  # 饱和度增强：±70% 饱和度变化
        hsv_v=0.4,                  # 亮度增强：±40% 明度变化
        
        # === 数据增强 - 几何变换 ===
        degrees=0.0,                # 旋转角度：±0°（分类任务通常不旋转）
        translate=0.1,              # 平移比例：±10% 图像平移
        scale=0.5,                  # 缩放比例：50%-150% 随机缩放
        shear=0.0,                  # 剪切角度：无剪切
        perspective=0.0,            # 透视变换：无透视变形
        
        # === 数据增强 - 翻转 ===
        flipud=0.0,                 # 上下翻转概率：0%（植物图片通常不需要）
        fliplr=0.5,                 # 左右翻转概率：50%（常用增强）
        
        # === 高级增强 ===
        mosaic=1.0,                 # Mosaic 增强概率：100%（YOLO 特色增强）
        mixup=0.1,                  # Mixup 混合概率：10%（轻微增强，帮助泛化）
        copy_paste=0.0              # Copy-Paste 增强：0%（用于实例分割）
    )

    # 复制最佳模型
    best_model_path = Path(project_dir) / exp_name / "weights" / "best.pt"
    if best_model_path.exists():
        dest_dir = Path("../models/plant_classification")
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(best_model_path, dest_dir / "best.pt")
        print(f"模型已保存到 {dest_dir / 'best.pt'}")
    else:
        print("未找到最佳模型权重！")

    print(results)

if __name__ == "__main__":
    train_plant_classifier()
import os
import shutil
from pathlib import Path
from ultralytics import YOLO
import torch

def train_disease_detector():
    # 数据路径
    dataset_yaml = "../processed/disease_detection/dataset.yaml"
    # 输出路径（YOLO 默认 runs/detect/train，我们指定为当前目录下 runs，最后复制模型）
    project_dir = "runs/detect"
    exp_name = "disease_detector"
    
    # 自动检测设备并设置参数
    device = '0' if torch.cuda.is_available() else 'cpu'
    num_workers = 2  # Windows 系统减少 worker 数量以避免内存问题
    
    # 加载预训练模型（使用本地权重文件，避免网络下载）
    model_path = Path(__file__).parent.parent.parent / "yolov8n.pt"
    print(f"检查模型路径：{model_path.absolute()}")
    print(f"模型文件存在：{model_path.exists()}")
    
    if not model_path.exists():
        # 尝试当前工作目录
        alt_model_path = Path("yolov8n.pt")
        if alt_model_path.exists():
            model_path = alt_model_path
            print(f"使用备用模型路径：{model_path.absolute()}")
        else:
            raise FileNotFoundError(f"未找到模型权重文件：{model_path}")
    
    model = YOLO(str(model_path))  # 目标检测预训练权重

    # 训练参数
    results = model.train(
        # === 基础配置 ===
        data=dataset_yaml,          # 数据集配置文件路径（YOLO 格式 dataset.yaml）
        epochs=50,                 # 训练总轮数：完整遍历数据集的次数
        imgsz=640,                  # 输入图像尺寸：检测任务常用 640x640
        batch=16,                   # 批次大小：每批处理 16 张图像，适配 6GB 显存
        device=device,              # 训练设备：'0'使用 GPU 0，'cpu'使用 CPU
        workers=num_workers,        # 数据加载线程数：根据 CPU 核心数自适应
        
        # === 实验管理 ===
        project=project_dir,        # 项目保存路径：训练结果输出目录
        name=exp_name,              # 实验名称：本次训练的标识
        exist_ok=True,              # 覆盖已有实验：True 允许覆盖同名实验
        patience=10,                # 早停轮数：连续 15 轮无改进则停止训练
        pretrained=True,            # 加载预训练权重：True 使用 COCO 预训练模型
        
        # === 优化器配置 ===
        optimizer="AdamW",          # 优化器类型：AdamW 收敛更快更稳定
        lr0=0.002,                  # 初始学习率：AdamW 常用 0.002
        lrf=0.01,                   # 最终学习率因子：结束时的学习率 = lr0 * lrf
        weight_decay=0.001,         # 权重衰减：L2 正则化系数，防止过拟合
        
        # === 学习率调度 ===
        warmup_epochs=5,            # 预热轮数：前 5 轮线性增加学习率
        warmup_momentum=0.8,        # 预热动量：预热阶段使用的动量值
        warmup_bias_lr=0.1,         # 预热偏置学习率：bias 层的初始学习率
        
        # === 损失函数增益 ===
        box=7.5,                    # Box 损失增益：边界框定位损失权重
        cls=0.5,                    # Class 损失增益：分类损失权重
        dfl=1.5,                    # DFL 损失增益：分布焦点损失权重
        
        # === 数据增强 - HSV 色彩空间 ===
        hsv_h=0.015,                # 色调增强：±1.5% 色相变化
        hsv_s=0.7,                  # 饱和度增强：±70% 饱和度变化
        hsv_v=0.4,                  # 亮度增强：±40% 明度变化
        
        # === 数据增强 - 几何变换 ===
        degrees=0.0,                # 旋转角度：±0°（叶片病斑通常不旋转）
        translate=0.1,              # 平移比例：±10% 图像平移
        scale=0.5,                  # 缩放比例：50%-150% 随机缩放
        shear=0.0,                  # 剪切角度：无剪切
        perspective=0.0,            # 透视变换：无透视变形
        
        # === 数据增强 - 翻转 ===
        flipud=0.0,                 # 上下翻转概率：0%（病斑检测通常不需要）
        fliplr=0.5,                 # 左右翻转概率：50%（常用增强）
        
        # === 高级增强 ===
        mosaic=1.0,                 # Mosaic 增强概率：100%（YOLO 特色增强，拼接 4 张图）
        mixup=0.1,                  # Mixup 混合概率：10%（轻微增强，帮助泛化）
        copy_paste=0.0              # Copy-Paste 增强：0%（用于实例分割）
    )

    # 复制最佳模型到 models 目录
    best_model_path = Path(project_dir) / exp_name / "weights" / "best.pt"
    if best_model_path.exists():
        dest_dir = Path("../models/disease_detection")
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(best_model_path, dest_dir / "best.pt")
        print(f"模型已保存到 {dest_dir / 'best.pt'}")
    else:
        print("未找到最佳模型权重！")

    # 可选：打印训练结果
    print(results)

if __name__ == "__main__":
    train_disease_detector()
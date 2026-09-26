import os
import shutil
import pandas as pd
import requests
from pathlib import Path
from tqdm import tqdm
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_image(url, save_path):
    """
    下载图片并保存到指定路径。
    
    Args:
        url: 图片 URL
        save_path: 保存路径
    
    Returns:
        tuple: (成功与否，保存路径)
    """
    if save_path.exists():
        return (True, save_path)  # 已存在则跳过
    
    try:
        response = requests.get(url, timeout=(5, 30), stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            return (True, save_path)
        elif response.status_code == 404:
            return (False, save_path)
        else:
            return (False, save_path)
    except Exception as e:
        return (False, save_path)

def prepare_plant_classification(limit_classes=120, max_images_per_class=500, max_workers=10):
    """
    从 PlantCLEF 2025 数据中筛选指定数量的常见物种，
    下载图片并按物种分类到 processed/plant_classification/ 下。
    
    Args:
        limit_classes: 限制的物种类别数量
        max_images_per_class: 每个类别的最大图片数
        max_workers: 并发下载的线程数（建议 5-20）
    """
    data_root = Path("../data/plantclef-2025")
    csv_file = data_root / "PlantCLEF2024_single_plant_training_metadata.csv"
    species_file = data_root / "species_ids.csv"

    if not csv_file.exists():
        print(f"未找到元数据文件: {csv_file}")
        print("请确保已正确放置 PlantCLEF 2025 数据。")
        sys.exit(1)

    # 读取物种映射表（如果存在，可能包含额外的物种信息）
    species_df = pd.read_csv(species_file, sep=';') if species_file.exists() else None
    # 读取元数据（只读取必要列，注意使用分号分隔符）
    df = pd.read_csv(csv_file, sep=';', usecols=["species_id", "url", "species"], nrows=100000)  # 可调整行数

    # 统计每个物种的图片数量，选出最常见的前 limit_classes 个
    species_counts = df["species_id"].value_counts()
    top_species = species_counts.head(limit_classes).index.tolist()

    # 输出目录
    output_dir = Path("../processed/plant_classification")
    train_dir = output_dir / "train"
    val_dir = output_dir / "val"
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    # 为每个物种创建文件夹
    # 使用 CSV 中的 species 列作为物种名称（如果没有则用 ID）
    species_names = {}
    for sid in top_species:
        subset = df[df["species_id"] == sid]
        if len(subset) > 0 and not pd.isna(subset.iloc[0]["species"]):
            species_names[sid] = subset.iloc[0]["species"]
        else:
            species_names[sid] = f"species_{sid}"

    # 遍历每个选中物种
    for species_id in top_species:
        # 获取物种名称（如果没有名称，用 ID）
        class_name = species_names.get(species_id, f"species_{species_id}")
        # 创建分类文件夹
        (train_dir / class_name).mkdir(exist_ok=True)
        (val_dir / class_name).mkdir(exist_ok=True)

        # 获取该物种的所有图片 URL
        urls = df[df["species_id"] == species_id]["url"].tolist()
        # 限制每类最多下载 max_images_per_class 张
        urls = urls[:max_images_per_class]
        # 随机划分训练/验证（8:2）
        split_idx = int(len(urls) * 0.8)
        train_urls = urls[:split_idx]
        val_urls = urls[split_idx:]

        # 收集所有需要下载的任务
        download_tasks = []
        
        # 训练集任务
        for idx, url in enumerate(train_urls):
            img_name = f"{species_id}_{idx}.jpg"
            save_path = train_dir / class_name / img_name
            if not save_path.exists():
                download_tasks.append((url, save_path))
        
        # 验证集任务
        for idx, url in enumerate(val_urls):
            img_name = f"{species_id}_{idx}.jpg"
            save_path = val_dir / class_name / img_name
            if not save_path.exists():
                download_tasks.append((url, save_path))
        
        # 使用线程池并发下载
        if download_tasks:
            success_count = 0
            fail_count = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有下载任务
                future_to_url = {
                    executor.submit(download_image, url, path): (url, path) 
                    for url, path in download_tasks
                }
                
                # 显示进度条
                for future in tqdm(as_completed(future_to_url), total=len(download_tasks), 
                                 desc=f"下载 {class_name}", leave=False):
                    url, save_path = future_to_url[future]
                    try:
                        success, path = future.result()
                        if success:
                            success_count += 1
                        else:
                            fail_count += 1
                    except Exception as e:
                        fail_count += 1
            
            print(f"\n{class_name}: 成功 {success_count}/{len(download_tasks)}, 失败 {fail_count}")

    print(f"完成！共处理 {len(top_species)} 个物种，图片保存在 {output_dir}")

if __name__ == "__main__":
    prepare_plant_classification()
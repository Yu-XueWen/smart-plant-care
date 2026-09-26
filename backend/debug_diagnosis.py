"""
完整诊断流程测试 - 找出为什么总是返回黑斑病
"""
import sys
import asyncio
sys.path.insert(0, 'D:/Practicum/smart-plant-care/backend')

from app.api.services.ai_service import AIService
from pathlib import Path
import os

async def test_full_diagnosis():
    """测试完整的诊断流程"""
    
    print("=" * 80)
    print("病害诊断完整流程测试")
    print("=" * 80)
    
    # 1. 检查AI服务初始化
    print("\n1. 初始化AI服务...")
    ai_service = AIService()
    
    # 2. 检查模型是否加载
    print(f"\n2. 模型加载状态:")
    print(f"   - 植物检测模型: {'✓ 已加载' if ai_service.plant_detector else '✗ 未加载'}")
    print(f"   - 植物分类模型: {'✓ 已加载' if ai_service.plant_classifier else '✗ 未加载'}")
    print(f"   - 病害检测模型: {'✓ 已加载' if ai_service.disease_detector else '✗ 未加载'}")
    
    # 3. 检查病害名称映射
    print(f"\n3. 病害名称映射:")
    print(f"   - 映射数量: {len(ai_service.disease_name_mapping)}")
    if len(ai_service.disease_name_mapping) > 0:
        print(f"   - 示例: Tomato___Early_blight -> {ai_service.disease_name_mapping.get('Tomato___Early_blight', 'N/A')}")
    
    # 4. 查找测试图片
    print(f"\n4. 查找测试图片...")
    upload_dir = Path("D:/Practicum/smart-plant-care/backend/uploads")
    if upload_dir.exists():
        images = list(upload_dir.glob("*.jpg")) + list(upload_dir.glob("*.png")) + list(upload_dir.glob("*.webp"))
        if images:
            print(f"   找到 {len(images)} 张图片")
            test_image = str(images[-1])  # 使用最后一张图片
            print(f"   测试图片: {test_image}")
        else:
            print(f"   ⚠️  uploads目录中没有图片")
            print(f"   请先上传一些病害图片进行测试")
            return
    else:
        print(f"   ⚠️  uploads目录不存在")
        return
    
    # 5. 测试诊断
    print(f"\n5. 开始诊断测试...")
    print("-" * 80)
    
    image_url = f"/uploads/{Path(test_image).name}"
    print(f"图片URL: {image_url}")
    
    try:
        result = await ai_service.diagnose_disease(image_url)
        
        print(f"\n诊断结果:")
        print(f"   - 病害名称: {result['primary_disease']}")
        print(f"   - 置信度: {result['confidence']}")
        print(f"   - 症状描述: {result['symptoms'][:50]}...")
        
        # 判断是否使用了mock数据
        if result['primary_disease'] == '黑斑病' and result['confidence'] == 0.85:
            print(f"\n⚠️  警告: 检测到使用的是模拟数据（Mock Data）！")
            print(f"   这说明模型没有正确工作或没有检测到目标")
            print(f"\n可能的原因:")
            print(f"   1. 模型未加载成功")
            print(f"   2. 图片无法读取")
            print(f"   3. 模型推理失败")
            print(f"   4. 未检测到任何病害目标")
            print(f"\n请查看上方的详细日志输出，找到具体原因")
        else:
            print(f"\n✓ 诊断成功，使用的是真实模型结果")
            
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_full_diagnosis())

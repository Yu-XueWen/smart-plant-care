"""
检查知识图谱中的浇水频率信息
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.api.core.neo4j_client import Neo4jClient

def check_watering_info():
    """检查知识图谱中的浇水信息"""
    neo4j_client = Neo4jClient()
    
    print("=" * 100)
    print("检查知识图谱中的浇水频率信息")
    print("=" * 100)
    
    # 查询所有植物的浇水管理信息
    query = """
    MATCH (p:Plant)
    RETURN p.name AS plant_name,
           p.watering_management AS watering_management
    ORDER BY p.name
    LIMIT 20
    """
    
    with neo4j_client.driver.session() as session:
        result = session.run(query)
        plants = result.data()
        
        print(f"\n前20个植物的浇水管理信息:\n")
        
        for idx, plant in enumerate(plants, 1):
            print(f"{idx}. {plant['plant_name']}")
            watering = plant.get('watering_management')
            if watering:
                # 截取前60个字符显示
                display_text = watering[:60] + "..." if len(watering) > 60 else watering
                print(f"   浇水管理: {display_text}")
            else:
                print(f"   浇水管理: 无数据")
            print()
    
    # 统计有浇水信息的植物数量
    count_query = """
    MATCH (p:Plant)
    WHERE p.watering_management IS NOT NULL AND p.watering_management <> ''
    RETURN count(p) AS count_with_watering
    """
    
    total_query = """
    MATCH (p:Plant)
    RETURN count(p) AS total
    """
    
    with neo4j_client.driver.session() as session:
        count_result = session.run(count_query).single()
        total_result = session.run(total_query).single()
        
        count_with_watering = count_result['count_with_watering'] if count_result else 0
        total_plants = total_result['total'] if total_result else 0
        
        print("=" * 100)
        print(f"统计信息:")
        print(f"  - 植物总数: {total_plants}")
        print(f"  - 有浇水管理信息的植物: {count_with_watering}")
        print(f"  - 覆盖率: {count_with_watering/total_plants*100:.1f}%" if total_plants > 0 else "  - 覆盖率: 0%")
        print("=" * 100)
        
        # 检查是否有结构化的浇水频率字段
        schema_query = """
        MATCH (p:Plant)
        RETURN keys(p) AS properties
        LIMIT 1
        """
        
        schema_result = session.run(schema_query).single()
        if schema_result:
            properties = schema_result['properties']
            print(f"\n植物节点的属性列表:")
            for prop in sorted(properties):
                print(f"  - {prop}")
            
            # 检查是否有专门的浇水频率字段
            watering_fields = [p for p in properties if 'water' in p.lower()]
            if watering_fields:
                print(f"\n✓ 找到浇水相关字段: {watering_fields}")
            else:
                print(f"\n⚠ 未找到专门的浇水频率字段，使用 watering_management 文本字段")

if __name__ == "__main__":
    try:
        check_watering_info()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

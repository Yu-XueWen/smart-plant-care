"""
检查知识图谱中季节性浇水频率信息
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.api.core.neo4j_client import Neo4jClient

def check_seasonal_watering():
    """检查季节性浇水信息"""
    neo4j_client = Neo4jClient()
    
    print("=" * 100)
    print("检查知识图谱中的季节性浇水频率")
    print("=" * 100)
    
    # 查询植物的季节性浇水信息
    query = """
    MATCH (p:Plant)
    RETURN p.name AS plant_name,
           p.watering_management AS general_watering,
           p.watering_spring AS spring,
           p.watering_summer AS summer,
           p.watering_autumn AS autumn,
           p.watering_winter AS winter
    ORDER BY p.name
    LIMIT 15
    """
    
    with neo4j_client.driver.session() as session:
        result = session.run(query)
        plants = result.data()
        
        print(f"\n前15个植物的季节性浇水信息:\n")
        
        for idx, plant in enumerate(plants, 1):
            print(f"{idx}. {plant['plant_name']}")
            
            # 通用浇水管理
            general = plant.get('general_watering')
            if general:
                display = general[:50] + "..." if len(general) > 50 else general
                print(f"   通用: {display}")
            
            # 春季
            spring = plant.get('spring')
            if spring:
                display = spring[:40] + "..." if len(spring) > 40 else spring
                print(f"   春季: {display}")
            
            # 夏季
            summer = plant.get('summer')
            if summer:
                display = summer[:40] + "..." if len(summer) > 40 else display
                print(f"   夏季: {display}")
            
            # 秋季
            autumn = plant.get('autumn')
            if autumn:
                display = autumn[:40] + "..." if len(autumn) > 40 else autumn
                print(f"   秋季: {display}")
            
            # 冬季
            winter = plant.get('winter')
            if winter:
                display = winter[:40] + "..." if len(winter) > 40 else winter
                print(f"   冬季: {display}")
            
            print()
    
    # 统计各字段的覆盖率
    stats_query = """
    MATCH (p:Plant)
    WITH 
      count(p) AS total,
      count(CASE WHEN p.watering_spring IS NOT NULL AND p.watering_spring <> '' THEN 1 END) AS spring_count,
      count(CASE WHEN p.watering_summer IS NOT NULL AND p.watering_summer <> '' THEN 1 END) AS summer_count,
      count(CASE WHEN p.watering_autumn IS NOT NULL AND p.watering_autumn <> '' THEN 1 END) AS autumn_count,
      count(CASE WHEN p.watering_winter IS NOT NULL AND p.watering_winter <> '' THEN 1 END) AS winter_count
    RETURN total, spring_count, summer_count, autumn_count, winter_count
    """
    
    with neo4j_client.driver.session() as session:
        stats = session.run(stats_query).single()
        
        if stats:
            total = stats['total']
            print("=" * 100)
            print(f"季节性浇水信息覆盖率:")
            print(f"  - 植物总数: {total}")
            print(f"  - 春季浇水: {stats['spring_count']} ({stats['spring_count']/total*100:.1f}%)")
            print(f"  - 夏季浇水: {stats['summer_count']} ({stats['summer_count']/total*100:.1f}%)")
            print(f"  - 秋季浇水: {stats['autumn_count']} ({stats['autumn_count']/total*100:.1f}%)")
            print(f"  - 冬季浇水: {stats['winter_count']} ({stats['winter_count']/total*100:.1f}%)")
            print("=" * 100)

if __name__ == "__main__":
    try:
        check_seasonal_watering()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

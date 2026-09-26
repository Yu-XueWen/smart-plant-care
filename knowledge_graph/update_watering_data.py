"""
植物浇水数据更新脚本
从 watering.txt 读取浇水频率数据并更新到 Neo4j 知识图谱
"""
import csv
from neo4j import GraphDatabase
from pathlib import Path
from typing import List, Dict, Any
import sys


class WateringDataUpdater:
    """浇水数据更新器"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """初始化 Neo4j 连接"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        print(f"✓ 已连接到 Neo4j: {uri}")
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            print("✓ Neo4j 连接已关闭")
    
    def parse_watering_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析 watering.txt 文件"""
        watering_data = []
        
        # 尝试多种编码
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.reader(f, delimiter='\t')
                    headers = next(reader)  # 跳过标题行
                    
                    print(f"✓ 使用编码: {encoding}")
                    print(f"✓ 表头: {headers}")
                    
                    for row_num, row in enumerate(reader, start=2):
                        if len(row) < 5:
                            print(f"⚠ 第 {row_num} 行数据不完整({len(row)}列)，跳过")
                            continue
                        
                        try:
                            plant_name = row[0].strip()
                            spring = row[1].strip()
                            summer = row[2].strip()
                            autumn = row[3].strip()
                            winter = row[4].strip()
                            
                            if not plant_name:
                                continue
                            
                            watering_info = {
                                'plant_name': plant_name,
                                'spring': spring,
                                'summer': summer,
                                'autumn': autumn,
                                'winter': winter,
                            }
                            
                            watering_data.append(watering_info)
                            
                        except Exception as e:
                            print(f"⚠ 解析第 {row_num} 行时出错: {e}")
                            continue
                    
                    # 如果成功解析，跳出循环
                    if watering_data:
                        break
                        
            except UnicodeDecodeError:
                print(f"⚠ 编码 {encoding} 失败，尝试下一个...")
                continue
        
        print(f"✓ 成功解析 {len(watering_data)} 条浇水数据")
        return watering_data
    
    def update_plant_watering(self, watering_data: List[Dict[str, Any]]):
        """批量更新植物浇水数据到 Neo4j"""
        with self.driver.session(database=self.database) as session:
            total = len(watering_data)
            success_count = 0
            not_found_count = 0
            
            for idx, data in enumerate(watering_data, 1):
                try:
                    plant_name = data['plant_name']
                    
                    # 处理括号问题：将英文括号转换为中文括号
                    normalized_name = plant_name.replace('(', '（').replace(')', '）')
                    
                    # 检查植物是否存在（尝试原始名称和标准化名称）
                    result = session.run("""
                        MATCH (p:Plant)
                        WHERE p.name = $plant_name OR p.name = $normalized_name
                        RETURN p.name as name
                        LIMIT 1
                    """, plant_name=plant_name, normalized_name=normalized_name)
                    
                    record = result.single()
                    
                    if not record:
                        print(f"⚠ 未找到植物: {plant_name}")
                        not_found_count += 1
                        continue
                    
                    # 使用实际找到的植物名称
                    actual_name = record['name']
                    
                    # 更新植物的浇水信息
                    session.run("""
                        MATCH (p:Plant {name: $plant_name})
                        SET p.watering_spring = $spring,
                            p.watering_summer = $summer,
                            p.watering_autumn = $autumn,
                            p.watering_winter = $winter,
                            p.updated_at = timestamp()
                    """, 
                        plant_name=actual_name,
                        spring=data['spring'],
                        summer=data['summer'],
                        autumn=data['autumn'],
                        winter=data['winter']
                    )
                    
                    success_count += 1
                    
                    if idx % 10 == 0:
                        print(f"进度: {idx}/{total} ({idx*100//total}%) - 成功: {success_count}, 未找到: {not_found_count}")
                
                except Exception as e:
                    print(f"✗ 更新植物 '{data.get('plant_name', 'Unknown')}' 时出错: {e}")
                    continue
            
            print(f"\n✓ 更新完成:")
            print(f"  - 总计: {total} 条")
            print(f"  - 成功: {success_count} 条")
            print(f"  - 未找到: {not_found_count} 条")
    
    def get_watering_statistics(self) -> Dict[str, int]:
        """获取浇水数据统计"""
        with self.driver.session(database=self.database) as session:
            stats = {}
            
            # 统计有浇水信息的植物数量
            queries = {
                'plants_with_watering': """
                    MATCH (p:Plant)
                    WHERE p.watering_spring IS NOT NULL
                    RETURN count(p) as count
                """,
                'plants_without_watering': """
                    MATCH (p:Plant)
                    WHERE p.watering_spring IS NULL
                    RETURN count(p) as count
                """,
                'total_plants': "MATCH (p:Plant) RETURN count(p) as count",
            }
            
            for key, query in queries.items():
                result = session.run(query)
                record = result.single()
                stats[key] = record['count'] if record else 0
            
            return stats
    
    def verify_sample_data(self, sample_size: int = 5):
        """验证样本数据"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (p:Plant)
                WHERE p.watering_spring IS NOT NULL
                RETURN p.name as name, 
                       p.watering_spring as spring,
                       p.watering_summer as summer,
                       p.watering_autumn as autumn,
                       p.watering_winter as winter
                LIMIT $limit
            """, limit=sample_size)
            
            print(f"\n📋 样本数据验证（前 {sample_size} 条）:")
            print("-" * 80)
            for record in result:
                print(f"  植物: {record['name']}")
                print(f"    春季: {record['spring']}")
                print(f"    夏季: {record['summer']}")
                print(f"    秋季: {record['autumn']}")
                print(f"    冬季: {record['winter']}")
                print()


def main():
    """主函数"""
    # Neo4j 连接配置
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "12345678"
    NEO4J_DATABASE = "neo4j"
    
    print("=" * 70)
    print("🌿 开始更新植物浇水数据到知识图谱")
    print("=" * 70)
    
    # watering.txt 文件路径
    script_dir = Path(__file__).parent.parent
    watering_file = script_dir / "watering.txt"
    
    print(f"\n检查文件: {watering_file}")
    if not watering_file.exists():
        print(f"✗ 找不到 watering.txt 文件: {watering_file}")
        sys.exit(1)
    
    print(f"✓ 找到 watering.txt 文件")
    
    # 创建更新器
    updater = WateringDataUpdater(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)
    
    try:
        # 1. 解析浇水数据
        print("\n【步骤 1】解析 watering.txt 文件...")
        watering_data = updater.parse_watering_file(str(watering_file))
        
        if not watering_data:
            print("✗ 没有解析到任何浇水数据")
            sys.exit(1)
        
        # 2. 更新数据到 Neo4j
        print("\n【步骤 2】更新浇水数据到 Neo4j...")
        updater.update_plant_watering(watering_data)
        
        # 3. 显示统计信息
        print("\n【步骤 3】统计信息:")
        stats = updater.get_watering_statistics()
        print(f"  - 总植物数: {stats['total_plants']}")
        print(f"  - 已有浇水信息: {stats['plants_with_watering']}")
        print(f"  - 缺少浇水信息: {stats['plants_without_watering']}")
        
        # 4. 验证样本数据
        print("\n【步骤 4】验证数据...")
        updater.verify_sample_data(5)
        
        print("\n" + "=" * 70)
        print("✅ 浇水数据更新完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 更新浇水数据时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        updater.close()


if __name__ == "__main__":
    main()

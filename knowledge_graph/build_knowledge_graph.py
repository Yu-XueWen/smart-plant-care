"""
植物知识图谱构建脚本
从 information 文件读取植物数据并导入 Neo4j
"""
import csv
from neo4j import GraphDatabase
from pathlib import Path
from typing import List, Dict, Any
import sys


class PlantKnowledgeGraph:
    """植物知识图谱管理器"""
    
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
    
    def clear_database(self):
        """清空数据库（谨慎使用）"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ 数据库已清空")
    
    def create_constraints_and_indexes(self):
        """创建约束和索引以提高查询性能"""
        with self.driver.session(database=self.database) as session:
            # 创建唯一性约束
            constraints = [
                "CREATE CONSTRAINT plant_name_unique IF NOT EXISTS FOR (p:Plant) REQUIRE p.name IS UNIQUE",
                "CREATE CONSTRAINT family_name_unique IF NOT EXISTS FOR (f:Family) REQUIRE f.name IS UNIQUE",
                "CREATE CONSTRAINT genus_name_unique IF NOT EXISTS FOR (g:Genus) REQUIRE g.name IS UNIQUE",
                "CREATE CONSTRAINT disease_name_unique IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
                "CREATE CONSTRAINT pest_name_unique IF NOT EXISTS FOR (p:Pest) REQUIRE p.name IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"✓ 创建约束: {constraint.split('FOR')[1].split()[0]}")
                except Exception as e:
                    print(f"⚠ 约束已存在或创建失败: {e}")
            
            # 创建索引
            indexes = [
                "CREATE INDEX plant_scientific_name_idx IF NOT EXISTS FOR (p:Plant) ON (p.scientific_name)",
                "CREATE INDEX plant_difficulty_idx IF NOT EXISTS FOR (p:Plant) ON (p.difficulty_level)",
                "CREATE INDEX plant_light_idx IF NOT EXISTS FOR (p:Plant) ON (p.light_requirement)",
                "CREATE INDEX disease_plant_idx IF NOT EXISTS FOR ()-[r:HAS_DISEASE]-() ON (r.confidence)",
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    print(f"✓ 创建索引成功")
                except Exception as e:
                    print(f"⚠ 索引创建失败: {e}")
    
    def parse_information_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析 information 文件"""
        plants = []
        
        # 尝试多种编码
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    # 跳过标题行
                    reader = csv.reader(f, delimiter='\t')
                    headers = next(reader)
                    print(f"✓ 使用编码: {encoding}")
                    
                    for row_num, row in enumerate(reader, start=2):
                        if len(row) < 19:  # 至少需要19列
                            print(f"⚠ 第 {row_num} 行数据不完整({len(row)}列)，跳过")
                            continue
                        
                        try:
                            plant_data = {
                                'id': int(row[0]),
                                'name_cn': row[1].strip(),
                                'name_en': row[2].strip(),
                                'scientific_name': row[3].strip(),
                                'family_genus': row[4].strip(),
                                'aliases': row[5].strip(),
                                'origin': row[6].strip(),
                                'description': row[7].strip(),
                                'light_requirement': row[8].strip(),
                                'temperature_range': row[9].strip(),
                                'humidity_requirement': row[10].strip(),
                                'soil_type': row[11].strip(),
                                'growth_rate': row[12].strip(),
                                'difficulty_level': row[13].strip(),
                                'watering_management': row[14].strip(),
                                'fertilization_plan': row[15].strip(),
                                'pruning_guide': row[16].strip(),
                                'propagation_methods': row[17].strip(),
                                'common_pests_diseases': row[18].strip(),
                            }
                            
                            # 解析科属信息
                            family_genus_parts = plant_data['family_genus'].split('/')
                            if len(family_genus_parts) == 2:
                                plant_data['family'] = family_genus_parts[0].replace('科', '').strip()
                                plant_data['genus'] = family_genus_parts[1].replace('属', '').strip()
                            else:
                                plant_data['family'] = ''
                                plant_data['genus'] = ''
                            
                            # 解析别名列表
                            plant_data['aliases_list'] = [
                                alias.strip() for alias in plant_data['aliases'].split('、') 
                                if alias.strip()
                            ]
                            
                            # 解析病虫害列表
                            plant_data['pests_diseases_list'] = [
                                pd.strip() for pd in plant_data['common_pests_diseases'].split('、')
                                if pd.strip()
                            ]
                            
                            # 解析繁殖方法列表
                            plant_data['propagation_list'] = [
                                method.strip() for method in plant_data['propagation_methods'].split('、')
                                if method.strip()
                            ]
                            
                            plants.append(plant_data)
                            
                        except Exception as e:
                            print(f"⚠ 解析第 {row_num} 行时出错: {e}")
                            continue
                    
                    # 如果成功解析，跳出循环
                    if plants:
                        break
                        
            except UnicodeDecodeError:
                print(f"⚠ 编码 {encoding} 失败，尝试下一个...")
                continue
        
        print(f"✓ 成功解析 {len(plants)} 条植物数据")
        return plants
    
    def import_plants(self, plants: List[Dict[str, Any]]):
        """批量导入植物数据到 Neo4j"""
        with self.driver.session(database=self.database) as session:
            total = len(plants)
            
            for idx, plant in enumerate(plants, 1):
                try:
                    # 1. 创建或更新 Family 节点
                    session.run("""
                        MERGE (f:Family {name: $family_name})
                        ON CREATE SET f.created_at = timestamp()
                    """, family_name=plant['family'])
                    
                    # 2. 创建或更新 Genus 节点
                    session.run("""
                        MERGE (g:Genus {name: $genus_name})
                        ON CREATE SET g.created_at = timestamp()
                    """, genus_name=plant['genus'])
                    
                    # 3. 创建 Plant 节点
                    session.run("""
                        MERGE (p:Plant {name: $name_cn})
                        ON CREATE SET 
                            p.name_en = $name_en,
                            p.scientific_name = $scientific_name,
                            p.origin = $origin,
                            p.description = $description,
                            p.light_requirement = $light_requirement,
                            p.temperature_range = $temperature_range,
                            p.humidity_requirement = $humidity_requirement,
                            p.soil_type = $soil_type,
                            p.growth_rate = $growth_rate,
                            p.difficulty_level = $difficulty_level,
                            p.watering_management = $watering_management,
                            p.fertilization_plan = $fertilization_plan,
                            p.pruning_guide = $pruning_guide,
                            p.aliases = $aliases_list,
                            p.propagation_methods = $propagation_list,
                            p.created_at = timestamp()
                        ON MATCH SET
                            p.name_en = $name_en,
                            p.scientific_name = $scientific_name,
                            p.updated_at = timestamp()
                    """, **plant)
                    
                    # 4. 创建关系：Plant -> BELONGS_TO -> Family
                    session.run("""
                        MATCH (p:Plant {name: $plant_name})
                        MATCH (f:Family {name: $family_name})
                        MERGE (p)-[:BELONGS_TO_FAMILY]->(f)
                    """, plant_name=plant['name_cn'], family_name=plant['family'])
                    
                    # 5. 创建关系：Plant -> BELONGS_TO -> Genus
                    session.run("""
                        MATCH (p:Plant {name: $plant_name})
                        MATCH (g:Genus {name: $genus_name})
                        MERGE (p)-[:BELONGS_TO_GENUS]->(g)
                    """, plant_name=plant['name_cn'], genus_name=plant['genus'])
                    
                    # 6. 创建关系：Family -> CONTAINS -> Genus
                    session.run("""
                        MATCH (f:Family {name: $family_name})
                        MATCH (g:Genus {name: $genus_name})
                        MERGE (f)-[:CONTAINS_GENUS]->(g)
                    """, family_name=plant['family'], genus_name=plant['genus'])
                    
                    # 7. 创建 Disease/Pest 节点和关系
                    for pest_disease in plant['pests_diseases_list']:
                        # 判断是病害还是虫害（简单规则：包含"病"字的是病害）
                        if '病' in pest_disease or '腐' in pest_disease or '霉' in pest_disease:
                            node_type = 'Disease'
                            rel_type = 'HAS_DISEASE'
                        else:
                            node_type = 'Pest'
                            rel_type = 'HAS_PEST'
                        
                        # 创建病害/虫害节点
                        session.run(f"""
                            MERGE (d:{node_type} {{name: $pd_name}})
                            ON CREATE SET d.created_at = timestamp()
                        """, pd_name=pest_disease)
                        
                        # 创建关系
                        session.run(f"""
                            MATCH (p:Plant {{name: $plant_name}})
                            MATCH (d:{node_type} {{name: $pd_name}})
                            MERGE (p)-[r:{rel_type}]->(d)
                            ON CREATE SET r.confidence = 0.8
                        """, plant_name=plant['name_cn'], pd_name=pest_disease)
                    
                    if idx % 10 == 0:
                        print(f"进度: {idx}/{total} ({idx*100//total}%)")
                
                except Exception as e:
                    print(f"✗ 导入植物 '{plant.get('name_cn', 'Unknown')}' 时出错: {e}")
                    continue
            
            print(f"\n✓ 成功导入 {total} 条植物数据")
    
    def get_statistics(self) -> Dict[str, int]:
        """获取知识图谱统计信息"""
        with self.driver.session(database=self.database) as session:
            stats = {}
            
            # 统计各类型节点数量
            queries = {
                'plants': "MATCH (p:Plant) RETURN count(p) as count",
                'families': "MATCH (f:Family) RETURN count(f) as count",
                'genera': "MATCH (g:Genus) RETURN count(g) as count",
                'diseases': "MATCH (d:Disease) RETURN count(d) as count",
                'pests': "MATCH (p:Pest) RETURN count(p) as count",
                'belongs_to_family_rels': "MATCH ()-[:BELONGS_TO_FAMILY]->() RETURN count(*) as count",
                'belongs_to_genus_rels': "MATCH ()-[:BELONGS_TO_GENUS]->() RETURN count(*) as count",
                'has_disease_rels': "MATCH ()-[:HAS_DISEASE]->() RETURN count(*) as count",
                'has_pest_rels': "MATCH ()-[:HAS_PEST]->() RETURN count(*) as count",
            }
            
            for key, query in queries.items():
                result = session.run(query)
                record = result.single()
                stats[key] = record['count'] if record else 0
            
            return stats


def main():
    """主函数"""
    # Neo4j 连接配置
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "12345678"
    NEO4J_DATABASE = "neo4j"
    
    # information 文件路径
    script_dir = Path(__file__).parent.parent
    info_file = script_dir / "information.txt"
    
    if not info_file.exists():
        print(f"✗ 找不到 information 文件: {info_file}")
        sys.exit(1)
    
    print("=" * 60)
    print("开始构建植物知识图谱")
    print("=" * 60)
    
    # 创建知识图谱管理器
    kg = PlantKnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)
    
    try:
        # 1. 创建约束和索引
        print("\n【步骤 1】创建约束和索引...")
        kg.create_constraints_and_indexes()
        
        # 2. 解析数据
        print("\n【步骤 2】解析 information 文件...")
        plants = kg.parse_information_file(str(info_file))
        
        if not plants:
            print("✗ 没有解析到任何植物数据")
            sys.exit(1)
        
        # 3. 导入数据
        print("\n【步骤 3】导入数据到 Neo4j...")
        kg.import_plants(plants)
        
        # 4. 显示统计信息
        print("\n【步骤 4】知识图谱统计信息:")
        stats = kg.get_statistics()
        print(f"  - 植物节点: {stats['plants']}")
        print(f"  - 科节点: {stats['families']}")
        print(f"  - 属节点: {stats['genera']}")
        print(f"  - 病害节点: {stats['diseases']}")
        print(f"  - 虫害节点: {stats['pests']}")
        print(f"  - 属于科关系: {stats['belongs_to_family_rels']}")
        print(f"  - 属于属关系: {stats['belongs_to_genus_rels']}")
        print(f"  - 患有病害关系: {stats['has_disease_rels']}")
        print(f"  - 患有虫害关系: {stats['has_pest_rels']}")
        
        print("\n" + "=" * 60)
        print("✓ 知识图谱构建完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 构建知识图谱时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        kg.close()


if __name__ == "__main__":
    main()

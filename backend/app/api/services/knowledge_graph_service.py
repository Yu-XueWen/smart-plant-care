"""
知识图谱服务 - 提供植物养护相关的图谱查询功能
"""
from typing import Dict, Any, List, Optional
from neo4j import Session
from app.utils.logger import setup_logger
from app.api.core.neo4j_client import Neo4jClient

logger = setup_logger("knowledge_graph_service")


class KnowledgeGraphService:
    """知识图谱服务类"""
    
    def __init__(self):
        self.neo4j_client = Neo4jClient()
    
    def _check_connection(self) -> bool:
        """检查Neo4j连接状态"""
        if not self.neo4j_client.connected:
            logger.warning("Neo4j未连接，知识图谱功能不可用")
            return False
        return True
    
    def get_plant_care_guide(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """
        从知识图谱获取植物养护指南
        
        Args:
            plant_name: 植物中文名称或学名
            
        Returns:
            养护指南字典，包含光照、浇水、施肥等信息
        """
        if not self._check_connection():
            return None
        
        # 使用更灵活的查询：支持中文名、学名、英文名、别名
        query = """
        MATCH (p:Plant)
        WHERE p.name = $plant_name 
           OR p.scientific_name = $plant_name 
           OR p.name_en = $plant_name
           OR $plant_name IN p.aliases
        RETURN p.name AS name_cn,
               p.name_en AS name_en,
               p.scientific_name AS scientific_name,
               p.light_requirement AS light_requirement,
               p.temperature_range AS temperature_range,
               p.humidity_requirement AS humidity_requirement,
               p.soil_type AS soil_type,
               p.watering_management AS watering_management,
               p.fertilization_plan AS fertilization_plan,
               p.pruning_guide AS pruning_guide,
               p.propagation_methods AS propagation_methods,
               p.difficulty_level AS difficulty_level,
               p.growth_rate AS growth_rate,
               p.description AS description
        LIMIT 1
        """
        
        with self.neo4j_client.driver.session() as session:
            result = session.run(query, plant_name=plant_name)
            record = result.single()
            
            if record:
                return {
                    "plant_name": record["name_cn"],
                    "scientific_name": record["scientific_name"],
                    "light_requirement": record["light_requirement"],
                    "temperature_range": record["temperature_range"],
                    "humidity_requirement": record["humidity_requirement"],
                    "soil_type": record["soil_type"],
                    "watering_management": record["watering_management"],
                    "fertilization_plan": record["fertilization_plan"],
                    "pruning_guide": record["pruning_guide"],
                    "propagation_methods": record["propagation_methods"],
                    "difficulty_level": record["difficulty_level"],
                    "growth_rate": record["growth_rate"],
                    "description": record["description"]
                }
        
        return None
    
    def get_plant_diseases_and_pests(self, plant_name: str) -> Dict[str, List[str]]:
        """
        获取植物常见病虫害
        
        Args:
            plant_name: 植物中文名称或学名
            
        Returns:
            包含病害和虫害列表的字典
        """
        if not self._check_connection():
            return {"diseases": [], "pests": []}
        
        query = """
        MATCH (p:Plant)
        WHERE p.name = $plant_name 
           OR p.scientific_name = $plant_name 
           OR p.name_en = $plant_name
           OR $plant_name IN p.aliases
        OPTIONAL MATCH (p)-[:HAS_DISEASE]->(d:Disease)
        WITH p, collect(d.name) AS diseases
        OPTIONAL MATCH (p)-[:HAS_PEST]->(pest:Pest)
        RETURN diseases, collect(pest.name) AS pests
        LIMIT 1
        """
        
        with self.neo4j_client.driver.session() as session:
            result = session.run(query, plant_name=plant_name)
            record = result.single()
            
            if record:
                return {
                    "diseases": record["diseases"] or [],
                    "pests": record["pests"] or []
                }
        
        return {"diseases": [], "pests": []}
    
    def get_disease_treatment(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """
        获取病害防治方案
        
        Args:
            disease_name: 病害名称
            
        Returns:
            防治方案信息
        """
        if not self._check_connection():
            return None
        
        # 首先查找哪些植物有这个病害
        query = """
        MATCH (p:Plant)-[:HAS_DISEASE]->(d:Disease {name: $disease_name})
        WITH p, d
        RETURN p.name AS plant_name,
               p.watering_management AS watering_advice,
               p.fertilization_plan AS fertilization_advice
        LIMIT 5
        """
        
        with self.neo4j_client.driver.session() as session:
            result = session.run(query, disease_name=disease_name)
            affected_plants = []
            
            for record in result:
                affected_plants.append({
                    "plant_name": record["plant_name"],
                    "watering_advice": record["watering_advice"],
                    "fertilization_advice": record["fertilization_advice"]
                })
            
            if affected_plants:
                return {
                    "disease_name": disease_name,
                    "affected_plants": affected_plants,
                    "general_advice": self._generate_disease_advice(disease_name, affected_plants)
                }
        
        return None
    
    def find_similar_plants(self, plant_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        查找相似植物（同科或同属）
        
        Args:
            plant_name: 植物名称（中文名、学名、英文名或别名）
            limit: 返回数量
            
        Returns:
            相似植物列表
        """
        if not self._check_connection():
            return []
        
        query = """
        MATCH (target:Plant)
        WHERE target.name = $plant_name 
           OR target.scientific_name = $plant_name 
           OR target.name_en = $plant_name
           OR $plant_name IN target.aliases
        MATCH (target)-[:BELONGS_TO_FAMILY]->(f:Family)<-[:BELONGS_TO_FAMILY]-(similar:Plant)
        WHERE similar.name <> target.name AND similar.scientific_name <> target.scientific_name
        WITH similar, 2 AS score
        OPTIONAL MATCH (target)-[:BELONGS_TO_GENUS]->(g:Genus)<-[:BELONGS_TO_GENUS]-(similar2:Plant)
        WHERE similar2.name <> target.name AND similar2.scientific_name <> target.scientific_name AND (similar2.name = similar.name OR similar2.scientific_name = similar.scientific_name)
        WITH similar, score + CASE WHEN similar2 IS NOT NULL THEN 3 ELSE 0 END AS final_score
        RETURN similar.name AS name,
               similar.scientific_name AS scientific_name,
               similar.difficulty_level AS difficulty,
               similar.light_requirement AS light,
               final_score AS similarity_score
        ORDER BY similarity_score DESC
        LIMIT $limit
        """
        
        with self.neo4j_client.driver.session() as session:
            result = session.run(query, plant_name=plant_name, limit=limit)
            
            similar_plants = []
            for record in result:
                similar_plants.append({
                    "name": record["name"],
                    "scientific_name": record["scientific_name"],
                    "difficulty": record["difficulty"],
                    "light_requirement": record["light"],
                    "similarity_score": record["similarity_score"]
                })
            
            return similar_plants
    
    def search_plants_by_condition(self, **kwargs) -> List[Dict[str, Any]]:
        """
        根据条件搜索植物
        
        Args:
            **kwargs: 搜索条件，如 difficulty_level, light_requirement 等
            
        Returns:
            符合条件的植物列表
        """
        conditions = []
        params = {}
        
        # 构建动态查询条件
        if kwargs.get('difficulty_level'):
            conditions.append("p.difficulty_level = $difficulty_level")
            params['difficulty_level'] = kwargs['difficulty_level']
        
        if kwargs.get('light_requirement'):
            conditions.append("p.light_requirement = $light_requirement")
            params['light_requirement'] = kwargs['light_requirement']
        
        if kwargs.get('growth_rate'):
            conditions.append("p.growth_rate = $growth_rate")
            params['growth_rate'] = kwargs['growth_rate']
        
        if not conditions:
            return []
        
        where_clause = " AND ".join(conditions)
        query = f"""
        MATCH (p:Plant)
        WHERE {where_clause}
        RETURN p.name AS name,
               p.scientific_name AS scientific_name,
               p.difficulty_level AS difficulty,
               p.light_requirement AS light,
               p.watering_management AS watering,
               p.description AS description
        LIMIT 20
        """
        
        with self.neo4j_client.driver.session() as session:
            result = session.run(query, **params)
            
            plants = []
            for record in result:
                plants.append({
                    "name": record["name"],
                    "scientific_name": record["scientific_name"],
                    "difficulty": record["difficulty"],
                    "light_requirement": record["light"],
                    "watering": record["watering"],
                    "description": record["description"]
                })
            
            return plants
    
    def get_family_info(self, family_name: str) -> Optional[Dict[str, Any]]:
        """
        获取科的信息及其下的植物
        
        Args:
            family_name: 科名
            
        Returns:
            科信息和植物列表
        """
        query = """
        MATCH (f:Family {name: $family_name})<-[:BELONGS_TO_FAMILY]-(p:Plant)
        OPTIONAL MATCH (f)-[:CONTAINS_GENUS]->(g:Genus)
        RETURN f.name AS family_name,
               collect(DISTINCT g.name) AS genera,
               collect(p.name) AS plants,
               count(p) AS plant_count
        """
        
        with self.neo4j_client.driver.session() as session:
            result = session.run(query, family_name=family_name)
            record = result.single()
            
            if record:
                return {
                    "family_name": record["family_name"],
                    "genera": record["genera"],
                    "plants": record["plants"],
                    "plant_count": record["plant_count"]
                }
        
        return None
    
    def _generate_disease_advice(self, disease_name: str, affected_plants: List[Dict]) -> str:
        """生成通用防治建议"""
        advice_parts = [f"针对{disease_name}的防治建议："]
        
        # 基于受影响植物的养护方式生成建议
        watering_tips = set()
        for plant in affected_plants:
            if plant.get('watering_advice'):
                watering_tips.add(plant['watering_advice'])
        
        if watering_tips:
            advice_parts.append(f"\n1. 浇水管理：{'；'.join(list(watering_tips)[:2])}")
        
        advice_parts.append("\n2. 环境改善：保持通风良好，避免过度潮湿")
        advice_parts.append("\n3. 及时处理：发现病叶及时剪除并销毁")
        advice_parts.append("\n4. 预防为主：定期检查植物健康状况")
        
        return "".join(advice_parts)
    
    def get_statistics(self) -> Dict[str, int]:
        """获取知识图谱统计信息"""
        queries = {
            'total_plants': "MATCH (p:Plant) RETURN count(p) as count",
            'total_families': "MATCH (f:Family) RETURN count(f) as count",
            'total_genera': "MATCH (g:Genus) RETURN count(g) as count",
            'total_diseases': "MATCH (d:Disease) RETURN count(d) as count",
            'total_pests': "MATCH (p:Pest) RETURN count(p) as count",
        }
        
        stats = {}
        with self.neo4j_client.driver.session() as session:
            for key, query in queries.items():
                result = session.run(query)
                record = result.single()
                stats[key] = record['count'] if record else 0
        
        return stats


# 单例实例
kg_service = KnowledgeGraphService()

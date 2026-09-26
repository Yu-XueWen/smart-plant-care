from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.api.models.recommend import PlantSpecies, RecommendationHistory
from app.api.services.knowledge_graph_service import KnowledgeGraphService
from app.utils.logger import setup_logger
from datetime import datetime
import re

logger = setup_logger("recommend_service")


class RecommendService:
    """植物推荐服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_recommendations(self, questionnaire: Dict[str, Any], user_id: int = None, top_n: int = 10) -> Dict[str, Any]:
        """
        根据问卷答案获取植物推荐
        
        Args:
            questionnaire: 问卷答案
            user_id: 用户ID（可选，用于保存历史）
            top_n: 返回的推荐数量
            
        Returns:
            推荐结果字典
        """
        # 初始化知识图谱服务
        kg_service = KnowledgeGraphService()
        
        # 从知识图谱获取所有植物数据
        all_plants_data = self._get_all_plants_from_kg(kg_service)
        
        if not all_plants_data:
            logger.error("知识图谱中没有植物数据")
            return {
                "recommendations": [],
                "questionnaire_summary": self._summarize_questionnaire(questionnaire),
                "total_matches": 0,
                "message": "暂无可推荐的植物数据"
            }
        
        logger.info(f"从知识图谱获取到 {len(all_plants_data)} 种植物")
        
        # 【关键改进】先根据问卷进行初步筛选，排除明显不匹配的植物
        filtered_plants = self._filter_plants_by_questionnaire(all_plants_data, questionnaire)
        logger.info(f"筛选后剩余 {len(filtered_plants)} 种植物符合基本条件")
        
        if not filtered_plants:
            logger.warning("没有植物符合问卷的基本条件，放宽筛选条件")
            # 如果筛选太严格，使用全部植物
            filtered_plants = all_plants_data
        
        # 计算每种植物的匹配分数
        scored_plants = []
        for plant_data in filtered_plants:
            score, reasons = self._calculate_match_score(plant_data, questionnaire)
            if score > 30:  # 提高阈值，只保留匹配度较高的植物（原为0）
                scored_plants.append({
                    "plant_data": plant_data,
                    "score": score,
                    "reasons": reasons
                })
        
        # 按分数降序排序
        scored_plants.sort(key=lambda x: x["score"], reverse=True)
        
        # 取前 top_n 个
        top_plants = scored_plants[:top_n]
        
        # 构建推荐结果
        recommendations = []
        for item in top_plants:
            plant_data = item["plant_data"]
            recommendation = self._build_recommendation_result(plant_data, item["score"], item["reasons"])
            recommendations.append(recommendation)
        
        # 保存推荐历史
        if user_id:
            self._save_recommendation_history(user_id, questionnaire, recommendations)
        
        return {
            "recommendations": recommendations,
            "questionnaire_summary": self._summarize_questionnaire(questionnaire),
            "total_matches": len(scored_plants)
        }

    def _filter_plants_by_questionnaire(self, plants_data: List[Dict], questionnaire: Dict[str, Any]) -> List[Dict]:
        """
        根据问卷答案筛选植物（硬性条件过滤）
        
        Args:
            plants_data: 所有植物数据
            questionnaire: 问卷答案
            
        Returns:
            筛选后的植物列表
        """
        filtered = []
        
        experience_level = questionnaire.get("experience_level", "beginner")
        light_condition = questionnaire.get("light_condition", "medium")
        space_size = questionnaire.get("space_size", "medium")
        time_availability = questionnaire.get("time_availability", "moderate")
        preferences = questionnaire.get("preferences", [])
        
        for plant_data in plants_data:
            # 1. 经验水平过滤：新手不推荐困难植物
            difficulty = plant_data.get("difficulty_level", "中等")
            difficulty_map = {
                "容易": "easy",
                "简单": "easy",
                "中等": "medium",
                "困难": "hard",
                "复杂": "hard"
            }
            mapped_difficulty = difficulty_map.get(difficulty, "medium")
            
            if experience_level == "beginner" and mapped_difficulty == "hard":
                continue  # 跳过困难植物
            
            # 2. 光照条件过滤：排除光照需求完全不匹配的
            plant_light = plant_data.get("light_requirement", "")
            mapped_light = self._map_light_requirement(plant_light)
            
            # 如果光照差距超过2级，直接排除
            light_levels = {"low": 1, "medium": 2, "high": 3, "full_sun": 4}
            plant_level = light_levels.get(mapped_light, 2)
            user_level = light_levels.get(light_condition, 2)
            
            if abs(plant_level - user_level) > 2:
                continue  # 光照完全不匹配
            
            # 3. 空间大小过滤：大空间植物不适合小空间
            growth_rate = plant_data.get("growth_rate", "")
            description = plant_data.get("description", "")
            plant_space = self._infer_space_requirement(growth_rate, description)
            
            space_levels = {"small": 1, "medium": 2, "large": 3}
            plant_space_level = space_levels.get(plant_space, 2)
            user_space_level = space_levels.get(space_size, 2)
            
            # 如果用户空间比植物需求小2级以上，排除
            if user_space_level < plant_space_level - 1:
                continue
            
            # 4. 时间可用性过滤：时间少的用户不适合需要频繁浇水的植物
            watering_info = plant_data.get("watering_management", "")
            water_freq = self._extract_watering_frequency(watering_info)
            
            freq_map = {
                "daily": 7,
                "every_2_days": 5,
                "weekly": 3,
                "biweekly": 2,
                "monthly": 1
            }
            time_map = {
                "little": 2,
                "moderate": 4,
                "much": 6
            }
            
            freq_score = freq_map.get(water_freq, 3)
            time_score = time_map.get(time_availability, 4)
            
            # 如果浇水频率远高于用户可用时间，排除
            if freq_score > time_score + 3:
                continue
            
            # 5. 偏好标签过滤：如果有明确偏好，至少满足一个
            if preferences:
                plant_tags = self._extract_plant_tags(plant_data)
                matching_tags = [tag for tag in preferences if tag in plant_tags]
                
                # 如果用户有偏好但植物完全不匹配，降低优先级但不完全排除
                # 这里我们保留，但在评分时会体现
            
            # 通过所有筛选条件
            filtered.append(plant_data)
        
        return filtered
    
    def _calculate_match_score(self, plant_data: Dict[str, Any], questionnaire: Dict[str, Any]) -> tuple:
        """
        计算植物与问卷的匹配分数
        
        Args:
            plant_data: 从知识图谱获取的植物数据
            questionnaire: 问卷答案
            
        Returns:
            (分数, 推荐理由列表)
        """
        score = 0.0
        reasons = []
        
        # 1. 经验水平匹配 (权重: 25分)
        experience_level = questionnaire.get("experience_level", "beginner")
        difficulty = plant_data.get("difficulty_level", "medium")
        
        # 将知识图谱的难度等级映射到推荐系统
        difficulty_map = {
            "容易": "easy",
            "简单": "easy",
            "中等": "medium",
            "困难": "hard",
            "复杂": "hard"
        }
        mapped_difficulty = difficulty_map.get(difficulty, "medium")
        
        if experience_level == "beginner":
            if mapped_difficulty == "easy":
                score += 25
                reasons.append("适合新手养护")
            elif mapped_difficulty == "medium":
                score += 10
                reasons.append("难度适中，需要一定学习")
        elif experience_level == "intermediate":
            if mapped_difficulty in ["easy", "medium"]:
                score += 25
                reasons.append("难度适中，有一定挑战性")
            else:
                score += 15
                reasons.append("需要较多养护经验")
        else:  # advanced
            score += 25
            reasons.append("满足专业养护需求")
        
        # 2. 光照条件匹配 (权重: 20分)
        light_condition = questionnaire.get("light_condition", "medium")
        plant_light = plant_data.get("light_requirement", "")
        
        # 解析光照需求
        mapped_light = self._map_light_requirement(plant_light)
        
        if mapped_light == light_condition:
            score += 20
            reasons.append(f"光照需求与您的环境匹配")
        elif self._is_light_compatible(mapped_light, light_condition):
            score += 15
            reasons.append("光照条件基本适配")
        
        # 3. 空间大小匹配 (权重: 15分)
        space_size = questionnaire.get("space_size", "medium")
        # 从描述或生长速度推断空间需求
        growth_rate = plant_data.get("growth_rate", "")
        description = plant_data.get("description", "")
        plant_space = self._infer_space_requirement(growth_rate, description)
        
        if plant_space == space_size:
            score += 15
            reasons.append("空间需求与您的环境匹配")
        elif self._is_space_compatible(plant_space, space_size):
            score += 10
            reasons.append("空间基本适配")
        
        # 4. 时间可用性匹配 (权重: 15分)
        time_availability = questionnaire.get("time_availability", "moderate")
        watering_info = plant_data.get("watering_management", "")
        water_freq = self._extract_watering_frequency(watering_info)
        
        if self._is_watering_compatible(water_freq, time_availability):
            score += 15
            reasons.append("浇水频率适合您的时间安排")
        
        # 5. 偏好标签匹配 (权重: 20分)
        preferences = questionnaire.get("preferences", [])
        if preferences:
            plant_tags = self._extract_plant_tags(plant_data)
            matching_tags = [tag for tag in preferences if tag in plant_tags]
            if matching_tags:
                tag_score = min(20, len(matching_tags) * 10)
                score += tag_score
                reasons.append(f"符合您的偏好：{', '.join(matching_tags[:2])}")
        
        # 6. 季节性因素加成 (权重: 5分)
        season_bonus = self._get_season_factor(plant_data)
        if season_bonus > 1.0:
            score *= season_bonus
            reasons.append("当前季节适合养护")
        
        # 确保分数不超过100
        score = min(100, round(score, 2))
        
        return score, reasons

    def _is_light_compatible(self, plant_light: str, user_light: str) -> bool:
        """检查光照兼容性"""
        light_levels = {"low": 1, "medium": 2, "high": 3, "full_sun": 4}
        plant_level = light_levels.get(plant_light, 2)
        user_level = light_levels.get(user_light, 2)
        return abs(plant_level - user_level) <= 1

    def _is_space_compatible(self, plant_space: str, user_space: str) -> bool:
        """检查空间兼容性"""
        space_levels = {"small": 1, "medium": 2, "large": 3}
        plant_level = space_levels.get(plant_space, 2)
        user_level = space_levels.get(user_space, 2)
        return user_level >= plant_level  # 用户空间可以大于植物需求

    def _is_watering_compatible(self, water_freq: str, time_avail: str) -> bool:
        """检查浇水频率与时间可用性是否匹配"""
        freq_map = {
            "daily": 7,
            "every_2_days": 5,
            "weekly": 3,
            "biweekly": 2,
            "monthly": 1
        }
        time_map = {
            "little": 2,
            "moderate": 4,
            "much": 6
        }
        
        freq_score = freq_map.get(water_freq, 3)
        time_score = time_map.get(time_avail, 4)
        
        return time_score >= freq_score

    def _summarize_questionnaire(self, questionnaire: Dict[str, Any]) -> Dict[str, str]:
        """生成问卷摘要"""
        level_map = {
            "beginner": "新手",
            "intermediate": "中级",
            "advanced": "高级"
        }
        light_map = {
            "low": "弱光",
            "medium": "中等光照",
            "high": "强光",
            "full_sun": "全日照"
        }
        space_map = {
            "small": "小空间",
            "medium": "中等空间",
            "large": "大空间"
        }
        time_map = {
            "little": "时间较少",
            "moderate": "时间适中",
            "much": "时间充足"
        }
        
        return {
            "experience_level": level_map.get(questionnaire.get("experience_level", ""), "未知"),
            "light_condition": light_map.get(questionnaire.get("light_condition", ""), "未知"),
            "space_size": space_map.get(questionnaire.get("space_size", ""), "未知"),
            "time_availability": time_map.get(questionnaire.get("time_availability", ""), "未知"),
            "preferences": ", ".join(questionnaire.get("preferences", [])) or "无特殊偏好"
        }

    def _save_recommendation_history(self, user_id: int, questionnaire: Dict[str, Any], recommendations: List[Dict]):
        """保存推荐历史"""
        try:
            history = RecommendationHistory(
                user_id=user_id,
                questionnaire_data=questionnaire,
                recommended_plants=[{
                    "plant_name": r["plant_name"],
                    "match_score": r["match_score"]
                } for r in recommendations]
            )
            self.db.add(history)
            self.db.commit()
            logger.info(f"已保存用户 {user_id} 的推荐历史")
        except Exception as e:
            logger.error(f"保存推荐历史失败: {e}")
            self.db.rollback()

    def _get_all_plants_from_kg(self, kg_service: KnowledgeGraphService) -> List[Dict[str, Any]]:
        """
        从知识图谱获取所有植物数据
        
        Args:
            kg_service: 知识图谱服务实例
            
        Returns:
            植物数据列表
        """
        try:
            # 使用搜索功能获取所有植物
            # 这里我们不带任何条件，获取所有植物
            query = """
            MATCH (p:Plant)
            RETURN p.name AS name,
                   p.name_en AS name_en,
                   p.scientific_name AS scientific_name,
                   p.difficulty_level AS difficulty_level,
                   p.light_requirement AS light_requirement,
                   p.watering_management AS watering_management,
                   p.temperature_range AS temperature_range,
                   p.humidity_requirement AS humidity_requirement,
                   p.soil_type AS soil_type,
                   p.fertilization_plan AS fertilization_plan,
                   p.pruning_guide AS pruning_guide,
                   p.propagation_methods AS propagation_methods,
                   p.growth_rate AS growth_rate,
                   p.description AS description
            LIMIT 100
            """
            
            with kg_service.neo4j_client.driver.session() as session:
                result = session.run(query)
                plants = []
                
                for record in result:
                    plant_data = {
                        "name": record["name"],
                        "name_en": record["name_en"],
                        "scientific_name": record["scientific_name"],
                        "difficulty_level": record["difficulty_level"],
                        "light_requirement": record["light_requirement"],
                        "watering_management": record["watering_management"],
                        "temperature_range": record["temperature_range"],
                        "humidity_requirement": record["humidity_requirement"],
                        "soil_type": record["soil_type"],
                        "fertilization_plan": record["fertilization_plan"],
                        "pruning_guide": record["pruning_guide"],
                        "propagation_methods": record["propagation_methods"],
                        "growth_rate": record["growth_rate"],
                        "description": record["description"]
                    }
                    plants.append(plant_data)
                
                return plants
        except Exception as e:
            logger.error(f"从知识图谱获取植物数据失败: {e}", exc_info=True)
            return []
    
    def _build_recommendation_result(self, plant_data: Dict[str, Any], score: float, reasons: List[str]) -> Dict[str, Any]:
        """
        构建推荐结果
        
        Args:
            plant_data: 植物数据
            score: 匹配分数
            reasons: 推荐理由
            
        Returns:
            推荐结果字典
        """
        # 提取养护信息
        watering_freq = self._extract_watering_frequency(plant_data.get("watering_management", ""))
        temp_range = plant_data.get("temperature_range", "15°C - 30°C")
        humidity_range = plant_data.get("humidity_requirement", "40% - 70%")
        
        # 提取标签
        tags = self._extract_plant_tags(plant_data)
        
        # 生成养护技巧
        care_tips = self._generate_care_tips(plant_data)
        
        return {
            "plant_name": plant_data.get("name", "未知植物"),
            "scientific_name": plant_data.get("scientific_name"),
            "family": None,  # 知识图谱中暂未包含科属信息
            "match_score": score,
            "reasons": reasons,
            "care_difficulty": plant_data.get("difficulty_level", "中等"),
            "light_requirement": plant_data.get("light_requirement", "中等光照"),
            "water_frequency": watering_freq,
            "temperature_range": temp_range,
            "humidity_range": humidity_range,
            "tags": tags,
            "benefits": [],  # 可以从描述中提取
            "description": plant_data.get("description", ""),
            "care_tips": care_tips,
            "image_url": None,  # 知识图谱中暂未包含图片
            "popularity_score": 50.0  # 默认值
        }
    
    def _map_light_requirement(self, light_str: str) -> str:
        """
        将知识图谱的光照描述映射到标准等级
        
        Args:
            light_str: 光照描述字符串
            
        Returns:
            标准光照等级: low/medium/high/full_sun
        """
        if not light_str:
            return "medium"
        
        light_lower = light_str.lower()
        
        if any(keyword in light_lower for keyword in ["弱光", "阴", "shade", "low"]):
            return "low"
        elif any(keyword in light_lower for keyword in ["强光", "全日照", "sun", "bright"]):
            return "full_sun"
        elif any(keyword in light_lower for keyword in ["充足", "明亮", "high"]):
            return "high"
        else:
            return "medium"
    
    def _infer_space_requirement(self, growth_rate: str, description: str) -> str:
        """
        根据生长速度和描述推断空间需求
        
        Returns:
            small/medium/large
        """
        text = f"{growth_rate} {description}".lower()
        
        if any(keyword in text for keyword in ["小型", "迷你", "桌面", "small", "mini"]):
            return "small"
        elif any(keyword in text for keyword in ["大型", "高大", "庭院", "large", "big"]):
            return "large"
        else:
            return "medium"
    
    def _extract_watering_frequency(self, watering_info: str) -> str:
        """
        从浇水管理描述中提取浇水频率
        
        Returns:
            daily/every_2_days/weekly/biweekly/monthly
        """
        if not watering_info:
            return "weekly"
        
        watering_lower = watering_info.lower()
        
        if any(keyword in watering_lower for keyword in ["每天", "每日", "daily"]):
            return "daily"
        elif any(keyword in watering_lower for keyword in ["2天", "两天", "every 2"]):
            return "every_2_days"
        elif any(keyword in watering_lower for keyword in ["周", "week", "每周"]):
            return "weekly"
        elif any(keyword in watering_lower for keyword in ["半月", "双周", "biweek"]):
            return "biweekly"
        elif any(keyword in watering_lower for keyword in ["月", "month", "每月"]):
            return "monthly"
        else:
            return "weekly"
    
    def _extract_plant_tags(self, plant_data: Dict[str, Any]) -> List[str]:
        """
        从植物数据中提取标签
        
        Returns:
            标签列表
        """
        tags = []
        description = plant_data.get("description", "").lower()
        growth_rate = plant_data.get("growth_rate", "").lower()
        
        # 根据描述和特性添加标签
        if any(keyword in description for keyword in ["开花", "花", "flower"]):
            tags.append("开花")
        
        if any(keyword in description for keyword in ["观叶", "叶", "leaf", " foliage"]):
            tags.append("观叶")
        
        if any(keyword in description for keyword in ["多肉", "succulent"]):
            tags.append("多肉")
        
        if any(keyword in description for keyword in ["净化空气", "空气", "air", "purify"]):
            tags.append("空气净化")
        
        if any(keyword in description for keyword in ["香", "fragrant", "aromatic"]):
            tags.append("芳香")
        
        if any(keyword in description for keyword in ["耐阴", "阴", "shade"]):
            tags.append("耐阴")
        
        if any(keyword in description for keyword in ["耐旱", "旱", "drought"]):
            tags.append("耐旱")
        
        if any(keyword in description for keyword in ["悬挂", "吊", "hanging"]):
            tags.append("悬挂")
        
        if any(keyword in description for keyword in ["水培", "water"]):
            tags.append("水培")
        
        return tags
    
    def _generate_care_tips(self, plant_data: Dict[str, Any]) -> str:
        """
        生成养护技巧
        
        Returns:
            养护技巧文本
        """
        tips = []
        
        # 光照建议
        light = plant_data.get("light_requirement", "")
        if light:
            tips.append(f"光照：{light}")
        
        # 浇水建议
        watering = plant_data.get("watering_management", "")
        if watering:
            tips.append(f"浇水：{watering}")
        
        # 温度建议
        temp = plant_data.get("temperature_range", "")
        if temp:
            tips.append(f"温度：{temp}")
        
        # 施肥建议
        fertilizer = plant_data.get("fertilization_plan", "")
        if fertilizer:
            tips.append(f"施肥：{fertilizer}")
        
        return "；".join(tips) if tips else "保持适宜的生长环境"
    
    def _get_season_factor(self, plant_data: Dict[str, Any]) -> float:
        """
        根据当前季节调整推荐分数
        
        Returns:
            季节因子（1.0-1.2）
        """
        current_month = datetime.now().month
        description = plant_data.get("description", "").lower()
        
        # 春季(3-5月): 适合开花植物、播种
        if 3 <= current_month <= 5:
            if any(keyword in description for keyword in ["开花", "春", "spring", "flower"]):
                return 1.2
        
        # 夏季(6-8月): 适合耐热植物
        elif 6 <= current_month <= 8:
            temp_range = plant_data.get("temperature_range", "")
            if "30" in temp_range or "35" in temp_range:
                return 1.15
        
        # 秋季(9-11月): 适合观叶植物
        elif 9 <= current_month <= 11:
            if "观叶" in description or "leaf" in description:
                return 1.1
        
        # 冬季(12-2月): 适合耐寒植物
        else:
            temp_range = plant_data.get("temperature_range", "")
            if "5" in temp_range or "10" in temp_range or "耐寒" in description:
                return 1.15
        
        return 1.0

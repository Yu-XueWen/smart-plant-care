# backend/app/services/ai_service.py
import os
import cv2
import json
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from ultralytics import YOLO

# 修复：正确导入 settings
from app.api.core.config import settings
from app.api.services.knowledge_graph_service import kg_service

logger = logging.getLogger(__name__)


class AIService:
    """AI模型服务类，封装YOLO模型的加载和推理"""

    def __init__(self):
        self.plant_detector = None  # 植物主体检测模型
        self.plant_classifier = None  # 植物分类模型
        self.disease_detector = None  # 病害检测模型
        self.flower_name_mapping = {}  # 英文名称到中文名称的映射
        self.disease_name_mapping = {}  # 病害英文名称到中文名称的映射
        self._load_flower_name_mapping()
        self._load_disease_name_mapping()
        self._init_models()

    def _load_flower_name_mapping(self):
        """加载花卉名称映射文件"""
        try:
            mapping_file = Path(__file__).parent / "flower_name_mapping.json"
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self.flower_name_mapping = json.load(f)
                logger.info(f"✓ 花卉名称映射文件加载成功，共 {len(self.flower_name_mapping)} 条")
            else:
                logger.warning(f"花卉名称映射文件不存在: {mapping_file}")
        except Exception as e:
            logger.error(f"加载花卉名称映射文件失败: {e}")
    
    def _load_disease_name_mapping(self):
        """加载病害名称映射文件"""
        try:
            # disease_name_mapping.json 在 backend 目录下
            mapping_file = Path(__file__).parent.parent.parent.parent / "disease_name_mapping.json"
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self.disease_name_mapping = json.load(f)
                logger.info(f"✓ 病害名称映射文件加载成功，共 {len(self.disease_name_mapping)} 条")
            else:
                logger.warning(f"病害名称映射文件不存在: {mapping_file}")
        except Exception as e:
            logger.error(f"加载病害名称映射文件失败: {e}")
    
    def _translate_disease_name(self, english_name: str) -> str:
        """将病害英文名称转换为中文名称"""
        # 直接匹配
        if english_name in self.disease_name_mapping:
            return self.disease_name_mapping[english_name]
        
        # 如果没有找到映射，返回原名称（可能是健康状态）
        return english_name

    def _translate_to_chinese(self, english_name: str) -> str:
        """将英文名称转换为中文名称"""
        # 先尝试直接匹配
        if english_name in self.flower_name_mapping:
            return self.flower_name_mapping[english_name]
        
        # 尝试小写匹配
        lower_name = english_name.lower().strip()
        if lower_name in self.flower_name_mapping:
            return self.flower_name_mapping[lower_name]
        
        # 如果没有找到映射，返回原名称
        return english_name

    def _init_models(self):
        """初始化AI模型"""
        try:
            # 植物主体检测（使用YOLO预训练模型）
            model_path = Path(__file__).parent.parent.parent.parent.parent / "yolov8n.pt"
            if model_path.exists():
                self.plant_detector = YOLO(str(model_path))
                logger.info("植物主体检测模型加载成功")
            else:
                logger.warning(f"植物主体检测模型不存在: {model_path}")
                self.plant_detector = None
        except Exception as e:
            logger.warning(f"植物主体检测模型加载失败: {e}")
            self.plant_detector = None

        try:
            # 植物分类模型
            if settings.plant_classify_model:
                model_path = Path(settings.plant_classify_model)
                # 如果是相对路径，基于 backend 目录转换
                if not model_path.is_absolute():
                    backend_dir = Path(__file__).parent.parent.parent.parent
                    model_path = backend_dir / settings.plant_classify_model
                if model_path.exists():
                    self.plant_classifier = YOLO(str(model_path))
                    logger.info(f"植物分类模型加载成功: {model_path}")
                else:
                    logger.warning(f"植物分类模型不存在: {model_path}")
                    self.plant_classifier = None
            else:
                self.plant_classifier = None
        except Exception as e:
            logger.warning(f"植物分类模型加载失败: {e}")
            self.plant_classifier = None

        try:
            # 病害检测模型
            if settings.disease_model:
                model_path = Path(settings.disease_model)
                # 如果是相对路径，基于 backend 目录转换
                if not model_path.is_absolute():
                    backend_dir = Path(__file__).parent.parent.parent.parent
                    model_path = backend_dir / settings.disease_model
                if model_path.exists():
                    self.disease_detector = YOLO(str(model_path))
                    logger.info(f"病害检测模型加载成功: {model_path}")
                else:
                    logger.warning(f"病害检测模型不存在: {model_path}")
                    self.disease_detector = None
            else:
                self.disease_detector = None
        except Exception as e:
            logger.warning(f"病害检测模型加载失败: {e}")
            self.disease_detector = None

    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """加载图片"""
        try:
            if image_path.startswith('/uploads/'):
                # 从本地文件加载
                if hasattr(settings, 'upload_dir'):
                    local_path = Path(settings.upload_dir) / Path(image_path).name
                    img = cv2.imread(str(local_path))
                else:
                    img = cv2.imread(image_path)
            else:
                img = cv2.imread(image_path)

            if img is None:
                logger.error(f"无法加载图片: {image_path}")
                return None
            return img
        except Exception as e:
            logger.error(f"加载图片失败: {e}")
            return None

    async def detect_plant(self, image_url: str) -> Dict[str, Any]:
        """植物主体检测"""
        img = self._load_image(image_url)
        if img is None:
            return {"detections": [], "processing_time_ms": 0, "original_size": [0, 0]}

        height, width = img.shape[:2]

        if self.plant_detector is None:
            return {
                "detections": [{
                    "bbox": [0, 0, width, height],
                    "confidence": 1.0,
                    "class": "plant",
                    "cropped_image_url": image_url
                }],
                "processing_time_ms": 0,
                "original_size": [width, height]
            }

        results = self.plant_detector(img, classes=[58, 59])
        detections = []

        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = "plant" if cls in [58, 59] else "unknown"

                    detections.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
                        "class": class_name,
                        "cropped_image_url": None
                    })

        return {
            "detections": detections,
            "processing_time_ms": results[0].speed.get('inference', 0) if results else 0,
            "original_size": [width, height]
        }

    async def identify_plant(self, image_url: str) -> Dict[str, Any]:
        """植物识别"""
        img = self._load_image(image_url)

        if self.plant_classifier is None:
            return self._get_mock_identify_result()

        results = self.plant_classifier(img)

        if results and results[0].probs is not None:
            probs = results[0].probs
            top5_idx = probs.top5
            top5_conf = probs.top5conf.tolist()

            top5_results = []
            for idx, conf in zip(top5_idx, top5_conf):
                plant_name = self.plant_classifier.names[idx]
                logger.info(f"模型识别结果: ID={idx}, 英文名称={plant_name}, 置信度={conf}")
                
                # 将英文名称转换为中文名称
                chinese_name = self._translate_to_chinese(plant_name)
                logger.info(f"转换后的中文名称: {chinese_name}")
                
                # 尝试从知识图谱获取详细信息（使用中文名称）
                kg_info = self._get_plant_details_from_kg(chinese_name)
                if kg_info:
                    logger.info(f"✓ 从知识图谱获取到 [{chinese_name}] 的详细信息")
                else:
                    logger.warning(f"✗ 知识图谱中未找到 [{chinese_name}] 的信息")
                
                plant_info = {
                    "plant_name": chinese_name,  # 使用中文名称
                    "scientific_name": kg_info.get("scientific_name", self._get_scientific_name(plant_name)),
                    "confidence": float(conf),
                    "species_id": f"plant_{plant_name.lower().replace(' ', '_')}"
                }
                
                # 如果有知识图谱信息，添加详细信息
                if kg_info:
                    plant_info.update(kg_info)
                else:
                    # 否则使用基础养护指南
                    plant_info["care_guide"] = self._get_care_guide(chinese_name)
                
                top5_results.append(plant_info)

            top1 = top5_results[0] if top5_results else None

            return {
                "top1": top1,
                "top5": top5_results
            }

        return self._get_mock_identify_result()

    async def diagnose_disease(self, image_url: str) -> Dict[str, Any]:
        """病害诊断"""
        logger.info(f"开始病害诊断，图片URL: {image_url}")
        img = self._load_image(image_url)
        
        if img is None:
            logger.error("无法加载图片")
            return self._get_error_diagnose_result("图片加载失败，请重新上传清晰的叶片照片")

        if self.disease_detector is None:
            logger.warning("病害检测模型未加载")
            return self._get_error_diagnose_result("病害检测服务暂时不可用，请稍后重试")

        try:
            logger.info("开始模型推理...")
            # 降低置信度阈值到0.1，以检测更多的目标
            results = self.disease_detector(img, conf=0.1, verbose=False)
            
            logger.info(f"模型推理完成，结果数量: {len(results)}")

            if results and results[0].boxes is not None:
                boxes = results[0].boxes
                logger.info(f"检测到 {len(boxes)} 个目标")
                
                if len(boxes) > 0:
                    # 输出所有检测结果供调试
                    for i, box in enumerate(boxes):
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name_en = self.disease_detector.names[cls_id]
                        class_name_cn = self._translate_disease_name(class_name_en)
                        logger.info(f"  检测结果[{i}]: {class_name_en} -> {class_name_cn}, 置信度={conf:.4f}")
                    
                    # 使用置信度最高的结果
                    top_box = boxes[0]
                    disease_id = int(top_box.cls[0])
                    confidence = float(top_box.conf[0])
                    disease_name_en = self.disease_detector.names[disease_id]
                    
                    logger.info(f"选择最高置信度结果: ID={disease_id}, 英文名={disease_name_en}, 置信度={confidence}")
                    
                    # 转换为中文名称
                    disease_name_cn = self._translate_disease_name(disease_name_en)
                    logger.info(f"最终诊断结果: {disease_name_cn}, 置信度={confidence:.2%}")
                    
                    # 如果置信度低于40%，认为叶片健康
                    if confidence < 0.4:
                        logger.info(f"置信度{confidence:.2%}低于40%，判定为健康叶片")
                        return self._get_healthy_result(confidence)

                    return {
                        "primary_disease": disease_name_cn,
                        "confidence": confidence,
                        "symptoms": self._get_disease_symptoms(disease_name_cn),
                        "treatment": self._get_treatment_plan(disease_name_cn)
                    }
                else:
                    logger.warning("⚠️  未检测到任何病害目标")
                    return self._get_no_detection_result()
            else:
                logger.warning("模型返回结果为空或boxes为None")
                return self._get_error_diagnose_result("模型分析失败，请尝试重新上传")
        except Exception as e:
            logger.error(f"病害诊断过程出错: {e}", exc_info=True)
            return self._get_error_diagnose_result(f"诊断过程出现错误: {str(e)}")

    # ========== 辅助方法 ==========

    def _get_plant_details_from_kg(self, plant_name: str) -> Dict[str, Any]:
        """从知识图谱获取植物详细信息"""
        try:
            # 获取养护指南
            kg_care = kg_service.get_plant_care_guide(plant_name)
            if not kg_care:
                return {}
            
            # 获取病虫害信息
            diseases_pests = kg_service.get_plant_diseases_and_pests(plant_name)
            
            # 构建完整的植物信息
            plant_details = {
                # 基本信息
                "scientific_name": kg_care.get("scientific_name", ""),
                "description": kg_care.get("description", ""),
                
                # 养护难度和特性
                "difficulty_level": kg_care.get("difficulty_level", ""),
                "growth_rate": kg_care.get("growth_rate", ""),
                
                # 环境要求
                "care_guide": {
                    "light_requirement": kg_care.get("light_requirement", "明亮散射光"),
                    "temperature_range": kg_care.get("temperature_range", "15-25°C"),
                    "humidity_requirement": kg_care.get("humidity_requirement", "中等湿度"),
                    "soil_type": kg_care.get("soil_type", "排水良好的土壤"),
                    "water_frequency": kg_care.get("watering_management", "保持土壤湿润"),
                    "fertilization": kg_care.get("fertilization_plan", "每月1次"),
                    "pruning_guide": kg_care.get("pruning_guide", "根据生长情况修剪"),
                    "propagation_methods": kg_care.get("propagation_methods", "扦插或播种")
                },
                
                # 病虫害信息
                "common_diseases": diseases_pests.get("diseases", []),
                "common_pests": diseases_pests.get("pests", [])
            }
            
            return plant_details
            
        except Exception as e:
            logger.warning(f"从知识图谱获取植物详情失败 [{plant_name}]: {e}")
            return {}

    def _get_scientific_name(self, plant_name: str) -> str:
        """获取植物学名"""
        names = {
            "月季": "Rosa chinensis",
            "玫瑰": "Rosa rugosa",
            "番茄": "Solanum lycopersicum",
            "辣椒": "Capsicum annuum",
        }
        return names.get(plant_name, "")

    def _get_care_guide(self, plant_name: str) -> Dict[str, str]:
        """获取养护指南（优先从知识图谱获取）"""
        # 首先尝试从知识图谱获取
        try:
            kg_care = kg_service.get_plant_care_guide(plant_name)
            if kg_care:
                return {
                    "water_frequency": kg_care.get("watering_management", "保持土壤湿润"),
                    "light_requirement": kg_care.get("light_requirement", "明亮散射光"),
                    "fertilization": kg_care.get("fertilization_plan", "每月1次"),
                    "soil_requirement": kg_care.get("soil_type", "排水良好的土壤"),
                    "temperature_requirement": kg_care.get("temperature_range", "15-25°C")
                }
        except Exception as e:
            logger.warning(f"从知识图谱获取养护指南失败: {e}")
        
        # 如果知识图谱没有，使用硬编码数据
        guides = {
            "月季": {
                "water_frequency": "每周2-3次",
                "light_requirement": "全日照",
                "fertilization": "生长期每月1次",
                "soil_requirement": "疏松肥沃的微酸性土壤",
                "temperature_requirement": "15-25°C"
            },
            "番茄": {
                "water_frequency": "每天1次（夏季）",
                "light_requirement": "充足阳光",
                "fertilization": "每2周1次",
                "soil_requirement": "排水良好的土壤",
                "temperature_requirement": "20-28°C"
            }
        }
        return guides.get(plant_name, {
            "water_frequency": "保持土壤湿润",
            "light_requirement": "明亮散射光",
            "fertilization": "每月1次"
        })

    def _get_disease_symptoms(self, disease_name: str) -> str:
        """获取病害症状描述"""
        symptoms = {
            "黑斑病": "叶片出现圆形黑色病斑，边缘呈放射状，严重时叶片变黄脱落",
            "白粉病": "叶片表面出现白色粉末状霉层，叶片卷曲变形",
            "早疫病": "叶片出现褐色同心轮纹病斑，边缘有黄色晕圈",
            "晚疫病": "叶片出现水浸状暗绿色病斑，后变为褐色，湿度大时产生白色霉层",
            "炭疽病": "叶片出现椭圆形或不规则形褐色病斑，中央灰白色，边缘深褐色",
            "叶斑病": "叶片出现不规则形褐色斑点，逐渐扩大融合，导致叶片枯死",
            "锈病": "叶片背面出现橙黄色或红褐色粉状孢子堆，正面出现褪绿斑点",
            "灰霉病": "花器、果实和叶片出现灰色霉层，组织软化腐烂",
            "霜霉病": "叶片正面出现黄色多角形病斑，背面产生白色霜状霉层",
            "根腐病": "根部变褐腐烂，植株萎蔫，生长缓慢，严重时整株死亡",
            "病毒病": "叶片出现花叶、畸形、矮化等症状，颜色不均匀"
        }
        return symptoms.get(disease_name, "叶片出现异常斑点或变色")

    def _get_treatment_plan(self, disease_name: str) -> Dict[str, str]:
        """获取防治方案"""
        plans = {
            "黑斑病": {
                "chemical": "喷洒代森锰锌可湿性粉剂，稀释800-1000倍，每7-10天一次",
                "organic": "剪除病叶，改善通风，避免叶面喷水",
                "prevention": "选择抗病品种，保持植株间距，定期喷药预防"
            },
            "白粉病": {
                "chemical": "喷洒三唑酮或戊唑醇，稀释1500-2000倍",
                "organic": "使用硫磺粉喷洒，或用小苏打溶液（1%浓度）",
                "prevention": "保持通风，避免氮肥过量，及时清除病叶"
            },
            "早疫病": {
                "chemical": "喷洒百菌清或多菌灵，稀释600-800倍，每7天一次",
                "organic": "轮作种植，清除病残体，增施磷钾肥",
                "prevention": "选用无病种子，合理密植，控制温湿度"
            },
            "晚疫病": {
                "chemical": "喷洒甲霜灵或烯酰吗啉，稀释1000-1500倍",
                "organic": "及时排水，降低湿度，清除病株",
                "prevention": "选择抗病品种，避免连作，加强田间管理"
            },
            "炭疽病": {
                "chemical": "喷洒咪鲜胺或苯醚甲环唑，稀释1500-2000倍",
                "organic": "剪除病枝病叶，改善通风透光条件",
                "prevention": "加强肥水管理，增强植株抗性，及时清理果园"
            },
            "叶斑病": {
                "chemical": "喷洒甲基托布津或多菌灵，稀释800-1000倍",
                "organic": "清除落叶，减少病原，合理施肥",
                "prevention": "选择抗病品种，保持适当密度，避免过度浇水"
            },
            "锈病": {
                "chemical": "喷洒粉锈宁或腈菌唑，稀释1500-2000倍",
                "organic": "清除转主寄主，修剪过密枝条",
                "prevention": "选用抗病品种，早春喷药预防，加强栽培管理"
            },
            "灰霉病": {
                "chemical": "喷洒嘧霉胺或异菌脲，稀释1000-1500倍",
                "organic": "降低湿度，及时清除病花病果",
                "prevention": "控制温湿度，加强通风，避免伤口感染"
            },
            "霜霉病": {
                "chemical": "喷洒霜脲氰或烯酰吗啉，稀释1000-1500倍",
                "organic": "改善通风，降低湿度，清除病叶",
                "prevention": "选择抗病品种，合理密植，避免低温高湿"
            },
            "根腐病": {
                "chemical": "灌根恶霉灵或咯菌腈，稀释800-1000倍",
                "organic": "改善土壤排水，移除病株，晒土消毒",
                "prevention": "选择排水良好的土壤，避免积水，合理浇水"
            },
            "病毒病": {
                "chemical": "无特效药剂，可喷洒病毒A或盐酸吗啉胍缓解症状",
                "organic": "及时拔除病株，防止传播，控制蚜虫等传毒媒介",
                "prevention": "选用无毒种苗，防虫网隔离，工具消毒"
            }
        }
        return plans.get(disease_name, {
            "chemical": "建议咨询专业园艺师",
            "organic": "剪除病叶，改善养护环境",
            "prevention": "保持通风，合理浇水施肥"
        })

    def _get_healthy_result(self, confidence: float = 0.0) -> Dict[str, Any]:
        """返回健康叶片的结果"""
        return {
            "primary_disease": "叶片健康",
            "confidence": round(confidence, 4) if confidence > 0 else 0.95,
            "symptoms": "叶片状态良好，未发现明显病害症状。继续保持当前的养护方式即可。",
            "treatment": {
                "chemical": "无需用药",
                "organic": "继续保持良好的养护习惯",
                "prevention": "定期观察叶片状态，注意通风和适当浇水"
            },
            "is_healthy": True
        }
    
    def _get_no_detection_result(self) -> Dict[str, Any]:
        """未检测到病害时的友好提示"""
        return {
            "primary_disease": "未检测到明显病害",
            "confidence": 0.0,
            "symptoms": "系统未在图片中检测到明显的病害症状。这可能是以下原因：\n1. 叶片确实健康\n2. 病害症状不明显\n3. 拍摄角度或光线影响识别",
            "treatment": {
                "chemical": "暂不需要用药",
                "organic": "建议继续观察，如出现新症状可重新拍照诊断",
                "prevention": "保持良好的养护环境，定期检查植株状态"
            },
            "suggestions": [
                "确保拍摄清晰的叶片特写",
                "在充足光线下拍摄，避免阴影",
                "对焦在病害症状最明显的区域",
                "可以尝试从不同角度拍摄"
            ],
            "is_healthy": True
        }
    
    def _get_error_diagnose_result(self, error_message: str = "诊断失败") -> Dict[str, Any]:
        """返回错误提示"""
        return {
            "primary_disease": "诊断失败",
            "confidence": 0.0,
            "symptoms": f"{error_message}",
            "treatment": {
                "chemical": "",
                "organic": "请重新上传清晰的叶片照片进行诊断",
                "prevention": "确保图片清晰、光线充足、病害症状明显"
            },
            "error": True,
            "suggestions": [
                "使用相机模式拍摄，确保清晰度",
                "在自然光下拍摄，避免强光直射",
                "拍摄叶片正面和背面",
                "确保病害症状在图片中清晰可见"
            ]
        }
    
    def _get_mock_identify_result(self) -> Dict[str, Any]:
        """模拟识别结果"""
        return {
            "top1": {
                "plant_name": "月季",
                "scientific_name": "Rosa chinensis",
                "confidence": 0.89,
                "species_id": "plant_rose_001",
                "care_guide": self._get_care_guide("月季")
            },
            "top5": [
                {"plant_name": "月季", "scientific_name": "Rosa chinensis", "confidence": 0.89},
                {"plant_name": "玫瑰", "scientific_name": "Rosa rugosa", "confidence": 0.07},
                {"plant_name": "蔷薇", "scientific_name": "Rosa multiflora", "confidence": 0.03},
            ]
        }


# 单例实例
ai_service = AIService()
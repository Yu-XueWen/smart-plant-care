"""
管理员知识库管理端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import datetime

from app.api.core.database import get_db
from app.api.models.user import User
from app.api.v1.dependencies.auth import get_current_admin
from app.utils.response_utils import ResponseModel

router = APIRouter()

# 模拟知识库存储
_knowledge_base = {
    "plants": [
        {
            "id": 1,
            "name": "绿萝",
            "scientific_name": "Epipremnum aureum",
            "family": "天南星科",
            "care_level": "easy",
            "light_requirement": "散射光",
            "water_requirement": "保持土壤湿润",
            "temperature_range": "18-28°C",
            "humidity_range": "60-80%",
            "description": "绿萝是常见的室内观叶植物，耐阴耐旱，适合新手养护。",
            "image_url": "/static/images/plants/pothos.jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
        {
            "id": 2,
            "name": "吊兰",
            "scientific_name": "Chlorophytum comosum",
            "family": "阿福花科",
            "care_level": "easy",
            "light_requirement": "明亮散射光",
            "water_requirement": "见干见湿",
            "temperature_range": "15-25°C",
            "humidity_range": "50-70%",
            "description": "吊兰是经典的室内悬挂植物，净化空气能力强。",
            "image_url": "/static/images/plants/spider-plant.jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
    ],
    "diseases": [
        {
            "id": 1,
            "name": "叶斑病",
            "scientific_name": "Leaf Spot",
            "pathogen": "真菌感染",
            "symptoms": "叶片出现褐色或黑色斑点，边缘模糊",
            "affected_plants": ["绿萝", "吊兰", "龟背竹"],
            "treatment": "切除病叶，喷洒多菌灵溶液",
            "prevention": "保持通风，避免叶片积水",
            "severity": "moderate",
            "image_url": "/static/images/diseases/leaf-spot.jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
        {
            "id": 2,
            "name": "根腐病",
            "scientific_name": "Root Rot",
            "pathogen": "真菌感染",
            "symptoms": "根部变黑腐烂，叶片发黄萎蔫",
            "affected_plants": ["绿萝", "吊兰", "发财树"],
            "treatment": "切除腐烂根部，更换新土，喷洒杀菌剂",
            "prevention": "控制浇水，确保土壤排水良好",
            "severity": "severe",
            "image_url": "/static/images/diseases/root-rot.jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
    ],
    "care_tips": [
        {
            "id": 1,
            "title": "浇水技巧",
            "category": "watering",
            "content": "大多数室内植物喜欢'见干见湿'的浇水方式，即土壤表面干燥后再浇水。",
            "image_url": "/static/images/tips/watering.jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
        {
            "id": 2,
            "title": "施肥指南",
            "category": "fertilizing",
            "content": "生长季节每2周施一次稀释的液肥，冬季停止施肥。",
            "image_url": "/static/images/tips/fertilizing.jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
    ]
}

_next_id = 10


class KnowledgeItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


@router.get("/plants", response_model=ResponseModel)
def get_plant_knowledge(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取植物知识库列表"""
    items = _knowledge_base["plants"]
    
    if search:
        items = [item for item in items if search.lower() in item["name"].lower() or 
                 search.lower() in item.get("description", "").lower()]
    
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated_items
    })


@router.get("/plants/{plant_id}", response_model=ResponseModel)
def get_plant_knowledge_detail(
    plant_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取植物知识库详情"""
    plant = next((p for p in _knowledge_base["plants"] if p["id"] == plant_id), None)
    if not plant:
        raise HTTPException(status_code=404, detail="植物知识不存在")
    
    return ResponseModel(data=plant)


@router.post("/plants", response_model=ResponseModel)
def create_plant_knowledge(
    plant_data: dict,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建植物知识"""
    global _next_id
    
    new_item = {
        "id": _next_id,
        "name": plant_data.get("name"),
        "scientific_name": plant_data.get("scientific_name"),
        "family": plant_data.get("family"),
        "care_level": plant_data.get("care_level", "easy"),
        "light_requirement": plant_data.get("light_requirement"),
        "water_requirement": plant_data.get("water_requirement"),
        "temperature_range": plant_data.get("temperature_range"),
        "humidity_range": plant_data.get("humidity_range"),
        "description": plant_data.get("description"),
        "image_url": plant_data.get("image_url"),
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
    }
    
    _knowledge_base["plants"].append(new_item)
    _next_id += 1
    
    return ResponseModel(data=new_item, message="植物知识创建成功")


@router.put("/plants/{plant_id}", response_model=ResponseModel)
def update_plant_knowledge(
    plant_id: int,
    plant_data: dict,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新植物知识"""
    plant = next((p for p in _knowledge_base["plants"] if p["id"] == plant_id), None)
    if not plant:
        raise HTTPException(status_code=404, detail="植物知识不存在")
    
    # 更新字段
    for key in ["name", "scientific_name", "family", "care_level", 
                "light_requirement", "water_requirement", "temperature_range",
                "humidity_range", "description", "image_url"]:
        if key in plant_data:
            plant[key] = plant_data[key]
    
    plant["updated_at"] = datetime.datetime.now().isoformat()
    
    return ResponseModel(data=plant, message="植物知识更新成功")


@router.delete("/plants/{plant_id}", response_model=ResponseModel)
def delete_plant_knowledge(
    plant_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除植物知识"""
    plant = next((p for p in _knowledge_base["plants"] if p["id"] == plant_id), None)
    if not plant:
        raise HTTPException(status_code=404, detail="植物知识不存在")
    
    _knowledge_base["plants"] = [p for p in _knowledge_base["plants"] if p["id"] != plant_id]
    
    return ResponseModel(message="植物知识删除成功")


@router.get("/diseases", response_model=ResponseModel)
def get_disease_knowledge(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取病害知识库列表"""
    items = _knowledge_base["diseases"]
    
    if search:
        items = [item for item in items if search.lower() in item["name"].lower() or 
                 search.lower() in item.get("symptoms", "").lower()]
    
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated_items
    })


@router.get("/diseases/{disease_id}", response_model=ResponseModel)
def get_disease_knowledge_detail(
    disease_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取病害知识库详情"""
    disease = next((d for d in _knowledge_base["diseases"] if d["id"] == disease_id), None)
    if not disease:
        raise HTTPException(status_code=404, detail="病害知识不存在")
    
    return ResponseModel(data=disease)


@router.post("/diseases", response_model=ResponseModel)
def create_disease_knowledge(
    disease_data: dict,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建病害知识"""
    global _next_id
    
    new_item = {
        "id": _next_id,
        "name": disease_data.get("name"),
        "scientific_name": disease_data.get("scientific_name"),
        "pathogen": disease_data.get("pathogen"),
        "symptoms": disease_data.get("symptoms"),
        "affected_plants": disease_data.get("affected_plants", []),
        "treatment": disease_data.get("treatment"),
        "prevention": disease_data.get("prevention"),
        "severity": disease_data.get("severity", "moderate"),
        "image_url": disease_data.get("image_url"),
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
    }
    
    _knowledge_base["diseases"].append(new_item)
    _next_id += 1
    
    return ResponseModel(data=new_item, message="病害知识创建成功")


@router.put("/diseases/{disease_id}", response_model=ResponseModel)
def update_disease_knowledge(
    disease_id: int,
    disease_data: dict,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新病害知识"""
    disease = next((d for d in _knowledge_base["diseases"] if d["id"] == disease_id), None)
    if not disease:
        raise HTTPException(status_code=404, detail="病害知识不存在")
    
    # 更新字段
    for key in ["name", "scientific_name", "pathogen", "symptoms", 
                "affected_plants", "treatment", "prevention", "severity", "image_url"]:
        if key in disease_data:
            disease[key] = disease_data[key]
    
    disease["updated_at"] = datetime.datetime.now().isoformat()
    
    return ResponseModel(data=disease, message="病害知识更新成功")


@router.delete("/diseases/{disease_id}", response_model=ResponseModel)
def delete_disease_knowledge(
    disease_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除病害知识"""
    disease = next((d for d in _knowledge_base["diseases"] if d["id"] == disease_id), None)
    if not disease:
        raise HTTPException(status_code=404, detail="病害知识不存在")
    
    _knowledge_base["diseases"] = [d for d in _knowledge_base["diseases"] if d["id"] != disease_id]
    
    return ResponseModel(message="病害知识删除成功")


@router.get("/care-tips", response_model=ResponseModel)
def get_care_tips(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取养护技巧列表"""
    items = _knowledge_base["care_tips"]
    
    if category:
        items = [item for item in items if item.get("category") == category]
    
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = items[start:end]
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated_items
    })


@router.get("/care-tips/{tip_id}", response_model=ResponseModel)
def get_care_tip_detail(
    tip_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取养护技巧详情"""
    tip = next((t for t in _knowledge_base["care_tips"] if t["id"] == tip_id), None)
    if not tip:
        raise HTTPException(status_code=404, detail="养护技巧不存在")
    
    return ResponseModel(data=tip)


@router.post("/care-tips", response_model=ResponseModel)
def create_care_tip(
    tip_data: dict,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建养护技巧"""
    global _next_id
    
    new_item = {
        "id": _next_id,
        "title": tip_data.get("title"),
        "category": tip_data.get("category", "general"),
        "content": tip_data.get("content"),
        "image_url": tip_data.get("image_url"),
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
    }
    
    _knowledge_base["care_tips"].append(new_item)
    _next_id += 1
    
    return ResponseModel(data=new_item, message="养护技巧创建成功")


@router.put("/care-tips/{tip_id}", response_model=ResponseModel)
def update_care_tip(
    tip_id: int,
    tip_data: dict,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新养护技巧"""
    tip = next((t for t in _knowledge_base["care_tips"] if t["id"] == tip_id), None)
    if not tip:
        raise HTTPException(status_code=404, detail="养护技巧不存在")
    
    # 更新字段
    for key in ["title", "category", "content", "image_url"]:
        if key in tip_data:
            tip[key] = tip_data[key]
    
    tip["updated_at"] = datetime.datetime.now().isoformat()
    
    return ResponseModel(data=tip, message="养护技巧更新成功")


@router.delete("/care-tips/{tip_id}", response_model=ResponseModel)
def delete_care_tip(
    tip_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除养护技巧"""
    tip = next((t for t in _knowledge_base["care_tips"] if t["id"] == tip_id), None)
    if not tip:
        raise HTTPException(status_code=404, detail="养护技巧不存在")
    
    _knowledge_base["care_tips"] = [t for t in _knowledge_base["care_tips"] if t["id"] != tip_id]
    
    return ResponseModel(message="养护技巧删除成功")


@router.get("/stats", response_model=ResponseModel)
def get_knowledge_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取知识库统计"""
    return ResponseModel(data={
        "plants": len(_knowledge_base["plants"]),
        "diseases": len(_knowledge_base["diseases"]),
        "care_tips": len(_knowledge_base["care_tips"]),
        "total": len(_knowledge_base["plants"]) + len(_knowledge_base["diseases"]) + len(_knowledge_base["care_tips"])
    })

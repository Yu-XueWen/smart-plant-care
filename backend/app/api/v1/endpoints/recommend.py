from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.core.database import get_db
from app.api.core.deps import get_current_user
from app.api.models.user import User
from app.api.schemas.recommend import (
    QuestionnaireRequest,
    RecommendationResponse,
    PlantSpeciesCreate,
    PlantSpeciesUpdate,
    PlantSpeciesResponse
)
from app.api.services.recommend_service import RecommendService
from app.utils.response_utils import ResponseModel
from app.api.models.recommend import PlantSpecies

router = APIRouter()


@router.post("/recommend", response_model=ResponseModel)
def get_plant_recommendations(
        questionnaire: QuestionnaireRequest,
        top_n: int = Query(0, ge=0, le=200, description="返回的推荐数量，0表示返回全部"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    根据问卷答案获取植物推荐
    
    用户填写养护偏好问卷后，系统会综合分析并推荐最适合的植物
    top_n=0 时返回所有符合条件的植物，否则返回指定数量（最大200）
    """
    try:
        service = RecommendService(db)
        
        # 如果top_n为0，设置为一个很大的值以返回所有结果
        actual_top_n = top_n if top_n > 0 else 200
        
        # 获取推荐结果
        result = service.get_recommendations(
            questionnaire=questionnaire.dict(),
            user_id=current_user.id,
            top_n=actual_top_n
        )
        
        return ResponseModel(
            code=200,
            message="推荐成功",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


# ========== 管理员接口：植物物种管理 ==========

@router.get("/species", response_model=ResponseModel)
def list_plant_species(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        difficulty: Optional[str] = Query(None, description="筛选难度"),
        light: Optional[str] = Query(None, description="筛选光照"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取植物物种列表（管理员）"""
    # 检查管理员权限
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    query = db.query(PlantSpecies)
    
    if difficulty:
        query = query.filter(PlantSpecies.care_difficulty == difficulty)
    if light:
        query = query.filter(PlantSpecies.light_requirement == light)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ResponseModel(data={
        "total": total,
        "items": [PlantSpeciesResponse.from_orm(item) for item in items]
    })


@router.post("/species", response_model=ResponseModel)
def create_plant_species(
        species_data: PlantSpeciesCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """创建植物物种（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 检查是否已存在
    existing = db.query(PlantSpecies).filter(
        PlantSpecies.plant_name == species_data.plant_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该植物已存在")
    
    new_species = PlantSpecies(**species_data.dict())
    db.add(new_species)
    db.commit()
    db.refresh(new_species)
    
    return ResponseModel(
        code=200,
        message="创建成功",
        data={"id": new_species.id}
    )


@router.put("/species/{species_id}", response_model=ResponseModel)
def update_plant_species(
        species_id: int,
        species_data: PlantSpeciesUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新植物物种（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    species = db.query(PlantSpecies).filter(PlantSpecies.id == species_id).first()
    if not species:
        raise HTTPException(status_code=404, detail="植物物种不存在")
    
    update_data = species_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(species, key, value)
    
    db.commit()
    db.refresh(species)
    
    return ResponseModel(message="更新成功")


@router.delete("/species/{species_id}", response_model=ResponseModel)
def delete_plant_species(
        species_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """删除植物物种（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    species = db.query(PlantSpecies).filter(PlantSpecies.id == species_id).first()
    if not species:
        raise HTTPException(status_code=404, detail="植物物种不存在")
    
    db.delete(species)
    db.commit()
    
    return ResponseModel(message="删除成功")


@router.get("/species/{species_id}", response_model=ResponseModel)
def get_plant_species_detail(
        species_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取植物物种详情"""
    species = db.query(PlantSpecies).filter(PlantSpecies.id == species_id).first()
    if not species:
        raise HTTPException(status_code=404, detail="植物物种不存在")
    
    return ResponseModel(data=PlantSpeciesResponse.from_orm(species))

# backend/app/api/v1/endpoints/plants.py
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, datetime
from typing import Optional
import uuid
import shutil
import logging
from pathlib import Path
from app.api.core.database import get_db
from app.api.core.config import settings
from app.api.v1.dependencies.auth import get_current_user
from app.api.models.user import User
from app.api.models.plant import UserPlant, WateringRecord, TreatmentRecord
from app.api.schemas.plant import (
    PlantCreate, PlantUpdate, PlantResponse,
    WateringCreate, WateringResponse,
    TreatmentCreate, TreatmentResponse
)
from app.api.schemas.common import ResponseModel
from app.api.services.knowledge_graph_service import kg_service

logger = logging.getLogger(__name__)

router = APIRouter()

# 上传目录
UPLOAD_DIR = Path(settings.upload_dir) / "plants"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ========== 植物档案管理 ==========

@router.get("", response_model=ResponseModel)
def get_plants(
        status: Optional[int] = Query(1, description="状态:1正常,0已移除"),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    query = db.query(UserPlant).filter(
        UserPlant.user_id == current_user.id,
        UserPlant.status == status
    )

    total = query.count()
    items = query.order_by(desc(UserPlant.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    # 优化：批量查询所有植物的浇水和给药记录，避免 N+1 问题
    if items:
        plant_ids = [p.id for p in items]
        
        # 批量查询浇水记录
        watering_records = db.query(WateringRecord).filter(
            WateringRecord.user_plant_id.in_(plant_ids)
        ).order_by(desc(WateringRecord.watering_date)).all()
        
        # 批量查询给药记录
        treatment_records = db.query(TreatmentRecord).filter(
            TreatmentRecord.user_plant_id.in_(plant_ids),
            TreatmentRecord.treatment_type == "pesticide"
        ).order_by(desc(TreatmentRecord.application_date)).all()
        
        # 按植物ID分组
        from collections import defaultdict
        water_by_plant = defaultdict(list)
        for w in watering_records:
            water_by_plant[w.user_plant_id].append(w)
        
        treatment_by_plant = defaultdict(list)
        for t in treatment_records:
            treatment_by_plant[t.user_plant_id].append(t)
    
    # 获取每个植物的最近浇水日期和给药日期
    result_items = []
    for plant in items:
        last_water = water_by_plant.get(plant.id, [None])[0] if items else None
        last_treatment = treatment_by_plant.get(plant.id, [None])[0] if items else None

        result_items.append({
            "id": plant.id,
            "nickname": plant.nickname,
            "plant_name": plant.plant_name,
            "species_id": plant.species_id,
            "planting_date": plant.planting_date.isoformat() if plant.planting_date else None,
            "source": plant.source,
            "status": plant.status,
            "initial_photos": plant.initial_photos,
            "last_water_date": last_water.watering_date.isoformat() if last_water else None,
            "last_treatment_date": last_treatment.application_date.isoformat() if last_treatment else None,
            "created_at": plant.created_at.isoformat()
        })

    return ResponseModel(data={"total": total, "items": result_items})


@router.post("", response_model=ResponseModel)
def create_plant(
        plant_data: PlantCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    new_plant = UserPlant(
        user_id=current_user.id,
        plant_name=plant_data.plant_name,
        species_id=plant_data.species_id,
        nickname=plant_data.nickname,
        planting_date=plant_data.planting_date,
        source=plant_data.source,
        initial_photos=plant_data.initial_photos,
        notes=plant_data.notes,
        status=1
    )
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)
    
    # 自动创建浇水提醒（基于知识图谱的季节性浇水频率）
    try:
        from app.api.services.watering_reminder_service import WateringReminderService
        reminder_service = WateringReminderService()
        reminder_info = reminder_service.create_or_update_watering_reminder(
            db=db,
            user_id=current_user.id,
            plant_id=new_plant.id,
            last_watering_date=plant_data.planting_date,  # 使用种植日期作为基准
            current_date=date.today()
        )
        logger.info(f"为新植物 {new_plant.plant_name} 创建浇水提醒成功: {reminder_info}")
    except Exception as e:
        logger.warning(f"为新植物 {new_plant.plant_name} 创建浇水提醒失败: {e}")
        # 即使创建提醒失败，也不影响植物添加

    return ResponseModel(
        code=200,
        message="添加成功",
        data={"id": new_plant.id}
    )


@router.get("/{plant_id}", response_model=ResponseModel)
def get_plant_detail(
        plant_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")

    # 获取浇水记录
    watering_records = db.query(WateringRecord).filter(
        WateringRecord.user_plant_id == plant_id
    ).order_by(desc(WateringRecord.watering_date)).limit(20).all()

    # 获取养护记录
    treatment_records = db.query(TreatmentRecord).filter(
        TreatmentRecord.user_plant_id == plant_id
    ).order_by(desc(TreatmentRecord.application_date)).limit(20).all()

    return ResponseModel(data={
        "id": plant.id,
        "plant_name": plant.plant_name,
        "species_id": plant.species_id,
        "nickname": plant.nickname,
        "planting_date": plant.planting_date.isoformat() if plant.planting_date else None,
        "source": plant.source,
        "status": plant.status,
        "notes": plant.notes,
        "initial_photos": plant.initial_photos,
        "watering_records": [
            {"id": r.id, "date": r.watering_date.isoformat(), "amount": r.water_amount, "notes": r.notes}
            for r in watering_records
        ],
        "treatment_records": [
            {"id": r.id, "type": r.treatment_type, "product": r.product_name,
             "dosage": r.dosage, "date": r.application_date.isoformat(), "notes": r.notes}
            for r in treatment_records
        ]
    })


@router.put("/{plant_id}", response_model=ResponseModel)
def update_plant(
        plant_id: int,
        plant_data: PlantUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")

    update_data = plant_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plant, key, value)

    plant.updated_at = datetime.now()
    db.commit()

    return ResponseModel(message="更新成功")


@router.delete("/{plant_id}", response_model=ResponseModel)
def delete_plant(
        plant_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")

    plant.status = 0
    plant.updated_at = datetime.now()
    db.commit()

    return ResponseModel(message="删除成功")


# ========== 浇水记录 ==========

@router.post("/{plant_id}/watering", response_model=ResponseModel)
def add_watering(
        plant_id: int,
        watering_data: WateringCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 验证植物属于当前用户
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")

    record = WateringRecord(
        user_plant_id=plant_id,
        watering_date=watering_data.watering_date,
        water_amount=watering_data.water_amount,
        notes=watering_data.notes,
        created_at=datetime.now()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ResponseModel(data={"record_id": record.id})


@router.get("/{plant_id}/watering", response_model=ResponseModel)
def get_watering_history(
        plant_id: int,
        limit: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")

    records = db.query(WateringRecord).filter(
        WateringRecord.user_plant_id == plant_id
    ).order_by(desc(WateringRecord.watering_date)).limit(limit).all()

    total = db.query(WateringRecord).filter(WateringRecord.user_plant_id == plant_id).count()

    return ResponseModel(data={
        "total": total,
        "items": [
            {"id": r.id, "date": r.watering_date.isoformat(), "amount": r.water_amount, "notes": r.notes}
            for r in records
        ]
    })


@router.post("/{plant_id}/quick-water", response_model=ResponseModel)
def quick_water_single_plant(
        plant_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    快速浇水单个盆栽
    - 记录今日浇水
    - 自动更新下次浇水日期
    """
    from app.api.services.watering_reminder_service import WateringReminderService
    
    logger.info(f"收到快速浇水请求: plant_id={plant_id}, user_id={current_user.id}")
    
    try:
        # 验证植物属于当前用户
        plant = db.query(UserPlant).filter(
            UserPlant.id == plant_id,
            UserPlant.user_id == current_user.id
        ).first()
        if not plant:
            logger.error(f"植物不存在: plant_id={plant_id}")
            raise HTTPException(status_code=404, detail="植物档案不存在")
        
        logger.info(f"找到植物: {plant.plant_name} (nickname: {plant.nickname})")
        
        today = date.today()
        logger.info(f"浇水日期: {today}")
        
        # 创建浇水记录
        record = WateringRecord(
            user_plant_id=plant_id,
            watering_date=today,
            notes="快速浇水"
        )
        db.add(record)
        logger.info(f"已添加浇水记录到会话")
        
        # 更新下次浇水提醒
        reminder_service = WateringReminderService()
        try:
            reminder_info = reminder_service.create_or_update_watering_reminder(
                db=db,
                user_id=current_user.id,
                plant_id=plant_id,
                last_watering_date=today,
                current_date=today
            )
            logger.info(f"浇水提醒更新成功: {reminder_info}")
        except Exception as e:
            # 即使提醒更新失败，也要保存浇水记录
            logger.warning(f"更新浇水提醒失败: {e}", exc_info=True)
            reminder_info = None
        
        db.commit()
        db.refresh(record)
        
        logger.info(f"浇水记录已提交到数据库，record_id={record.id}")
        
        return ResponseModel(
            code=200,
            message="浇水成功",
            data={
                "record_id": record.id,
                "watering_date": today.isoformat(),
                "next_watering_date": reminder_info["scheduled_date"] if reminder_info else None,
                "interval_days": reminder_info["interval_days"] if reminder_info else None
            }
        )
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"快速浇水失败: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"浇水失败: {str(e)}")


@router.post("/batch-quick-water", response_model=ResponseModel)
def batch_quick_water_all_plants(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    一键浇水所有盆栽
    - 为所有正常状态的盆栽记录今日浇水
    - 自动更新每个盆栽的下次浇水日期
    """
    from app.api.services.watering_reminder_service import WateringReminderService
    
    today = date.today()
    
    # 获取用户所有正常状态的盆栽
    plants = db.query(UserPlant).filter(
        UserPlant.user_id == current_user.id,
        UserPlant.status == 1
    ).all()
    
    if not plants:
        return ResponseModel(
            code=200,
            message="暂无盆栽",
            data={"success_count": 0, "failed_count": 0, "details": []}
        )
    
    reminder_service = WateringReminderService()
    success_count = 0
    failed_count = 0
    details = []
    
    for plant in plants:
        try:
            # 创建浇水记录
            record = WateringRecord(
                user_plant_id=plant.id,
                watering_date=today,
                notes="一键浇水"
            )
            db.add(record)
            
            # 更新下次浇水提醒
            try:
                reminder_info = reminder_service.create_or_update_watering_reminder(
                    db=db,
                    user_id=current_user.id,
                    plant_id=plant.id,
                    last_watering_date=today,
                    current_date=today
                )
                details.append({
                    "plant_id": plant.id,
                    "plant_name": plant.plant_name,
                    "nickname": plant.nickname,
                    "status": "success",
                    "next_watering_date": reminder_info["scheduled_date"],
                    "interval_days": reminder_info["interval_days"]
                })
            except Exception as e:
                logger.warning(f"更新植物 {plant.plant_name} 的浇水提醒失败: {e}")
                details.append({
                    "plant_id": plant.id,
                    "plant_name": plant.plant_name,
                    "nickname": plant.nickname,
                    "status": "partial_success",
                    "message": f"浇水记录已保存，但提醒更新失败: {str(e)}"
                })
            
            success_count += 1
        except Exception as e:
            failed_count += 1
            details.append({
                "plant_id": plant.id,
                "plant_name": plant.plant_name,
                "nickname": plant.nickname,
                "status": "failed",
                "message": str(e)
            })
    
    db.commit()
    
    return ResponseModel(
        code=200,
        message=f"浇水完成：成功{success_count}盆，失败{failed_count}盆",
        data={
            "success_count": success_count,
            "failed_count": failed_count,
            "total": len(plants),
            "details": details
        }
    )


# ========== 养护记录 ==========

@router.post("/{plant_id}/treatment", response_model=ResponseModel)
def add_treatment(
        plant_id: int,
        treatment_data: TreatmentCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")

    record = TreatmentRecord(
        user_plant_id=plant_id,
        treatment_type=treatment_data.treatment_type,
        product_name=treatment_data.product_name,
        dosage=treatment_data.dosage,
        application_date=treatment_data.application_date,
        notes=treatment_data.notes,
        created_at=datetime.now()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ResponseModel(data={"record_id": record.id})


@router.get("/{plant_id}/treatments", response_model=ResponseModel)
def get_treatment_history(
        plant_id: int,
        treatment_type: Optional[str] = Query(None, description="筛选类型"),
        limit: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")

    query = db.query(TreatmentRecord).filter(TreatmentRecord.user_plant_id == plant_id)
    if treatment_type:
        query = query.filter(TreatmentRecord.treatment_type == treatment_type)

    records = query.order_by(desc(TreatmentRecord.application_date)).limit(limit).all()
    total = query.count()

    return ResponseModel(data={
        "total": total,
        "items": [
            {"id": r.id, "type": r.treatment_type, "product_name": r.product_name,
             "dosage": r.dosage, "date": r.application_date.isoformat(), "notes": r.notes}
            for r in records
        ]
    })


# ========== 图片上传 ==========

@router.post("/upload/image", response_model=ResponseModel)
async def upload_plant_image(
    file: UploadFile = File(..., description="上传的图片文件"),
    current_user: User = Depends(get_current_user)
):
    """上传盆栽图片"""
    # 打印调试信息
    print(f"收到上传请求:")
    print(f"  文件名: {file.filename}")
    print(f"  内容类型: {file.content_type}")
    print(f"  用户: {current_user.username}")
    
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"只支持 JPG、PNG、GIF、WEBP 格式的图片，当前类型: {file.content_type}")
    
    # 验证文件大小（5MB）
    max_size = 5 * 1024 * 1024
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置到文件开头
    
    print(f"  文件大小: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
    
    if file_size > max_size:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")
    
    # 生成唯一文件名
    ext = Path(file.filename).suffix if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename
    
    print(f"  保存路径: {file_path}")
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"  ✓ 文件保存成功")
    except Exception as e:
        print(f"  ✗ 文件保存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")
    
    # 返回URL
    image_url = f"/uploads/plants/{filename}"
    
    return ResponseModel(
        code=200,
        message="上传成功",
        data={"url": image_url}
    )


# ========== 知识图谱查询接口 ==========

@router.get("/kg/search", response_model=ResponseModel)
def search_plant_from_kg(
        plant_name: str = Query(..., description="植物名称"),
        current_user: User = Depends(get_current_user)
):
    """
    从知识图谱查询植物详细信息
    用于添加盆栽时自动填充物种信息
    """
    try:
        # 查询植物养护指南
        care_guide = kg_service.get_plant_care_guide(plant_name)
        
        if not care_guide:
            return ResponseModel(
                code=404,
                message=f"未找到植物 '{plant_name}' 的信息",
                data=None
            )
        
        # 查询病虫害信息
        diseases_and_pests = kg_service.get_plant_diseases_and_pests(plant_name)
        
        # 组合返回数据
        result = {
            "plant_name": care_guide.get("plant_name"),
            "scientific_name": care_guide.get("scientific_name"),
            "light_requirement": care_guide.get("light_requirement"),
            "temperature_range": care_guide.get("temperature_range"),
            "humidity_requirement": care_guide.get("humidity_requirement"),
            "soil_type": care_guide.get("soil_type"),
            "watering_management": care_guide.get("watering_management"),
            "fertilization_plan": care_guide.get("fertilization_plan"),
            "pruning_guide": care_guide.get("pruning_guide"),
            "propagation_methods": care_guide.get("propagation_methods"),
            "difficulty_level": care_guide.get("difficulty_level"),
            "growth_rate": care_guide.get("growth_rate"),
            "description": care_guide.get("description"),
            "common_diseases": diseases_and_pests.get("diseases", []),
            "common_pests": diseases_and_pests.get("pests", [])
        }
        
        return ResponseModel(
            code=200,
            message="查询成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/{plant_id}/kg-info", response_model=ResponseModel)
def get_plant_kg_info(
        plant_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    获取盆栽的知识图谱详细信息
    用于盆栽详情页展示
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 验证植物归属
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")
    
    try:
        # 清洗植物名称：去除前后空格
        clean_name = plant.plant_name.strip()
        logger.info(f"查询植物知识图谱: '{clean_name}' (原始: '{plant.plant_name}', 物种ID: '{plant.species_id}')")
        
        # 尝试多种查询方式
        care_guide = None
        query_name = None
        
        # 方式1: 优先使用 species_id（学名）查询
        if plant.species_id and plant.species_id.strip():
            query_name = plant.species_id.strip()
            logger.info(f"尝试使用物种ID(学名)查询: '{query_name}'")
            care_guide = kg_service.get_plant_care_guide(query_name)
        
        # 方式2: 如果学名查询失败，尝试使用植物中文名
        if not care_guide:
            query_name = clean_name
            logger.info(f"尝试使用植物中文名查询: '{query_name}'")
            care_guide = kg_service.get_plant_care_guide(query_name)
        
        if not care_guide:
            logger.warning(f"未找到植物 '{clean_name}' 的知识图谱信息 (尝试了: species_id='{plant.species_id}', plant_name='{clean_name}')")
            return ResponseModel(
                code=200,
                message=f"知识图谱中暂无「{clean_name}」的详细信息",
                data={"plant_name": clean_name, "has_kg_info": False}
            )
        
        # 查询病虫害信息（使用与养护指南相同的查询名称）
        diseases_and_pests = kg_service.get_plant_diseases_and_pests(query_name)
        
        # 查询相似植物
        similar_plants = kg_service.find_similar_plants(query_name, limit=3)
        
        result = {
            "plant_name": clean_name,
            "has_kg_info": True,
            "care_guide": care_guide,
            "common_diseases": diseases_and_pests.get("diseases", []),
            "common_pests": diseases_and_pests.get("pests", []),
            "similar_plants": similar_plants
        }
        
        logger.info(f"成功获取植物 '{clean_name}' 的知识图谱信息")
        return ResponseModel(
            code=200,
            message="查询成功",
            data=result
        )
    except Exception as e:
        import traceback
        logger.error(f"查询知识图谱失败: {str(e)}")
        logger.error(traceback.format_exc())
        # 不抛出异常，返回友好提示
        return ResponseModel(
            code=200,
            message=f"查询失败: {str(e)}",
            data={"plant_name": plant.plant_name, "has_kg_info": False, "error": str(e)}
        )
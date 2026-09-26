# backend/app/api/v1/endpoints/ai.py
import os
import uuid
import shutil
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.api.core.config import settings
from app.api.models.user import User
from app.api.models.history import IdentifyHistory, DiagnoseHistory
from app.api.schemas.common import ResponseModel
from app.api.services.ai_service import ai_service

router = APIRouter()

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
# 最大文件大小 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


def save_upload_file(file: UploadFile) -> str:
    """保存上传的文件，返回文件URL"""
    # 验证文件类型
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}，允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 验证文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    size = file.file.tell()
    file.file.seek(0)  # 重置指针
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）"
        )
    
    # 生成安全文件名（使用 UUID 防止路径遍历）
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/uploads/{filename}"


@router.post("/identify", response_model=ResponseModel)
async def identify_plant(
        image: UploadFile = File(...),
        save_history: bool = Form(True),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """植物识别（看图识花）"""
    # 保存图片
    image_url = save_upload_file(image)

    # 调用AI服务识别
    try:
        result = await ai_service.identify_plant(image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")

    # 保存历史记录
    history_id = None
    if save_history:
        history = IdentifyHistory(
            user_id=current_user.id,
            image_url=image_url,
            plant_name=result["top1"]["plant_name"],
            confidence=result["top1"]["confidence"],
            result_detail=result,
            created_at=datetime.now()
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        history_id = history.id

    return ResponseModel(data={
        **result,
        "history_id": history_id,
        "image_url": image_url
    })


@router.post("/diagnose", response_model=ResponseModel)
async def diagnose_disease(
        image: UploadFile = File(...),
        plant_id: int = Form(None, description="关联的植物档案ID"),
        save_history: bool = Form(True),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """病害诊断（症状诊断）"""
    # 保存图片
    image_url = save_upload_file(image)

    # 调用AI服务诊断
    try:
        result = await ai_service.diagnose_disease(image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断失败: {str(e)}")

    # 保存历史记录
    history_id = None
    if save_history:
        history = DiagnoseHistory(
            user_id=current_user.id,
            image_url=image_url,
            disease_name=result["primary_disease"],
            confidence=result["confidence"],
            symptoms=result["symptoms"],
            treatment=result["treatment"],
            created_at=datetime.now()
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        history_id = history.id

    return ResponseModel(data={
        **result,
        "history_id": history_id,
        "image_url": image_url
    })


@router.post("/detect-plant", response_model=ResponseModel)
async def detect_plant(
        image: UploadFile = File(...),
        current_user: User = Depends(get_current_user)
):
    """植物主体检测（预处理）"""
    image_url = save_upload_file(image)

    try:
        result = await ai_service.detect_plant(image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

    return ResponseModel(data=result)


@router.post("/save-to-plant", response_model=ResponseModel)
def save_to_plant(
        history_type: str,
        history_id: int,
        plant_id: int,
        action: str = None,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """将识别/诊断结果保存到植物档案"""
    # 验证植物属于当前用户
    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()
    if not plant:
        raise HTTPException(status_code=404, detail="植物档案不存在")

    if history_type == "identify":
        history = db.query(IdentifyHistory).filter(
            IdentifyHistory.id == history_id,
            IdentifyHistory.user_id == current_user.id
        ).first()
        if not history:
            raise HTTPException(status_code=404, detail="识别记录不存在")

        # 更新植物名称
        plant.plant_name = history.plant_name
        plant.species_id = history.result_detail.get("top1", {}).get("species_id")

    elif history_type == "diagnose":
        history = db.query(DiagnoseHistory).filter(
            DiagnoseHistory.id == history_id,
            DiagnoseHistory.user_id == current_user.id
        ).first()
        if not history:
            raise HTTPException(status_code=404, detail="诊断记录不存在")

        # 可选：创建提醒
        if action == "create_reminder":
            from app.models.reminder import RemindConfig
            reminder = RemindConfig(
                user_id=current_user.id,
                user_plant_id=plant_id,
                remind_type="pesticide",
                frequency_type="one_time",
                scheduled_date=datetime.now().date(),
                custom_message=f"建议对{plant.nickname or plant.plant_name}进行{history.disease_name}防治",
                is_enabled=True,
                created_at=datetime.now()
            )
            db.add(reminder)

    plant.updated_at = datetime.now()
    db.commit()

    return ResponseModel(message="保存成功")
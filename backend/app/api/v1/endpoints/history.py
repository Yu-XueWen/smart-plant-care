# backend/app/api/v1/endpoints/history.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.core.database import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.api.models.user import User
from app.api.models.history import IdentifyHistory, DiagnoseHistory
from app.api.schemas.common import ResponseModel

router = APIRouter()


@router.get("/identify", response_model=ResponseModel)
def get_identify_history(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=50),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取识花历史记录"""
    query = db.query(IdentifyHistory).filter(IdentifyHistory.user_id == current_user.id)
    total = query.count()

    items = query.order_by(desc(IdentifyHistory.created_at)) \
        .offset((page - 1) * page_size).limit(page_size).all()

    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": h.id,
                "image_url": h.image_url,
                "plant_name": h.plant_name,
                "confidence": float(h.confidence) if h.confidence else None,
                "created_at": h.created_at.isoformat()
            }
            for h in items
        ]
    })


@router.get("/diagnose", response_model=ResponseModel)
def get_diagnose_history(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=50),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取诊断历史记录"""
    query = db.query(DiagnoseHistory).filter(DiagnoseHistory.user_id == current_user.id)
    total = query.count()

    items = query.order_by(desc(DiagnoseHistory.created_at)) \
        .offset((page - 1) * page_size).limit(page_size).all()

    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": h.id,
                "image_url": h.image_url,
                "disease_name": h.disease_name,
                "confidence": float(h.confidence) if h.confidence else None,
                "created_at": h.created_at.isoformat()
            }
            for h in items
        ]
    })


@router.get("/{history_type}/{history_id}", response_model=ResponseModel)
def get_history_detail(
        history_type: str,
        history_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取单条历史详情"""
    if history_type == "identify":
        history = db.query(IdentifyHistory).filter(
            IdentifyHistory.id == history_id,
            IdentifyHistory.user_id == current_user.id
        ).first()
        if not history:
            raise HTTPException(status_code=404, detail="识别记录不存在")

        return ResponseModel(data={
            "type": "identify",
            "id": history.id,
            "image_url": history.image_url,
            "plant_name": history.plant_name,
            "confidence": float(history.confidence) if history.confidence else None,
            "result_detail": history.result_detail,
            "created_at": history.created_at.isoformat()
        })

    elif history_type == "diagnose":
        history = db.query(DiagnoseHistory).filter(
            DiagnoseHistory.id == history_id,
            DiagnoseHistory.user_id == current_user.id
        ).first()
        if not history:
            raise HTTPException(status_code=404, detail="诊断记录不存在")

        return ResponseModel(data={
            "type": "diagnose",
            "id": history.id,
            "image_url": history.image_url,
            "disease_name": history.disease_name,
            "confidence": float(history.confidence) if history.confidence else None,
            "symptoms": history.symptoms,
            "treatment": history.treatment,
            "created_at": history.created_at.isoformat()
        })

    else:
        raise HTTPException(status_code=400, detail="无效的历史类型")


@router.delete("/{history_type}/{history_id}", response_model=ResponseModel)
def delete_history(
        history_type: str,
        history_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """删除历史记录"""
    if history_type == "identify":
        history = db.query(IdentifyHistory).filter(
            IdentifyHistory.id == history_id,
            IdentifyHistory.user_id == current_user.id
        ).first()
    elif history_type == "diagnose":
        history = db.query(DiagnoseHistory).filter(
            DiagnoseHistory.id == history_id,
            DiagnoseHistory.user_id == current_user.id
        ).first()
    else:
        raise HTTPException(status_code=400, detail="无效的历史类型")

    if not history:
        raise HTTPException(status_code=404, detail="记录不存在")

    db.delete(history)
    db.commit()

    return ResponseModel(message="删除成功")
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.sql import func
from app.api.core.database import Base

class IdentifyHistory(Base):
    __tablename__ = "identify_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    plant_name = Column(String(100), nullable=False)
    confidence = Column(Float)
    result_detail = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class DiagnoseHistory(Base):
    __tablename__ = "diagnose_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    disease_name = Column(String(100), nullable=False)
    confidence = Column(Float)
    symptoms = Column(Text)
    treatment = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
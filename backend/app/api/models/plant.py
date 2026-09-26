from sqlalchemy import Column, Integer, String, Date, DateTime, Text, SmallInteger, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from app.api.core.database import Base

class UserPlant(Base):
    __tablename__ = "user_plant"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    plant_name = Column(String(100), nullable=False)
    species_id = Column(String(50))
    nickname = Column(String(50))
    planting_date = Column(Date)
    source = Column(String(50))
    initial_photos = Column(JSON)
    status = Column(SmallInteger, default=1)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class WateringRecord(Base):
    __tablename__ = "watering_record"

    id = Column(Integer, primary_key=True, index=True)
    user_plant_id = Column(Integer, ForeignKey("user_plant.id", ondelete="CASCADE"), nullable=False)
    watering_date = Column(Date, nullable=False)
    water_amount = Column(String(20))
    notes = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

class TreatmentRecord(Base):
    __tablename__ = "treatment_record"

    id = Column(Integer, primary_key=True, index=True)
    user_plant_id = Column(Integer, ForeignKey("user_plant.id", ondelete="CASCADE"), nullable=False)
    treatment_type = Column(Enum('fertilize', 'pesticide', 'prune', 'other'), nullable=False)
    product_name = Column(String(100))
    dosage = Column(String(50))
    application_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
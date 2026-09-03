import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scans = relationship("ScanResult", back_populates="owner", cascade="all, delete-orphan")


class ScanResult(Base):
    """One saved analysis: the source image + both models' outputs."""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    image_path = Column(String, nullable=False)  # stored file, served back to the client

    # Model 1 output — skin type classifier
    skin_type = Column(String, nullable=False)          # dry | oily | combination | normal
    skin_type_confidence = Column(Float, nullable=False)

    # Model 2 output — multi-label skin concern detector
    # [{"label": "acne", "confidence": 0.87, "box": [x, y, w, h]}, ...]
    concerns = Column(JSON, nullable=False)

    # Ingredient/product suggestions computed from the two outputs above
    recommendations = Column(JSON, nullable=False)

    owner = relationship("User", back_populates="scans")

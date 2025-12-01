"""Database models for image analysis."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from db.database import Base

class Analysis(Base):
    """Stored analysis result."""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    image_data = Column(Text, nullable=False)  # Base64 encoded image
    aggregate_confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to user and model results
    user = relationship("User", back_populates="analyses")
    model_results = relationship("ModelResult", back_populates="analysis", cascade="all, delete-orphan")


class ModelResult(Base):
    """Individual model result within an analysis."""
    __tablename__ = "model_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    model_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

    # Relationship to analysis
    analysis = relationship("Analysis", back_populates="model_results")

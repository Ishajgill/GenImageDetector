"""Pydantic schemas for API analysis models."""
from pydantic import BaseModel
from typing import List
from datetime import datetime


class ModelResultSchema(BaseModel):
    """Schema for individual model result."""
    model_name: str
    confidence: float

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    """Schema for analysis response."""
    id: int
    filename: str
    image_data: str
    aggregate_confidence: float
    created_at: datetime
    model_results: List[ModelResultSchema]

    class Config:
        from_attributes = True

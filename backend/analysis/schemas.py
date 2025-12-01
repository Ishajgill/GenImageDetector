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


class HistoryMigrationItem(BaseModel):
    """Schema for a single history item to migrate from anonymous to authenticated user."""
    image: str  # base64 data URL
    filename: str
    aggregate_confidence: float
    model_results: List[ModelResultSchema]


class HistoryMigrationRequest(BaseModel):
    """Schema for batch history migration request."""
    items: List[HistoryMigrationItem]


class HistoryMigrationResponse(BaseModel):
    """Schema for history migration response."""
    migrated_count: int
    failed_count: int
    message: str

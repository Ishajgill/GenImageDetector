"""Pydantic schemas for auth models."""
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str


class User(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

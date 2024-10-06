# models.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PasswordEntryBase(BaseModel):
    website: str
    username: str
    password: str
    notes: Optional[str] = None

class PasswordEntryCreate(PasswordEntryBase):
    pass

class PasswordEntryUpdate(BaseModel):
    website: Optional[str]
    username: Optional[str]
    password: Optional[str]
    notes: Optional[str]


class PasswordEntry(BaseModel):
    id: int
    user_id: int
    website: str
    username: str
    password: Optional[str] = None  # Include password field
    notes: Optional[str] = None
    last_used: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    created_at: datetime


class Config:
    orm_mode = True

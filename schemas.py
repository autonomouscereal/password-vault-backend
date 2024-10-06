# app/schemas.py
from pydantic import BaseModel

class PasswordEntryBase(BaseModel):
    website: str
    username: str
    password: str  # This will be the plain text password from the client

class PasswordEntryCreate(PasswordEntryBase):
    pass

class PasswordEntry(PasswordEntryBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

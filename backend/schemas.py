from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Project Schemas ---
class ProjectBase(BaseModel):
    prompt_desc: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    user_id: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    credit_balance: int
    is_active: bool
    created_at: datetime.datetime
    projects: List[Project] = []

    class Config:
        from_attributes = True

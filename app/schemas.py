from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional, List

#this is the general schema
class UserBase(BaseModel):
    name:str
    username: str
    email: EmailStr
    phone: str
    qualification: str
    skills: List[str]  # List of skills

#schema to input password
class UserCreate(UserBase):
    password: str  # plain password input

#schema for user response
class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


#this is the login schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str
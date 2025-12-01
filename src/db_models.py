# src/db_models.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Authentification
class UserCreate(BaseModel):
    username: EmailStr
    password: str

class UserLogin(BaseModel):
    username: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    full_name: Optional[str] = None

# Chatbot
class ChatQuestion(BaseModel):
    chat_id: str
    question: str
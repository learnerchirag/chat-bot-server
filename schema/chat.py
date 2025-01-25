from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List
from datetime import datetime
from models.chat import PyObjectId
from utils import parse_datetime
from enums import MessageRole

class UserCreate(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

class SessionCreate(BaseModel):
    user_id: str
    ip_address: str

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    ip_address: str
    created_at: datetime
    expires_at: datetime

    def is_active(self) -> bool:
        return datetime.now() > self.expires_at

class ConversationMessage(BaseModel):
    role: MessageRole
    content: str
    class Config:
        use_enum_values = True  

class ConversationCreate(BaseModel):
    session_id: str
    messages: List[ConversationMessage]

class MessageUpdateRequest(BaseModel):
    content: str
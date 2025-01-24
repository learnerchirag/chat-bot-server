from pydantic import BaseModel, EmailStr, field_validator
from typing import List
from datetime import datetime
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
    timestamp: datetime

    @field_validator('timestamp', mode='before')
    def parse_timestamp(cls, value):
        parsed = parse_datetime(value)
        return parsed
    class Config:
        use_enum_values = True  

class ConversationCreate(BaseModel):
    session_id: str
    messages: List[ConversationMessage]

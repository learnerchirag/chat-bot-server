from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime

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
    role: str  # 'user' or 'bot'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConversationCreate(BaseModel):
    session_id: str
    messages: List[ConversationMessage]

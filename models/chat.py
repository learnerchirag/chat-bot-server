from pydantic import BaseModel, Field
from enums import MessageRole
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.general_plain_validator_function(cls.validate)


    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema

    @classmethod
    def validate(cls, v, info: core_schema.ValidationInfo):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class MessageModel(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime
    edited_at: Optional[datetime] = None
    session_id: str
    id: str
    class Config:
        use_enum_values = True  


class ConversationModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    session_id: str
    messages: List[MessageModel]
    
    def update_message_content(self, session_id: str, message_id: str, new_content: str) -> None:
        if self.session_id != session_id:
            raise ValueError(f"Session ID {session_id} does not match this conversation.")
        for message in self.messages:
            if message.id == message_id:
                message.content = new_content
                return
        raise ValueError(f"Message with ID {message_id} not found in this conversation.")


    class Config:
        json_encoders = {ObjectId: str}

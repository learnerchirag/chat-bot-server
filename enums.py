from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    BOT = "assistant"
    SYSTEM = "system"


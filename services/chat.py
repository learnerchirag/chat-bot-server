import uuid
from datetime import datetime
from pymongo import MongoClient
from typing import Any, Dict, Tuple
from schema.chat import ConversationCreate, ConversationMessage
from services.openai_service import GPTResponseGenerator
from enums import MessageRole

async def create_conversation(db: MongoClient, session_id: str) -> None:
    new_conversation = {
        'session_id': session_id,
        'messages': [],
        'created_at': datetime.utcnow()
    }
    await db.conversations.insert_one(new_conversation)

    
async def find_conversation_by_session_id(db: MongoClient, session_id: str) -> ConversationCreate:
    return await db.conversations.find_one({'session_id': session_id})

async def update_conversation(db: MongoClient, session_id: str, update_operation: str, update_value: Dict[str, Any]):
    await db.conversations.update_one(
        {'session_id': session_id},
        {update_operation: update_value}
    )


async def insert_message_into_conversation(db: MongoClient, session_id: str, user_message_doc: ConversationMessage, gpt_generator: GPTResponseGenerator) -> Tuple[ConversationMessage, ConversationMessage]:
    
    existing_conversation = await find_conversation_by_session_id(db, session_id)
    
    if not existing_conversation:
        print("NO EXISTING CONVERSATION")
        await create_conversation(db, session_id)

    user_message_doc['id'] = str(uuid.uuid4())
    
    await update_conversation(db, session_id, '$push', {'messages': user_message_doc})
    
    conversation = await find_conversation_by_session_id(db, session_id)

    conversation_history = list(conversation['messages'])
    conversation_history.sort(key=lambda msg: msg["timestamp"], reverse=True)

    gpt_messages = [
        {"role": msg['role'], "content": msg['content']} 
        for msg in conversation_history
    ]
    
    bot_response_text = gpt_generator.generate_response(gpt_messages)
    
    bot_message = {
        'id': str(uuid.uuid4()),
        'role': MessageRole.BOT,
        'content': bot_response_text,
        'session_id': session_id,
        "timestamp": datetime.utcnow()
    }
    
    await update_conversation(db, session_id, '$push', {'messages': bot_message})
    
    return user_message_doc, bot_message 
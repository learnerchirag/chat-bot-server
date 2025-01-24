import uuid
from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException
from schema.chat import UserCreate, UserResponse, SessionCreate, SessionResponse, ConversationCreate, ConversationMessage
from datetime import datetime, timedelta
from services.openai_service import GPTResponseGenerator
import services.chat as ChatService
from env import OPENAI_API_KEY

router = APIRouter()
gpt_generator = GPTResponseGenerator(OPENAI_API_KEY)

@router.post("/users/register")
async def register_user(user: UserCreate, request: Request):

    db = request.app.mongodb

    existing_user = await db.users.find_one({'email': user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_data = {
        'email': user.email,
        'name': user.name,
        'created_at': datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_data)
    return UserResponse(
        id=str(result.inserted_id),
        email=user.email,
        name=user.name
    )

@router.post("/sessions/create")
async def create_session(request: Request, session: SessionCreate):
    
    db = request.app.mongodb

    user = await db.users.find_one({'_id': ObjectId(session.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_session = await db.sessions.find_one({
        'user_id': session.user_id,
        'ip_address': session.ip_address,
        'expires_at': {'$gt': datetime.utcnow()}
    })

    if existing_session:
        return existing_session
    
    session_data = {
        'user_id': session.user_id,
        'session_id': str(uuid.uuid4()),
        'ip_address': session.ip_address,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=1)
    }
    
    await db.sessions.insert_one(session_data)
    return SessionResponse(**session_data)

@router.get("/conversations/{session_id}")
async def get_conversations(session_id: str, request: Request):
    db = request.app.mongodb

    conversation = await db.conversations.find_one({
        'session_id': session_id
    })

    if not conversation:
        return []

    return conversation


@router.post("/conversations/{session_id}/message")
async def send_message(
    session_id: str, 
    message: ConversationMessage,
    request: Request
):
    db = request.app.mongodb

    session = await db.sessions.find_one({
        'session_id': session_id,
        'expires_at': {'$gt': datetime.utcnow()}
    })
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user_message_doc = message.dict()
    user_message_doc['session_id'] = session_id

    user_message_doc, bot_message_doc = ChatService.insert_message_into_conversation(user_message_doc)
    
    return {
        "user_message": user_message_doc,
        "bot_response": bot_message_doc
    }

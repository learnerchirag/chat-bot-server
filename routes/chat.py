from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException
from schema.chat import UserCreate, UserResponse, SessionCreate, SessionResponse, ConversationCreate, ConversationMessage
from datetime import datetime, timedelta
from services.openai_service import GPTResponseGenerator
import services.chat as ChatService
import services.auth as AuthService
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
    
    existing_session = await AuthService.get_active_session(session=session)
    if existing_session is None:
        existing_session = await AuthService.create_session(db=db, session=session)
    
    return existing_session



@router.get("/conversations/{session_id}")
async def get_conversations(session_id: str, request: Request):
    db = request.app.mongodb

    session_valid = await AuthService.validate_session(db=db, session_id=session_id)
    
    if session_valid is False:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    conversation = await db.conversations.find_one({'session_id': session_id})

    if not conversation:
        return []
    return ConversationCreate(**conversation)


@router.post("/conversations/{session_id}/message")
async def send_message(
    session_id: str, 
    message: ConversationMessage,
    request: Request
):
    db = request.app.mongodb

    session_valid = await AuthService.validate_session(db=db, session_id=session_id)
    
    if session_valid is False:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user_message_doc = message.dict()
    user_message_doc['session_id'] = session_id

    user_message_doc, bot_message_doc = await ChatService.insert_message_into_conversation(
        db=db, 
        session_id=session_id, 
        user_message_doc=user_message_doc, 
        gpt_generator=gpt_generator
    )
    
    return {
        "user_message": user_message_doc,
        "bot_response": bot_message_doc
    }

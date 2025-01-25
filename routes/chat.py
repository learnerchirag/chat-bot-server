import uuid
from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException
from schema.chat import UserCreate, UserResponse, SessionCreate, ConversationCreate, ConversationMessage, MessageUpdateRequest
from datetime import datetime
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
    if existing_user is not None:
        return UserResponse(**existing_user)
    
    user_data = {
        'email': user.email,
        'name': user.name,
        'created_at': datetime.utcnow(),
        "id": str(uuid.uuid4())
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
    
    existing_session = await AuthService.get_active_session(db=db, session=session)
    if existing_session is None:
        existing_session = await AuthService.create_session(db=db, session=session)
    
    return existing_session

@router.get("/conversations/{session_id}")
async def get_conversations(session_id: str, request: Request):
    db = request.app.mongodb

    session_valid = await AuthService.validate_session(db=db, session_id=session_id)
    
    if session_valid is False:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    conversation = await ChatService.find_conversation_by_session_id(db=db, session_id=session_id)

    if not conversation:
        return None
    return conversation


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

@router.put("/conversations/{session_id}/message/{message_id}")
async def edit_message(
    session_id: str, 
    message_id: str, 
    update_request: MessageUpdateRequest,
    request: Request
):
    db = request.app.mongodb

    session_valid = await AuthService.validate_session(db=db, session_id=session_id)
    
    if session_valid is False:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    conversation = await ChatService.find_conversation_by_session_id(db=db, session_id=session_id)
    conversation.update_message_content(session_id=session_id, message_id=message_id, new_content=update_request.content)
    result = await ChatService.update_conversation(db=db, session_id=session_id, update_operation="$set", update_value={"messages": [msg.dict() for msg in conversation.messages]})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"status": "Message updated successfully"}

@router.delete("/conversations/{session_id}/message/{message_id}")
async def delete_message(session_id: str, message_id: str, request: Request):

    db = request.app.mongodb

    session_valid = await AuthService.validate_session(db=db, session_id=session_id)
    
    if session_valid is False:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    result = await ChatService.delete_message(db=db, session_id=session_id, message_id=message_id)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"status": "Message deleted successfully"}
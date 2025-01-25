import uuid
from pymongo import MongoClient
from datetime import datetime, timedelta
from schema.chat import SessionCreate, SessionResponse

async def validate_session(db: MongoClient, session_id: str) -> bool:
    sessions_collection = db.sessions
    session = await sessions_collection.find_one({
        'session_id': session_id,
        'expires_at': {'$gt': datetime.utcnow()}
    })
    return session is not None


async def create_session(db: MongoClient, session: SessionCreate) -> SessionResponse:
    session_data = {
        'user_id': session.user_id,
        'session_id': str(uuid.uuid4()),
        'ip_address': session.ip_address,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(hours=1)
    }
    
    await db.sessions.insert_one(session_data)
    return SessionResponse(**session_data)

async def get_active_session(db: MongoClient, session: SessionCreate) -> SessionResponse:
    session = await db.sessions.find_one({
        'user_id': session.user_id,
        'ip_address': session.ip_address,
        'expires_at': {'$gt': datetime.utcnow()}
    })
    return SessionResponse(**session)
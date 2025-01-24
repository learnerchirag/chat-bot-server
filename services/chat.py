import uuid
from datetime import datetime

async def create_conversation(db, session_id):
    new_conversation = {
        'session_id': session_id,
        'messages': [],
        'created_at': datetime.utcnow()
    }
    await db.conversations.insert_one(new_conversation)

    
async def find_conversation_by_session_id(db, session_id):
    return await db.conversations.find_one({'session_id': session_id})

async def update_conversation(db, session_id, update_operation, update_value):
    return await db.conversations.update_one(
        {'session_id': session_id},
        {[update_operation]: update_value}
    )


async def insert_message_into_conversation(db, session_id, user_message_doc, gpt_generator):
    
    existing_conversation = await find_conversation_by_session_id(db, session_id)
    
    if not existing_conversation:
        await create_conversation(db, session_id)

    user_message_doc['id'] = str(uuid.uuid4())
    
    conversation_history = await update_conversation(db, session_id, '$push', {'messages': user_message_doc})
    
    conversation_history = list(conversation_history['messages']).sort("timestamp", 1)[:5]
    
    gpt_messages = [
        {"role": msg['role'], "content": msg['content']} 
        for msg in conversation_history
    ]
    
    bot_response_text = gpt_generator.generate_response(gpt_messages)
    
    bot_message = {
        'id': str(uuid.uuid4()),
        'role': 'bot',
        'content': bot_response_text,
        'session_id': session_id
    }
    
    await update_conversation(session_id, '$push', {'messages': bot_message})
    
    return user_message_doc, bot_message 
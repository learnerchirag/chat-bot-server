from fastapi import FastAPI, HTTPException
from database import lifespan
from routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=chat_router, prefix="/api/v1", tags=["chat"])

@app.get("/test-db")
async def test_db_connection():
    try:
        # Attempt to fetch a collection to test the connection
        collections = await app.mongodb.list_collection_names()
        return {"status": "success", "collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
@app.get("/")
def read_root():
    return {"Hello": "World"}
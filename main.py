from fastapi import FastAPI, HTTPException
from database import lifespan

app = FastAPI(lifespan=lifespan)


@app.get("/test-db")  # Changed from fastapi.get to app.get
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
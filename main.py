# fastAPI
from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Intelligent Query System")
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Intelligent Query System API"}
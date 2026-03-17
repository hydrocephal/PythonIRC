from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ghost IRC Chat")

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Ghost IRC Chat"}
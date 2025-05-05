from fastapi import FastAPI
from app.api import users, auth
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Task Management API"}

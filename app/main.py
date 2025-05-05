from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, projects, tasks, optimizer
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Task Management API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Включение API маршрутов
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(tasks.router, prefix=settings.API_V1_STR)
app.include_router(optimizer.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Task Management API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

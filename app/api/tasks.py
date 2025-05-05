from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Task, TaskCreate
from app.crud import task
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=Task)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return task.create(db, task_in)

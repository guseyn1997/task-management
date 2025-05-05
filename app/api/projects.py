from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Project, ProjectCreate
from app.crud import project
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=Project)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return project.create(db, project_in, current_user.id)

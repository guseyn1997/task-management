from pydantic import BaseModel
from datetime import datetime

class ProjectBase(BaseModel):
    title: str
    description: str | None = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

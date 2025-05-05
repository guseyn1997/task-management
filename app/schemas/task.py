from pydantic import BaseModel
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    priority: int = 3

class TaskCreate(TaskBase):
    project_id: int

class Task(TaskBase):
    id: int
    is_completed: bool
    created_at: datetime
    assignee_id: int | None
    
    class Config:
        orm_mode = True

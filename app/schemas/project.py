from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Общие атрибуты
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

# Свойства для создания проекта
class ProjectCreate(ProjectBase):
    pass

# Свойства для обновления проекта
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Свойства модели, возвращаемые API
class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Расширенная модель с информацией о задачах
class ProjectDetail(Project):
    tasks_count: int
    completed_tasks_count: int

    class Config:
        orm_mode = True

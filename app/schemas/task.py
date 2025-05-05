from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

# Статусы задачи
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# Приоритеты задачи
class TaskPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

# Общие атрибуты
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_hours: Optional[int] = 0
    deadline: Optional[datetime] = None

# Свойства для создания задачи
class TaskCreate(TaskBase):
    project_id: int
    assigned_to: Optional[int] = None

# Свойства для обновления задачи
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    estimated_hours: Optional[int] = None
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None
    deadline: Optional[datetime] = None

# Свойства модели, возвращаемые API
class Task(TaskBase):
    id: int
    project_id: int
    assigned_to: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Запрос оптимизации задач
class OptimizationRequest(BaseModel):
    user_ids: List[int]
    project_id: Optional[int] = None  # Если None, то оптимизируем задачи по всем проектам

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import numpy as np
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskAssignment
from app.core.security import get_current_user

router = APIRouter()

@router.post("/optimize-tasks", response_model=List[TaskAssignment])
def optimize_task_assignment(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Алгоритм оптимизации распределения задач между сотрудниками
    с учетом загруженности и приоритетов задач.
    """

    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_completed == False
    ).order_by(Task.priority.desc()).all()
    
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this project")
    
    users = db.query(User).filter(User.is_active == True).all()
    
    if not users:
        raise HTTPException(status_code=404, detail="No active users found")
    
    user_workloads = {}
    for user in users:
        assigned_tasks = db.query(Task).filter(
            Task.assignee_id == user.id,
            Task.is_completed == False
        ).all()
        
        workload = sum([task.priority for task in assigned_tasks])
        user_workloads[user.id] = workload

    assignments = []
    
    for task in tasks:
        if task.assignee_id is not None:
            continue
  
        min_workload = float('inf')
        best_user_id = None
        
        for user_id, workload in user_workloads.items():
            if workload < min_workload:
                min_workload = workload
                best_user_id = user_id

        if best_user_id:
            task.assignee_id = best_user_id
            user_workloads[best_user_id] += task.priority

            days_to_add = 7 - task.priority
            task.due_date = datetime.now() + timedelta(days=days_to_add)
            
            db.add(task)
            assignments.append(
                TaskAssignment(
                    task_id=task.id,
                    task_title=task.title,
                    assignee_id=best_user_id,
                    due_date=task.due_date
                )
            )
    
    db.commit()
    return assignments

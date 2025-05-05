from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.dependencies import get_current_active_user, get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=schemas.Task)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Создать новую задачу
    """
    # Проверяем существование проекта и права доступа
    project = crud.project.get(db, id=task_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден",
        )
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас недостаточно прав для выполнения этого действия",
        )
    
    # Если указан пользователь для назначения, проверяем его существование
    if task_in.assigned_to:
        assignee = crud.user.get(db, id=task_in.assigned_to)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь для назначения не найден",
            )
    
    task = crud.task.create_with_creator(
        db=db, obj_in=task_in, creator_id=current_user.id
    )
    return task

@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    status: Optional[schemas.TaskStatus] = None,
    priority: Optional[schemas.TaskPriority] = None,
    assigned_to: Optional[int] = None,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить список задач с возможностью фильтрации
    """
    if project_id:
        # Проверка доступа к проекту
        project = crud.project.get(db, id=project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден",
            )
        if not current_user.is_superuser and project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия",
            )
    
    # Фильтрация задач
    if current_user.is_superuser:
        tasks = crud.task.get_multi_filtered(
            db, 
            skip=skip, 
            limit=limit,
            project_id=project_id,
            status=status,
            priority=priority,
            assigned_to=assigned_to
        )
    else:
        # Обычный пользователь видит задачи из своих проектов или назначенные ему
        tasks = crud.task.get_multi_for_user(
            db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            project_id=project_id,
            status=status,
            priority=priority,
            assigned_to=assigned_to
        )
    
    return tasks

@router.get("/{task_id}", response_model=schemas.Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить задачу по ID
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    
    # Проверка доступа (суперпользователь, владелец проекта или назначенный исполнитель)
    if not current_user.is_superuser:
        project = crud.project.get(db, id=task.project_id)
        if project.owner_id != current_user.id and task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия",
            )
    
    return task

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить задачу
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    
    # Проверка доступа (суперпользователь, владелец проекта или назначенный исполнитель)
    if not current_user.is_superuser:
        project = crud.project.get(db, id=task.project_id)
        if project.owner_id != current_user.id and task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия",
            )
    
    # Если меняется проект, проверяем права на новый проект
    if task_in.project_id and task_in.project_id != task.project_id:
        new_project = crud.project.get(db, id=task_in.project_id)
        if not new_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Новый проект не найден",
            )
        if not current_user.is_superuser and new_project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для перемещения задачи в этот проект",
            )
    
    # Если меняется назначенный пользователь, проверяем его существование
    if task_in.assigned_to and task_in.assigned_to != task.assigned_to:
        assignee = crud.user.get(db, id=task_in.assigned_to)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь для назначения не найден",
            )
    
    task = crud.task.update(db, db_obj=task, obj_in=task_in)
    return task

@router.delete("/{task_id}", response_model=schemas.Task)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить задачу
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    
    # Проверка прав (суперпользователь или владелец проекта)
    if not current_user.is_superuser:
        project = crud.project.get(db, id=task.project_id)
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия",
            )
    
    task = crud.task.remove(db, id=task_id)
    return task

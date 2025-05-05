from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.dependencies import get_current_active_user, get_db

router = APIRouter(prefix="/optimizer", tags=["task-optimizer"])

@router.post("/optimize-tasks", response_model=Dict[int, List[schemas.Task]])
def optimize_tasks(
    optimization_request: schemas.OptimizationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Оптимизация распределения задач между пользователями
    
    Алгоритм:
    1. Проверяет доступ к проекту (если указан)
    2. Получает все нераспределенные задачи и задачи назначенные на указанных пользователей
    3. Вычисляет оптимальное распределение задач с учетом:
       - Приоритета задач
       - Предполагаемого времени выполнения
       - Текущей загруженности пользователей
       - Дедлайнов задач
    4. Возвращает оптимальное распределение задач
    """
    # Проверка существования пользователей
    users = {}
    for user_id in optimization_request.user_ids:
        user = crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {user_id} не найден",
            )
        users[user_id] = user
    
    # Проверка проекта, если указан
    project = None
    if optimization_request.project_id:
        project = crud.project.get(db, id=optimization_request.project_id)
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
    
    # Получение задач для оптимизации
    tasks = crud.task.get_tasks_for_optimization(
        db,
        user_ids=optimization_request.user_ids,
        project_id=optimization_request.project_id,
        current_user=current_user
    )
    
    # Алгоритм оптимизации (распределение по приоритету и оценке времени)
    
    # Сортировка задач по приоритету и дедлайну
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (
            -t.priority,  # От высокого к низкому
            t.deadline or "9999-12-31",  # Задачи с дедлайном в начале
            t.estimated_hours or 0  # Затем по оценке времени
        )
    )
    
    # Расчет текущей нагрузки на пользователей
    user_loads = {user_id: 0 for user_id in users}
    for user_id in users:
        assigned_tasks = crud.task.get_active_tasks_for_user(db, user_id=user_id)
        user_loads[user_id] = sum(task.estimated_hours or 1 for task in assigned_tasks)
    
    # Распределение задач
    optimized_distribution = {user_id: [] for user_id in users}
    
    for task in sorted_tasks:
        # Находим пользователя с наименьшей нагрузкой
        min_load_user_id = min(user_loads, key=user_loads.get)
        
        # Назначаем задачу
        task_in = schemas.TaskUpdate(assigned_to=min_load_user_id)
        updated_task = crud.task.update(db, db_obj=task, obj_in=task_in)
        
        # Обновляем нагрузку
        user_loads[min_load_user_id] += updated_task.estimated_hours or 1
        
        # Добавляем задачу в результат
        optimized_distribution[min_load_user_id].append(updated_task)
    
    return optimized_distribution

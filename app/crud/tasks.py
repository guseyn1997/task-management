from typing import List, Optional, Dict, Any, Union

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.task import Task, TaskStatus
from app.models.project import Project
from app.schemas.task import TaskCreate, TaskUpdate

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def create_with_creator(
        self, db: Session, *, obj_in: TaskCreate, creator_id: int
    ) -> Task:
        """
        Создать задачу с указанием создателя
        """
        obj_in_data = obj_in.dict()
        db_obj = Task(**obj_in_data, created_by=creator_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_filtered(
        self, 
        db: Session, 
        *,
        skip: int = 0, 
        limit: int = 100,
        project_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[int] = None,
        assigned_to: Optional[int] = None
    ) -> List[Task]:
        """
        Получить задачи с фильтрацией
        """
        query = db.query(Task)
        
        if project_id:
            query = query.filter(Task.project_id == project_id)
        
        if status:
            query = query.filter(Task.status == status)
        
        if priority:
            query = query.filter(Task.priority == priority)
        
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        
        return query.offset(skip).limit(limit).all()

    def get_multi_for_user(
        self, 
        db: Session, 
        *,
        user_id: int,
        skip: int = 0, 
        limit: int = 100,
        project_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[int] = None,
        assigned_to: Optional[int] = None
    ) -> List[Task]:
        """
        Получить задачи для пользователя (созданные им, назначенные ему или из его проектов)
        """
        # Сначала получаем проекты пользователя
        user_projects = db.query(Project.id).filter(Project.owner_id == user_id).all()
        user_project_ids = [p.id for p in user_projects]
        
        # Формируем запрос
        query = db.query(Task).filter(
            or_(
                Task.project_id.in_(user_project_ids),
                Task.assigned_to == user_id,
                Task.created_by == user_id
            )
        )
        
        # Дополнительные фильтры
        if project_id:
            # Проверяем, принадлежит ли проект пользователю
            if project_id in user_project_ids:
                query = query.filter(Task.project_id == project_id)
            else:
                # Если проект не принадлежит пользователю, возвращаем только задачи,
                # назначенные на пользователя или созданные им в этом проекте
                query = query.filter(
                    Task.project_id == project_id,
                    or_(
                        Task.assigned_to == user_id,
                        Task.created_by == user_id
                    )
                )
        
        if status:
            query = query.filter(Task.status == status)
        
        if priority:
            query = query.filter(Task.priority == priority)
        
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        
        return query.offset(skip).limit(limit).all()

    def get_tasks_for_optimization(
        self,
        db: Session,
        *,
        user_ids: List[int],
        project_id: Optional[int] = None,
        current_user: Any = None
    ) -> List[Task]:
        """
        Получить задачи для оптимизации
        """
        query = db.query(Task).filter(
            or_(
                Task.assigned_to.in_(user_ids),  # Задачи, уже назначенные на этих пользователей
                Task.assigned_to.is_(None)  # Нераспределенные задачи
            )
        )
        
        # Фильтр по статусу - только невыполненные задачи
        query = query.filter(Task.status != TaskStatus.DONE)
        
        # Фильтр по проекту если указан
        if project_id:
            query = query.filter(Task.project_id == project_id)
        elif not current_user.is_superuser:
            # Если пользователь не суперпользователь и проект не указан,
            # возвращаем только задачи из его проектов
            user_projects = db.query(Project.id).filter(Project.owner_id == current_user.id).all()
            user_project_ids = [p.id for p in user_projects]
            query = query.filter(Task.project_id.in_(user_project_ids))
        
        return query.all()

    def get_active_tasks_for_user(
        self,
        db: Session,
        *,
        user_id: int
    ) -> List[Task]:
        """
        Получить активные задачи пользователя (невыполненные)
        """
        return (
            db.query(Task)
            .filter(
                Task.assigned_to == user_id,
                Task.status != TaskStatus.DONE
            )
            .all()
        )

task = CRUDTask(Task)

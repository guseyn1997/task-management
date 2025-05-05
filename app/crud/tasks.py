from sqlalchemy.orm import Session
from app.models import Task
from app.schemas import TaskCreate

class CRUDTask:
    def create(self, db: Session, obj_in: TaskCreate):
        db_obj = Task(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

task = CRUDTask()

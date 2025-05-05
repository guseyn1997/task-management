from sqlalchemy.orm import Session
from app.models import Project
from app.schemas import ProjectCreate

class CRUDProject:
    def create(self, db: Session, obj_in: ProjectCreate, owner_id: int):
        db_obj = Project(**obj_in.dict(), owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

project = CRUDProject()

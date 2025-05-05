from typing import Any, Dict, Generic, TypeVar
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: ModelType):
        self.model = model

    def get(self, db: Session, id: Any):
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, *, obj_in: Dict):
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

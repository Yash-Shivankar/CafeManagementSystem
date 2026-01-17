# app/crud/base.py
from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.security import hash_password
from datetime import datetime

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int):
        return (
            db.query(self.model)
            .filter(self.model.id == id, self.model.is_deleted == False)
            .first()
        )

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        return (
            db.query(self.model)
            .filter(self.model.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_paginated(self, db: Session, skip: int = 0, limit: int = 100):
        query = db.query(self.model).filter(self.model.is_deleted == False)

        total = query.count()

        users = query.offset(skip).limit(limit).all()

        return users, total

    def create(self, db: Session, obj_in: CreateSchemaType, current_user=None):
        data = obj_in.dict(exclude={"password"})  # handle password separately
        if hasattr(obj_in, "password"):
            data["hashed_password"] = hash_password(obj_in.password)
        if current_user:
            data["created_by"] = current_user.id
            data["updated_by"] = current_user.id
        db_obj = self.model(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj, obj_in: UpdateSchemaType, current_user=None):
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        if current_user:
            db_obj.updated_by = current_user.id
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int, current_user=None):
        obj = db.query(self.model).get(id)
        if not obj:
            return None
        obj.is_deleted = True
        obj.deleted_at = datetime.utcnow()
        if current_user:
            obj.updated_by = current_user.id
        db.commit()
        db.refresh(obj)
        return obj

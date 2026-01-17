# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.base import CRUDBase
from app.models.User import User
from app.schemas.user import UserCreate, UserUpdate, UserOut, PaginatedUserOut
from math import ceil

router = APIRouter(prefix="/users", tags=["Users"])

crud_user = CRUDBase[User, UserCreate, UserUpdate](User)


@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create(db, user)


@router.get("/", response_model=PaginatedUserOut)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit

    users, total = crud_user.get_multi_paginated(db, skip=skip, limit=limit)

    total_pages = ceil(total / limit)

    return {
        "data": users,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = crud_user.get(db, user_id)
    return crud_user.update(db, db_user, user)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud_user.remove(db, user_id)

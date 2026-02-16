# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
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
    if user.email:
        existing_email_user = db.query(User).filter(User.email == user.email).first()
        if existing_email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

    # Check if mobile number already exists
    if user.mobile_number:
        existing_mobile_user = (
            db.query(User).filter(User.mobile_number == user.mobile_number).first()
        )
        if existing_mobile_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this mobile number already exists",
            )
    return crud_user.create(db, user)


@router.get("/", response_model=PaginatedUserOut)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    is_active: bool | None = Query(None),
    role_id: int | None = Query(None),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit

    filters = []

    if is_active is not None:
        filters.append(User.is_active == is_active)
    if role_id:
        filters.append(User.role_id == role_id)

    if search:
        filters.append(
            or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
            )
        )

    users, total = crud_user.get_multi_paginated(
        db,
        skip=skip,
        limit=limit,
        filters=filters,
        relationships=[
            "role",
        ],
    )

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
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check email uniqueness excluding current user
    if user.email:
        existing_email_user = (
            db.query(User).filter(User.email == user.email, User.id != user_id).first()
        )
        if existing_email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
            )

    # Check mobile number uniqueness excluding current user
    if user.mobile_number:
        existing_mobile_user = (
            db.query(User)
            .filter(User.mobile_number == user.mobile_number, User.id != user_id)
            .first()
        )
        if existing_mobile_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already exists",
            )
    return crud_user.update(db, db_user, user)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud_user.remove(db, user_id)

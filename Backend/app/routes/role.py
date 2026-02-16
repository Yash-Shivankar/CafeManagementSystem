# app/rotes/roles.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.crud.base import CRUDBase
from app.models.Role import Role
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut, PaginatedRoleOut
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/roles", tags=["Roles"])
role_crud = CRUDBase[Role, RoleCreate, RoleUpdate](Role)


@router.post("/", response_model=RoleOut)
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return role_crud.create(db, obj_in=role_in, current_user=current_user)


@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    return role_crud.get(db, role_id)


@router.get("/", response_model=PaginatedRoleOut)
def list_roles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    filters = []
    if search:
        filters.append(or_(Role.role_name.ilike(f"%{search}%")))
    roles, total = role_crud.get_multi_paginated(
        db,
        skip=skip,
        limit=limit,
        filters=filters,
    )
    total_pages = ceil(total / limit)
    return {
        "data": roles,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_role = role_crud.get(db, role_id)
    return role_crud.update(db, db_role, obj_in=role_in, current_user=current_user)


@router.delete("/{role_id}", response_model=RoleOut)
def delete_role(
    role_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return role_crud.remove(db, role_id, current_user=current_user)

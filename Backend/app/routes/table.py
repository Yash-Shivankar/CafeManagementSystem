from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.Table import Table
from app.schemas.table import TableCreate, TableUpdate, TableOut, PaginatedTableOut
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/tables", tags=["Tables"])

table_crud = CRUDBase[Table, TableCreate, TableUpdate](Table)


@router.post("/", response_model=TableOut)
def create_table(
    obj_in: TableCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return table_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{table_id}", response_model=TableOut)
def get_table(
    table_id: int,
    db: Session = Depends(get_db),
):
    return table_crud.get(db, table_id)


# @router.get("/", response_model=List[TableOut])
# def list_tables(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
# ):
#     return table_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedTableOut)
def list_tables(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    tables, total = table_crud.get_multi_paginated(db, skip=skip, limit=limit)
    total_pages = ceil(total / limit)
    return {
        "data": tables,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{table_id}", response_model=TableOut)
def update_table(
    table_id: int,
    obj_in: TableUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = table_crud.get(db, table_id)
    return table_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{table_id}", response_model=TableOut)
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return table_crud.remove(
        db=db,
        id=table_id,
        current_user=current_user,
    )

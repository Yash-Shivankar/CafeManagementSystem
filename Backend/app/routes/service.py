from fastapi import APIRouter, Depends, Query
from sqlalchemy import cast, String, or_
from sqlalchemy.orm import Session
from typing import List

from app.crud.base import CRUDBase
from app.models.Service import Service
from app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceOut,
    PaginatedServiceOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/services", tags=["Services"])

service_crud = CRUDBase[Service, ServiceCreate, ServiceUpdate](Service)


@router.post("/", response_model=ServiceOut)
def create_service(
    obj_in: ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    return service_crud.get(db, service_id)


# @router.get("/", response_model=List[ServiceOut])
# def list_service(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
# ):
#     return service_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedServiceOut)
def list_services(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    filters = []
    if search:
        filters.append(
            or_(
                Service.name.ilike(f"%{search}%"),
                cast(Service.price, String).ilike(f"%{search}%"),
            )
        )

    services, total = service_crud.get_multi_paginated(
        db, skip=skip, limit=limit, filters=filters
    )
    total_pages = ceil(total / limit)
    return {
        "data": services,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    obj_in: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = service_crud.get(db, service_id)
    return service_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{service_id}", response_model=ServiceOut)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service_crud.remove(
        db=db,
        id=service_id,
        current_user=current_user,
    )

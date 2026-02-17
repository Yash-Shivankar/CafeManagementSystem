# app/api/employee_document.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.EmployeeDocument import EmployeeDocument
from app.models.EmployeeDetails import EmployeeDetails
from app.models.User import User
from app.schemas.employee_document import (
    EmployeeDocumentCreate,
    EmployeeDocumentUpdate,
    EmployeeDocumentOut,
    PaginatedEmployeeDocumentOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/employee-documents", tags=["EmployeeDocuments"])
document_crud = CRUDBase[
    EmployeeDocument, EmployeeDocumentCreate, EmployeeDocumentUpdate
](EmployeeDocument)


@router.post("/", response_model=EmployeeDocumentOut)
def create_document(
    obj_in: EmployeeDocumentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return document_crud.create(db, obj_in=obj_in, current_user=current_user)


@router.get("/{document_id}", response_model=EmployeeDocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    return document_crud.get(db, document_id)


# @router.get("/", response_model=List[EmployeeDocumentOut])
# def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return document_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedEmployeeDocumentOut)
def list_documents(
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
                EmployeeDocument.filename.ilike(f"%{search}%"),
                EmployeeDocument.original_name.ilike(f"%{search}%"),
                EmployeeDocument.doc_type.ilike(f"%{search}%"),
                EmployeeDocument.employee.has(
                    EmployeeDetails.user.has(
                        or_(
                            User.first_name.ilike(f"%{search}%"),
                            User.last_name.ilike(f"%{search}%"),
                        )
                    ),
                ),
            )
        )

    documents, total = document_crud.get_multi_paginated(
        db, skip=skip, limit=limit, filters=filters, relationships=["employee"]
    )
    total_pages = ceil(total / limit)
    return {
        "data": documents,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{document_id}", response_model=EmployeeDocumentOut)
def update_document(
    document_id: int,
    obj_in: EmployeeDocumentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = document_crud.get(db, document_id)
    return document_crud.update(db, db_obj, obj_in=obj_in, current_user=current_user)


@router.delete("/{document_id}", response_model=EmployeeDocumentOut)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return document_crud.remove(db, document_id, current_user=current_user)

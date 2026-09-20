"""EmployeeDocuments endpoints.

HTTP binding only: path, verb, response model. What happens next is
EmployeeDocumentService; how it is fetched is EmployeeDocumentRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.employeeDocumentController import EmployeeDocumentController
from app.schemas.employee_document import (
    EmployeeDocumentCreate,
    EmployeeDocumentOut,
    EmployeeDocumentUpdate,
    PaginatedEmployeeDocumentOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/employee-documents", tags=["EmployeeDocuments"])


@router.get("/", response_model=PaginatedEmployeeDocumentOut)
def list_documents(
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: EmployeeDocumentController = Depends(),
):
    return controller.list(
        params,
        search=search,
    )


@router.get("/{document_id}", response_model=EmployeeDocumentOut)
def get_document(
    document_id: int,
    controller: EmployeeDocumentController = Depends(),
):
    return controller.get(document_id)


@router.post("/", response_model=EmployeeDocumentOut)
def create_document(
    payload: EmployeeDocumentCreate,
    controller: EmployeeDocumentController = Depends(),
):
    return controller.create(payload)


@router.put("/{document_id}", response_model=EmployeeDocumentOut)
def update_document(
    document_id: int,
    payload: EmployeeDocumentUpdate,
    controller: EmployeeDocumentController = Depends(),
):
    return controller.update(document_id, payload)


@router.delete("/{document_id}", response_model=EmployeeDocumentOut)
def delete_document(
    document_id: int,
    controller: EmployeeDocumentController = Depends(),
):
    return controller.delete(document_id)

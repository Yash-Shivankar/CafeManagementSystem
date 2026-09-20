from pydantic import BaseModel, ConfigDict


class DesignationBase(BaseModel):
    designation_name: str


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(BaseModel):
    designation_name: str | None = None


class DesignationOut(DesignationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedDesignationOut(BaseModel):
    data: list[DesignationOut]
    total: int
    totalPages: int
    currentPage: int

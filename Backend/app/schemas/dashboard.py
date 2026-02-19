from pydantic import BaseModel


class DashboardBase(BaseModel):
    users_count: int
    employees_count: int
    customers_count: int
    items_count: int


class DashboardOut(DashboardBase):
    pass

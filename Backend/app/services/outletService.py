from app.models.Outlet import Outlet
from app.repositories.outletRepository import OutletRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError


class OutletService(BaseService[Outlet]):
    """Outlet use-cases.

    Two rules worth stating out loud:

    * A user who is posted to one outlet sees only that outlet in the list.
      Without this, the branch switcher would show every branch in the chain to
      a Manager who can only act in one of them.
    * An outlet is never really deleted while it holds history. Soft-deleting
      the row would orphan invoices, payroll and stock movements that are legal
      records, so retiring a branch means `is_active = false`.
    """

    repository_class = OutletRepository
    entity_name = "Outlet"
    unique_fields = ("code",)

    def scope_filters(self) -> list:
        if self.is_org_wide:
            return []
        if self.outlet_id is not None:
            return [Outlet.id == self.outlet_id]
        return [Outlet.id == -1]

    def before_delete(self, obj: Outlet) -> None:
        raise BusinessRuleError(
            "An outlet cannot be deleted — its invoices, payroll and stock "
            "movements are records you are required to keep. Set is_active to "
            "false to retire it instead."
        )

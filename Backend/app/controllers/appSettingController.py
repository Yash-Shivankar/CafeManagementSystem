from app.controllers.baseController import BaseController
from app.services.appSettingService import AppSettingService


class AppSettingController(BaseController):
    """HTTP shaping for application settings. No rules — see AppSettingService."""

    service_class = AppSettingService
    service: AppSettingService

    def list_all(self):
        return self.service.list_all()

    def get_by_key(self, key: str):
        return self.service.get_by_key(key)

    def set_value(self, key: str, value: str):
        return self.service.set_value(key, value)

    def delete_by_key(self, key: str):
        self.service.delete_by_key(key)
        return {"detail": "Setting deleted successfully"}

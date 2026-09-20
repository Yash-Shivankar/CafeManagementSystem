from app.models.AppSettings import AppSettings
from app.repositories.appSettingRepository import AppSettingRepository
from app.services.baseService import BaseService
from app.utils.exceptions import NotFoundError


class AppSettingService(BaseService[AppSettings]):
    """Application settings — key/value configuration, not records.

    `set_value` is an upsert on purpose: the SPA's settings screen sends
    "theme = mysticForest" without caring whether a row already exists, and
    making the caller check first is a round trip that buys nothing.
    """

    repository_class = AppSettingRepository
    entity_name = "Setting"
    unique_fields = ("key",)

    repository: AppSettingRepository

    def list_all(self) -> list[AppSettings]:
        return self.repository.all_settings()

    def get_by_key(self, key: str) -> AppSettings:
        setting = self.repository.get_by_key(key)
        if setting is None:
            raise NotFoundError(f"Setting {key!r} not found")
        return setting

    def set_value(self, key: str, value: str) -> AppSettings:
        setting = self.repository.get_by_key(key)

        try:
            if setting is None:
                setting = self.repository.create(
                    {"key": key, "value": value}, actor_id=self.actor_id
                )
            else:
                setting = self.repository.update(setting, {"value": value}, actor_id=self.actor_id)
            self.commit()
        except Exception:
            self.rollback()
            raise

        self.db.refresh(setting)
        return setting

    def delete_by_key(self, key: str) -> AppSettings:
        setting = self.get_by_key(key)
        try:
            self.repository.soft_delete(setting, actor_id=self.actor_id)
            self.commit()
        except Exception:
            self.rollback()
            raise
        return setting

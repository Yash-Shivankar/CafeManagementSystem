from app.models.AppSettings import AppSettings
from app.repositories.baseRepository import BaseRepository


class AppSettingRepository(BaseRepository[AppSettings]):
    """Every app-settings query lives here.

    Settings are addressed by `key`, not by id — the SPA asks for "theme", not
    for row 7 — so this repository adds key-based lookups on top of the
    standard set.
    """

    model = AppSettings
    search_columns = ("key", "value")
    order_by_column = "key"

    def get_by_key(self, key: str) -> AppSettings | None:
        return self.get_by(key=key)

    def all_settings(self) -> list[AppSettings]:
        return self._base_query().order_by(AppSettings.key.asc()).all()

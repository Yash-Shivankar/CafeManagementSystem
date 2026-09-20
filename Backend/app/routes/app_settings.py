"""Settings endpoints.

Addressed by key rather than id. The list stays an unpaginated array because
there are a handful of settings and the SPA reads the whole set on boot.
"""

from fastapi import APIRouter, Depends, status

from app.controllers.appSettingController import AppSettingController
from app.schemas.app_settings import SettingCreate, SettingOut, SettingUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=list[SettingOut])
def get_all_settings(controller: AppSettingController = Depends()):
    return controller.list_all()


@router.get("/{key}", response_model=SettingOut)
def get_setting(key: str, controller: AppSettingController = Depends()):
    return controller.get_by_key(key)


@router.post("/", response_model=SettingOut, status_code=status.HTTP_201_CREATED)
def create_setting(
    payload: SettingCreate,
    controller: AppSettingController = Depends(),
):
    return controller.create(payload)


@router.put("/{key}", response_model=SettingOut)
def update_setting(
    key: str,
    payload: SettingUpdate,
    controller: AppSettingController = Depends(),
):
    """Upsert — creates the setting if it does not exist yet, which is what the
    previous handler already did, just without saying so."""
    return controller.set_value(key, payload.value)


@router.delete("/{key}", response_model=dict)
def delete_setting(key: str, controller: AppSettingController = Depends()):
    return controller.delete_by_key(key)

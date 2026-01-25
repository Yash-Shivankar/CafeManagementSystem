from app.crud.base import CRUDBase
from app.models.AppSettings import AppSettings
from app.schemas.app_settings import SettingCreate, SettingUpdate, SettingOut
from app.dependencies.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db

router = APIRouter(prefix="/settings", tags=["Settings"])
setting_crud = CRUDBase[AppSettings, SettingCreate, SettingUpdate](AppSettings)


@router.get("/", response_model=List[SettingOut])
def get_all_settings(db: Session = Depends(get_db)):
    settings = setting_crud.get_multi(db, skip=0, limit=1000)
    return settings


@router.get("/{key}", response_model=SettingOut)
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    setting = (
        db.query(AppSettings)
        .filter(AppSettings.key == key, AppSettings.is_deleted == False)
        .first()
    )
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.post(
    "/",
    response_model=SettingOut,
    status_code=status.HTTP_201_CREATED,
)
def create_setting(
    payload: SettingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = (
        db.query(AppSettings)
        .filter(AppSettings.key == payload.key, AppSettings.is_deleted == False)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Setting key already exists")
    return setting_crud.create(db, payload, current_user=current_user)


@router.put("/{key}", response_model=SettingOut)
def update_setting(
    key: str,
    payload: SettingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    setting = (
        db.query(AppSettings)
        .filter(AppSettings.key == key, AppSettings.is_deleted == False)
        .first()
    )
    if not setting:
        # create if not exist
        return setting_crud.create(db, SettingCreate(key=key, value=payload.value))
    return setting_crud.update(db, setting, payload, current_user=current_user)


@router.delete("/{key}", response_model=dict)
def delete_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    setting = (
        db.query(AppSettings)
        .filter(AppSettings.key == key, AppSettings.is_deleted == False)
        .first()
    )
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting_crud.remove(db, setting.id, current_user=current_user)
    return {"detail": "Setting deleted successfully"}

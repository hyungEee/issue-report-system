from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.user_setting_repo import UserSettingRepository

router = APIRouter(prefix="/users/{user_id}/settings", tags=["settings"])

DbDep = Annotated[Session, Depends(get_db)]


class UserSettingRequest(BaseModel):
    email: str
    alert_enabled: bool = True
    countries: list[str] | None = None
    categories: list[str] | None = None


class UserSettingResponse(BaseModel):
    user_id: int
    email: str
    alert_enabled: bool
    countries: list[str] | None
    categories: list[str] | None


def _to_response(user_setting) -> UserSettingResponse:
    return UserSettingResponse(
        user_id=user_setting.user_id,
        email=user_setting.email,
        alert_enabled=user_setting.alert_enabled,
        countries=json.loads(user_setting.country_json) if user_setting.country_json else None,
        categories=json.loads(user_setting.category_json) if user_setting.category_json else None,
    )


@router.get("", response_model=UserSettingResponse)
def get_user_setting(user_id: int, db: DbDep):
    repo = UserSettingRepository(db)
    user_setting = repo.find_by_user_id(user_id)
    if user_setting is None:
        raise HTTPException(status_code=404, detail="유저 설정을 찾을 수 없습니다.")
    return _to_response(user_setting)


@router.put("", response_model=UserSettingResponse)
def upsert_user_setting(user_id: int, body: UserSettingRequest, db: DbDep):
    repo = UserSettingRepository(db)
    user_setting = repo.upsert(
        user_id=user_id,
        email=body.email,
        alert_enabled=body.alert_enabled,
        country_json=json.dumps(body.countries) if body.countries is not None else None,
        category_json=json.dumps(body.categories) if body.categories is not None else None,
    )
    db.commit()
    return _to_response(user_setting)


@router.delete("", status_code=204)
def delete_user_setting(user_id: int, db: DbDep):
    repo = UserSettingRepository(db)
    deleted = repo.delete_by_user_id(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="유저 설정을 찾을 수 없습니다.")
    db.commit()

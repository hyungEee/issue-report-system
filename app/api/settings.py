from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.news_targets import REGION_COUNTRY_MAP, SUPPORTED_CATEGORIES
from app.repositories.user_setting_repo import UserSettingRepository

router = APIRouter(prefix="/settings", tags=["settings"])

DbDep = Annotated[Session, Depends(get_db)]

_VALID_REGIONS = set(REGION_COUNTRY_MAP.keys())
_VALID_CATEGORIES = set(SUPPORTED_CATEGORIES)


class UserSettingRequest(BaseModel):
    email: str
    alert_enabled: bool = True
    regions: list[str] | None = None
    categories: list[str] | None = None

    @field_validator("regions")
    @classmethod
    def validate_regions(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        invalid = [r for r in v if r not in _VALID_REGIONS]
        if invalid:
            raise ValueError(f"유효하지 않은 지역: {invalid}. 가능한 값: {sorted(_VALID_REGIONS)}")
        return v

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        invalid = [c for c in v if c not in _VALID_CATEGORIES]
        if invalid:
            raise ValueError(f"유효하지 않은 카테고리: {invalid}. 가능한 값: {sorted(_VALID_CATEGORIES)}")
        return v


class UserSettingResponse(BaseModel):
    email: str
    alert_enabled: bool
    regions: list[str] | None
    categories: list[str] | None


def _to_response(user_setting) -> UserSettingResponse:
    return UserSettingResponse(
        email=user_setting.email,
        alert_enabled=user_setting.alert_enabled,
        regions=json.loads(user_setting.region_json) if user_setting.region_json else None,
        categories=json.loads(user_setting.category_json) if user_setting.category_json else None,
    )


@router.get("/{email}", response_model=UserSettingResponse)
def get_user_setting(email: str, db: DbDep):
    repo = UserSettingRepository(db)
    user_setting = repo.find_by_email(email)
    if user_setting is None:
        raise HTTPException(status_code=404, detail="유저 설정을 찾을 수 없습니다.")
    return _to_response(user_setting)


@router.put("", response_model=UserSettingResponse, status_code=201)
def upsert_user_setting(body: UserSettingRequest, db: DbDep):
    repo = UserSettingRepository(db)
    user_setting = repo.upsert(
        email=body.email,
        alert_enabled=body.alert_enabled,
        region_json=json.dumps(body.regions) if body.regions is not None else None,
        category_json=json.dumps(body.categories) if body.categories is not None else None,
    )
    db.commit()
    return _to_response(user_setting)


@router.delete("/{email}", status_code=204)
def delete_user_setting(email: str, db: DbDep):
    repo = UserSettingRepository(db)
    deleted = repo.delete_by_email(email)
    if not deleted:
        raise HTTPException(status_code=404, detail="유저 설정을 찾을 수 없습니다.")
    db.commit()

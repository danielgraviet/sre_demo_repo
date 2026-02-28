from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.schemas import ErrorResponse, HealthResponse, UserProfileResponse
from app.sentry import init_sentry
from app.services.profile_service import get_profile
from app.settings import settings

VALID_MODES = {"none", "cache_off", "slow_query", "pool_saturation", "combined"}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_sentry()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Mock SRE Service", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get(
    "/api/users/profile/{user_id}",
    response_model=UserProfileResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def get_user_profile(
    user_id: int,
    response: Response,
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    response.headers["X-Failure-Mode"] = settings.failure_mode

    try:
        profile = get_profile(user_id, db)
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e.orig))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfileResponse.model_validate(profile)


@app.post("/admin/failure-mode/{mode}")
def set_failure_mode(mode: str) -> dict:
    if settings.env != "demo":
        raise HTTPException(status_code=403, detail="Only available in demo environment")
    if mode not in VALID_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Choose from: {', '.join(sorted(VALID_MODES))}",
        )
    settings.failure_mode = mode
    sentry_sdk.set_tag("failure_mode", mode)
    return {"failure_mode": mode}

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    detail: str


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    bio: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

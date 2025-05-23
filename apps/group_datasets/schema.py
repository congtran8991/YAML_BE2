from pydantic import BaseModel, Field, StringConstraints, field_validator
from typing import Optional, Annotated, Any, List
from datetime import datetime
from apps.users.schema import UserInToken


# Define the schema for GroupDatasets
class GroupDatasetCreateRequest(BaseModel):
    code: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)
    ]
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ]
    latest_version: Optional[int] = Field(default=1, ge=1)
    created_by_id: Optional[int] = Field(default=None, ge=1)

    class Config:
        from_attributes = (
            True  # Allows SQLAlchemy models to be converted to Pydantic models
        )


class GroupDatasetUpdateRequest(BaseModel):
    id: int = Field(...)
    code: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=50),
        Field(..., description="Required code"),
    ]
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
        Field(..., description="Required code"),
    ]


class GroupDatasetResponse(BaseModel):
    id: int
    code: str
    name: str
    latest_version: int
    created_by_user: Optional[UserInToken]
    created_at: datetime

    class Config:
        from_attributes = (
            True  # Allows SQLAlchemy models to be converted to Pydantic models
        )


class GroupDatasetDelete(BaseModel):
    ids: List[int]

from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from apps.users.schema import  UserInToken


# Define the schema for GroupDatasets
class GroupDatasetCreateRequest(BaseModel):
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    latest_version: Optional[int] = Field(default=1, ge=1)
    created_by_id: Optional[int] = Field(default=None, ge=1) 

    model_config = ConfigDict(
        from_attributes=True,  # Thay cho orm_mode = True
        extra="ignore"         # Cho phép bỏ qua field không khai báo
    )


class GroupDatasetResponse(BaseModel):
    id: int
    code: str
    name: str
    latest_version: int
    created_by_user: Optional[UserInToken]
    created_at: datetime

    class Config:
        orm_mode = True  # Allows SQLAlchemy models to be converted to Pydantic models
        from_attributes = True

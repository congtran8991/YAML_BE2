from pydantic import BaseModel, Field, StringConstraints, field_validator
from typing import Optional, Annotated
from datetime import datetime

# Define the schema for GroupDatasets
class GroupDatasetCreateRequest(BaseModel):
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    latest_version: Optional[int] = Field(default=1, ge=1)
    created_by: Optional[str] = Field(default=None, max_length=50)

    class Config:
        orm_mode = True  # Allows SQLAlchemy models to be converted to Pydantic models


class GroupDatasetResponse(BaseModel):
    id: int
    code: str
    name: str
    latest_version: int
    created_by: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True  # Allows SQLAlchemy models to be converted to Pydantic models
        from_attributes = True

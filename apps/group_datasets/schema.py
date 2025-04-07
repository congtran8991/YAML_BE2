from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Define the schema for GroupDatasets
class GroupDatasetCreateRequest(BaseModel):
    code: str
    name: str
    latest_version: Optional[int] = 1
    created_by: Optional[str] = None

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

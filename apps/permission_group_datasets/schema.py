from pydantic import BaseModel, Field
from typing import Optional


class AddingPermissionRequest(BaseModel):
    id: Optional[int]
    group_dataset_id: int = Field(...)
    email: str = Field(...)
    can_view: bool = Field(...)
    can_create: bool = Field(...)
    can_edit: bool = Field(...)
    can_delete: bool = Field(...)

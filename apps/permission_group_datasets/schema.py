from pydantic import BaseModel, Field
from typing import Optional


class SimpleUser(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class AddingPermissionRequest(BaseModel):
    id: Optional[int] = None
    group_dataset_id: int = Field(...)
    email: str = Field(...)
    can_view: bool = Field(...)
    can_create: bool = Field(...)
    can_edit: bool = Field(...)
    can_delete: bool = Field(...)


class PermissionWithUser(BaseModel):
    id: int
    group_dataset_id: int
    granted_by_user_id: int
    can_view: bool
    can_create: bool
    can_edit: bool
    can_delete: bool
    granted_to_user: SimpleUser

    class Config:
        from_attributes = True

from pydantic import BaseModel, StringConstraints, ConfigDict, EmailStr
from typing import Annotated
from datetime import datetime

# Tạo alias để dùng cho string có giới hạn chiều dài và tự động trim
TrimmedStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)
]


class UserRegisterRequest(BaseModel):
    email: Annotated[EmailStr, StringConstraints(strip_whitespace=True, max_length=100)]
    hashed_password: TrimmedStr


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_supper_admin: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,  # Tự động ánh xạ từ các thuộc tính của đối tượng
        extra="ignore",  # Cho phép bỏ qua field không khai báo
    )


class UserInToken(BaseModel):
    id: int
    email: EmailStr
    is_supper_admin: bool

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    email: Annotated[EmailStr, StringConstraints(strip_whitespace=True, max_length=100)]
    hashed_password: TrimmedStr


class UserLoginResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    access_token: str
    refetch_token: str

    class Config:
        from_attributes = True


class TypePermission(BaseModel):
    can_view: bool  # quyền đầy đủ
    can_create: bool  # quyền đầy đủ
    can_edit: bool  # quyền đầy đủ
    can_delete: bool  # quyền đầy đủ

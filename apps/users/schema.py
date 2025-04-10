from pydantic import BaseModel, Field, StringConstraints, field_validator, EmailStr
from typing import Annotated
from datetime import datetime

# Tạo alias để dùng cho string có giới hạn chiều dài và tự động trim
TrimmedStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]

class UserRegisterRequest(BaseModel):
    email: Annotated[EmailStr, StringConstraints(strip_whitespace=True, max_length=100)]
    hashed_password: TrimmedStr

class UserRegisterResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
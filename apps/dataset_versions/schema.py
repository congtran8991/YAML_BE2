from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# Define the schema for GroupDatasets
class DatasetVersionCreateRequest(BaseModel):
    group_dataset_id: int = Field(..., description="ID của group dataset liên quan")
    version: int = Field(..., description="Số phiên bản dataset")
    note: Optional[str] = Field(None, description="Ghi chú cho phiên bản")
    created_by_id: Optional[int] = Field(
        None, description="ID người tạo (có thể lấy từ token)"
    )

    model_config = ConfigDict(
        from_attributes=True,  # Thay cho orm_mode = True
        extra="ignore",  # Cho phép bỏ qua field không khai báo
    )


class DatasetVersionCreateResponse(BaseModel):
    id: int
    group_dataset_id: int
    version: int
    note: Optional[str]
    created_by_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,  # Tự động ánh xạ từ các thuộc tính của đối tượng
        extra="ignore",  # Cho phép bỏ qua field không khai báo
    )

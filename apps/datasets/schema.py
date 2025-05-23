from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Optional, Annotated, Dict, Any, List
from datetime import datetime

from apps.users.schema import UserInToken
from apps.dataset_versions.schema import DatasetVersionResponse


# Define the schema for GroupDatasets
class RecordDatasetCreateRequest(BaseModel):
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ]
    input: Dict[str, Any] = Field(..., description="Input data dưới dạng JSON")
    steps: List[Dict[str, Any]] = Field(..., description="Các bước xử lý")
    output: Optional[Dict[str, Any]] = Field(  # Optional không required
        default_factory=dict, description="Output kết quả nếu có"
    )

    model_config = ConfigDict(
        from_attributes=True,  # Thay cho orm_mode = True
        extra="ignore",  # Cho phép bỏ qua field không khai báo
    )


class DatasetCreateRequest(BaseModel):
    list_dataset: List[RecordDatasetCreateRequest] = Field(
        ..., description="Danh sách dataset"
    )
    group_dataset_id: int = Field(..., description="Group dataset")


class DatasetsByGroupDatasetRequest(BaseModel):
    version: int = Field(
        ..., description="Version của dataset."
    )  # Field(...,) required mặc định

    model_config = ConfigDict(
        extra="ignore",  # Cho phép bỏ qua field không khai báo
    )


class DatasetResponse(BaseModel):
    id: int
    name: str
    input: Dict  # Có thể là dict hoặc list tùy thuộc vào cấu trúc JSON
    steps: List  # Danh sách các bước
    output: Dict
    version_id: int
    created_by_id: int
    created_at: datetime

    # Schema cho user tạo dataset (có thể lấy thông tin user khi cần thiết)
    created_by_user: Optional[
        UserInToken
    ]  # Thông tin người tạo nếu có (ví dụ: {"id": 1, "email": "user@example.com"})

    dataset_versions: Optional[DatasetVersionResponse]

    model_config = ConfigDict(
        from_attributes=True,  # Tự động ánh xạ từ các thuộc tính của đối tượng
        extra="ignore",  # Cho phép bỏ qua field không khai báo
    )

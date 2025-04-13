from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Optional, Annotated, Dict, Any, List
from datetime import datetime

# Define the schema for GroupDatasets
class DatasetCreateRequest(BaseModel):
    group_dataset_id: int = Field(..., description="ID của group dataset (foreign key)")
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    input: Dict[str, Any] = Field(..., description="Input data dưới dạng JSON")
    steps: List[Dict[str, Any]] = Field(..., description="Các bước xử lý")
    output: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Output kết quả nếu có")

    model_config = ConfigDict(
        from_attributes=True,  # Thay cho orm_mode = True
        extra="ignore"         # Cho phép bỏ qua field không khai báo
    )

# class DatasetResponse(BaseModel):
#     id: int
#     code: str
#     name: str
#     latest_version: int
#     created_by: Optional[str]
#     created_at: datetime

#     class Config:
#         orm_mode = True  # Allows SQLAlchemy models to be converted to Pydantic models
#         from_attributes = True

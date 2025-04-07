from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database.db_setting import ModelBase  # Giả sử bạn đã khai báo Base ở đây

class GroupDatasetModel(ModelBase):
    __tablename__ = "groupdatasets"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)

    latest_version = Column(Integer, default=1, nullable=False)
    
    created_by = Column(String(50))
    created_at = Column(TIMESTAMP, default="CURRENT_TIMESTAMP")

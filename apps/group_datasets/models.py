from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database.db_setting import ModelBase  # Giả sử bạn đã khai báo Base ở đây
from datetime import datetime
class GroupDatasetModel(ModelBase):
    __tablename__ = "groupdatasets"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    latest_version = Column(Integer, nullable=False, default=1)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now())

    # relationships
    permissions_group_datasets = relationship("GroupDatasetPermissionModel", back_populates="group_datasets")
    created_by_user = relationship("UserModel", back_populates="group_datasets")
    datasets = relationship("DatasetModel", back_populates="group_datasets", cascade="all, delete")



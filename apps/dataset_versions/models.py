from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database.db_setting import ModelBase  # Giả sử bạn đã khai báo Base ở đây
from datetime import datetime


class DatasetVersionModel(ModelBase):
    __tablename__ = "dataset_versions"

    id = Column(Integer, primary_key=True)
    group_dataset_id = Column(
        Integer, ForeignKey("groupdatasets.id", ondelete="CASCADE"), nullable=False
    )
    note = Column(String(100), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    version = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    created_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Quan hệ với DatasetModel
    datasets = relationship(
        "DatasetModel", back_populates="dataset_versions", cascade="all, delete"
    )
    group_datasets = relationship(
        "GroupDatasetModel", back_populates="dataset_versions", cascade="all, delete"
    )
    created_by_user = relationship("UserModel", back_populates="dataset_versions")

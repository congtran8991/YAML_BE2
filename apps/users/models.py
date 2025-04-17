from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database.db_setting import ModelBase  # Giả sử bạn đã khai báo Base ở đây
from datetime import datetime


class UserModel(ModelBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(300), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now())

    # relationships
    group_datasets = relationship("GroupDatasetModel", back_populates="created_by_user")
    datasets = relationship("DatasetModel", back_populates="created_by_user")
    dataset_versions = relationship(
        "DatasetVersionModel", back_populates="created_by_user"
    )

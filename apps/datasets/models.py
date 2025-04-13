from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_setting import ModelBase  # Giả sử bạn đã khai báo Base ở đây
from datetime import datetime
class DatasetModel(ModelBase):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    group_dataset_id = Column(Integer, ForeignKey("groupdatasets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    input = Column(JSONB, nullable=False, default=dict)
    steps = Column(JSONB, nullable=False, default=list)
    output = Column(JSONB, default=dict)
    version = Column(Integer, nullable=False, default=1)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now())


    __table_args__ = (
        UniqueConstraint('group_dataset_id', 'name', name='uq_group_name'),
    )

    group_datasets = relationship("GroupDatasetModel", back_populates="datasets")
    created_by_user = relationship("UserModel", back_populates="datasets")



   

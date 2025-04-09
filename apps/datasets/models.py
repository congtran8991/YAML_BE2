from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database.db_setting import ModelBase  # Giả sử bạn đã khai báo Base ở đây

class DatasetModel(ModelBase):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    
    group_dataset_id = Column(Integer, ForeignKey("groupdatasets.id", ondelete="CASCADE"))

    name = Column(String(100), unique=True, nullable=False)

    input = Column(JSONB, nullable=False, default=dict)
    steps = Column(JSONB, nullable=False, default=list)
    output = Column(JSONB, default=dict)

    # version = Column(Integer, nullable=False, default=1)

    created_by = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        UniqueConstraint('group_dataset_id', 'name', name='uq_group_name'),
    )

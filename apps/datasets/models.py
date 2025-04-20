from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    UniqueConstraint,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db_setting import ModelBase


class DatasetModel(ModelBase):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(
        Integer, ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(100), nullable=False)
    input = Column(JSONB, nullable=False, default=dict)
    steps = Column(JSONB, nullable=False, default=list)
    output = Column(JSONB, default=dict)
    created_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(TIMESTAMP, default=datetime.now)

    __table_args__ = (UniqueConstraint("version_id", "name", name="uq_version_name"),)

    dataset_versions = relationship("DatasetVersionModel", back_populates="datasets")
    created_by_user = relationship("UserModel", back_populates="datasets")

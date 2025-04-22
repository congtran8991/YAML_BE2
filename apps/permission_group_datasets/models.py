from sqlalchemy import Column, Integer, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db_setting import ModelBase  # Giả định bạn đã có class base


class GroupDatasetPermissionModel(ModelBase):
    __tablename__ = "groupdataset_permissions"
    __table_args__ = (
        UniqueConstraint(
            "group_dataset_id", "granted_to_user_id", name="uq_group_dataset_user"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    group_dataset_id = Column(
        Integer, ForeignKey("groupdatasets.id", ondelete="CASCADE"), nullable=False
    )
    granted_to_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )  # user nhận quyền
    can_view = Column(Boolean, default=False)
    can_create = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    granted_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # user cho quyền
    granted_at = Column(TIMESTAMP, default=datetime.now())

    __table_args__ = (
        UniqueConstraint(
            "granted_to_user_id", "group_dataset_id", name="uix_granted_user_group"
        ),
    )

    # Quan hệ (optional - giúp dễ truy cập thông tin nếu cần)
    group_datasets = relationship(
        "GroupDatasetModel", back_populates="permissions_group_datasets"
    )
    granted_to_user = relationship("UserModel", foreign_keys=[granted_to_user_id])
    granted_by_user = relationship("UserModel", foreign_keys=[granted_by_user_id])

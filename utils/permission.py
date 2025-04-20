from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.schema import UserInToken
from apps.group_datasets.fetch import fetch_group_dataset_detail
from utils.handling_errors.exception_handler import UnicornException
from fastapi import status

from apps.group_datasets.models import GroupDatasetModel
from apps.permission_group_datasets.models import GroupDatasetPermissionModel

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


async def has_permission(
    db: AsyncSession,
    group_dataset_id: int,
    user: UserInToken,
    action: str = "view",  # hoặc "edit", "delete"
):
    # 1. Kiểm tra nếu user là người tạo
    stmt = select(GroupDatasetModel).where(
        GroupDatasetModel.id == group_dataset_id,
        GroupDatasetModel.created_by_id == user.id,
    )
    result = await db.execute(stmt)
    group_dataset = result.scalar_one_or_none()

    if group_dataset:
        return True  # Là chủ sở hữu → full quyền

    # 2. Kiểm tra xem có được cấp quyền thông qua permission model không
    stmt = select(GroupDatasetPermissionModel).where(
        GroupDatasetPermissionModel.group_dataset_id == group_dataset_id,
        GroupDatasetPermissionModel.granted_to_user_id == user.id,
    )
    result = await db.execute(stmt)
    permission = result.scalar_one_or_none()

    if not permission:
        return False

    if action == "view" and permission.can_view:
        return True
    if action == "create" and permission.can_create:
        return True
    elif action == "edit" and permission.can_edit:
        return True
    elif action == "delete" and permission.can_delete:
        return True

    return False

from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.schema import UserInToken
from apps.group_datasets.fetch import fetch_group_dataset_detail
from utils.handling_errors.exception_handler import UnicornException
from fastapi import status

from apps.group_datasets.models import GroupDatasetModel
from apps.permission_group_datasets.models import GroupDatasetPermissionModel

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

import asyncio

from typing import List


async def has_permission(
    db: AsyncSession,
    group_dataset_id: int,
    user: UserInToken,
    action: str = "view",  # hoặc "edit", "delete"
):
    # 1. Kiểm tra nếu user là super admin
    if user.is_supper_admin:
        return True

    # 2. Kiểm tra xem có được cấp quyền thông qua permission model không
    stmt = select(GroupDatasetPermissionModel).where(
        GroupDatasetPermissionModel.group_dataset_id == group_dataset_id,
        GroupDatasetPermissionModel.granted_to_user_id == user.id,
    )
    result = await db.execute(stmt)
    permission = result.scalar_one_or_none()

    print("permission", permission)

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


async def process_permissions(
    db: AsyncSession, ids: List[int], user: UserInToken
) -> bool:
    tasks = [
        asyncio.create_task(
            has_permission(
                group_dataset_id=group_dataset_id, user=user, action="delete", db=db
            )
        )
        for group_dataset_id in ids
    ]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # Check xem có task nào lỗi không
    for task in done:
        if task.exception() or not task.result():
            # Cancel các task còn lại
            for p in pending:
                p.cancel()
            print(f"🚨 Task bị lỗi: {task.exception()}")
            return False  # Có lỗi => trả về False luôn

    # Nếu tất cả done ok
    return True

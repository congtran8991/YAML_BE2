from sqlalchemy.ext.asyncio import AsyncSession
from apps.permission_group_datasets.models import GroupDatasetPermissionModel
from apps.users.schema import TypePermission

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from apps.group_datasets.models import GroupDatasetModel
from apps.permission_group_datasets.schema import PermissionWithUser
from apps.users.schema import UserInToken
from utils.handling_errors.exception_handler import UnicornException
from sqlalchemy.orm import joinedload


async def grant_full_permission(
    db: AsyncSession,
    group_dataset_id: int,
    type_permission: TypePermission,
    granted_to_user_id: int,
    granted_by_user_id: int,
) -> None:
    db_permission_group_dataset = GroupDatasetPermissionModel(
        group_dataset_id=group_dataset_id,  # user nhận quyền
        granted_to_user_id=granted_to_user_id,
        can_view=type_permission.can_view,  # quyền đầy đủ
        can_create=type_permission.can_create,  # quyền đầy đủ
        can_edit=type_permission.can_edit,  # quyền đầy đủ
        can_delete=type_permission.can_delete,  # quyền đầy đủ
        granted_by_user_id=granted_by_user_id,  # user cho quyền
    )

    db.add(db_permission_group_dataset)
    return db_permission_group_dataset


async def validate_user_can_grant_permission(
    db: AsyncSession, group_dataset_id: int, user: UserInToken
):
    if user.is_supper_admin:
        return True

    stmt = select(GroupDatasetModel.created_by_id).where(
        GroupDatasetModel.id == group_dataset_id
    )
    result = await db.execute(stmt)
    owner_id = result.scalar_one_or_none()

    if owner_id is None:
        raise UnicornException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="group_dataset_not_found",
        )

    if owner_id != user.id:
        raise UnicornException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="only_creator_can_grant_permission",
        )

    return True


async def get_permissions_for_group_dataset(
    db: AsyncSession, group_dataset_id: int, user: UserInToken
):
    # Tạo câu truy vấn với điều kiện group_dataset_id và nạp người dùng được cấp quyền
    stmt = (
        select(GroupDatasetPermissionModel)
        .where(GroupDatasetPermissionModel.group_dataset_id == group_dataset_id)
        .options(
            joinedload(GroupDatasetPermissionModel.granted_to_user)
        )  # Nạp người dùng được cấp quyền
    )

    # Thực hiện truy vấn và lấy kết quả
    result = await db.execute(stmt)

    # Trả về danh sách các permission (GroupDatasetPermissionModel) cùng với thông tin người dùng
    all_permissions = result.scalars().all()

    filtered_permissions = [
        perm
        for perm in all_permissions
        if not (
            user.is_supper_admin
            or perm.granted_to_user_id == user.id  # chính user cấp cho mình
        )
    ]

    return [PermissionWithUser.model_validate(item) for item in filtered_permissions]

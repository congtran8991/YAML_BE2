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
from sqlalchemy import or_
from sqlalchemy import update, delete
from typing import List


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


async def update_permission(
    db: AsyncSession,
    id: int,
    type_permission: TypePermission,
) -> GroupDatasetPermissionModel:
    stmt = (
        update(GroupDatasetPermissionModel)
        .where(GroupDatasetPermissionModel.id == id)
        .values(
            can_view=type_permission.can_view,
            can_create=type_permission.can_create,
            can_edit=type_permission.can_edit,
            can_delete=type_permission.can_delete,
        )
    ).options(
        joinedload(GroupDatasetPermissionModel.granted_to_user)
    )  # N
    await db.execute(stmt)
    await db.commit()

    result = await db.execute(
        select(GroupDatasetPermissionModel).where(GroupDatasetPermissionModel.id == id)
    )
    updated_permission = result.scalar_one()
    return updated_permission


async def delete_permission(db: AsyncSession, ids: List[int]):
    stmt = delete(GroupDatasetPermissionModel).where(
        GroupDatasetPermissionModel.id.in_(ids)
    )
    await db.execute(stmt)
    await db.commit()


async def validate_user_permission(
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


async def validate_user_permissions_by_grant_user(
    db: AsyncSession, ids: List[int], user: UserInToken
) -> List[GroupDatasetPermissionModel]:
    # Truy vấn tất cả các permission theo ids
    result = await db.execute(
        select(GroupDatasetPermissionModel).where(
            GroupDatasetPermissionModel.id.in_(ids)
        )
    )
    permissions = result.scalars().all()

    if len(permissions) != len(ids):
        raise UnicornException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="one_or_more_permissions_not_found",
        )

    # Nếu là super admin thì được quyền xử lý tất cả
    if user.is_supper_admin:
        return permissions

    # Kiểm tra xem người dùng có phải là người cấp quyền không
    for p in permissions:
        if p.granted_by_user_id != user.id:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="only_creator_can_update_or_delete_permission",
            )

    return permissions


async def get_permissions_for_group_dataset(
    db: AsyncSession, group_dataset_id: int, user: UserInToken
):
    # Tạo câu truy vấn với điều kiện group_dataset_id và nạp người dùng được cấp quyền
    stmt = (
        select(GroupDatasetPermissionModel)
        .where(
            GroupDatasetPermissionModel.group_dataset_id == group_dataset_id,
            or_(
                GroupDatasetPermissionModel.granted_by_user_id == user.id,
                user.is_supper_admin,
            ),
            GroupDatasetPermissionModel.granted_by_user_id
            != GroupDatasetPermissionModel.granted_to_user_id,
        )
        .options(
            joinedload(GroupDatasetPermissionModel.granted_to_user)
        )  # Nạp người dùng được cấp quyền
    )

    # Thực hiện truy vấn và lấy kết quả
    result = await db.execute(stmt)

    # Trả về danh sách các permission (GroupDatasetPermissionModel) cùng với thông tin người dùng
    all_permissions = result.scalars().all()
    print("-----------------------------error", user.id)
    # print(
    #     json.dumps(
    #         [
    #             PermissionWithUser.model_validate(perm).model_dump()
    #             for perm in all_permissions
    #         ],
    #         indent=2,
    #     )
    # )

    return [PermissionWithUser.model_validate(item) for item in all_permissions]


def parse_delete_permission_request(requestBody: dict):
    try:
        _group_dataset_id = int(requestBody["group_dataset_id"])
        _ids = requestBody["ids"]
        _ids = [int(i) for i in _ids]
        if not isinstance(_ids, list) or not all(isinstance(i, int) for i in _ids):
            raise ValueError("ids must be a list of integers")
        return _group_dataset_id, _ids
    except KeyError as e:
        raise ValueError(f"Missing field in request body: {e}")
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid request data: {e}")

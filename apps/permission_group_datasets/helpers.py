from sqlalchemy.ext.asyncio import AsyncSession
from apps.permission_group_datasets.models import GroupDatasetPermissionModel
from apps.users.schema import TypePermission


async def grant_full_permission(
    db: AsyncSession,
    user_id: int,
    group_dataset_id: int,
    type_permission: TypePermission,
) -> None:
    db_permission_group_dataset = GroupDatasetPermissionModel(
        group_dataset_id=group_dataset_id,  # user nhận quyền
        granted_to_user_id=user_id,
        can_view=type_permission.can_view,  # quyền đầy đủ
        can_create=type_permission.can_create,  # quyền đầy đủ
        can_edit=type_permission.can_edit,  # quyền đầy đủ
        can_delete=type_permission.can_delete,  # quyền đầy đủ
        granted_by_user_id=user_id,  # user cho quyền
    )

    db.add(db_permission_group_dataset)

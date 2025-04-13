from sqlalchemy.ext.asyncio import AsyncSession
from apps.permission_group_datasets.models import GroupDatasetPermissionModel

async def grant_full_permission(db: AsyncSession, user_id: int, group_dataset_id: int ) -> None:
    db_permission_group_dataset = GroupDatasetPermissionModel(
            group_dataset_id = group_dataset_id,
            granted_to_user_id = user_id, 
            can_view = True,  # quyền đầy đủ
            can_edit = True,  # quyền đầy đủ
            can_delete = True,  # quyền đầy đủ
            granted_by_user_id = user_id
        )
    
    db.add(db_permission_group_dataset)
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from apps.group_datasets.models import GroupDatasetModel
from apps.group_datasets.schema import GroupDatasetResponse
from apps.users.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


async def fetch_group_dataset_detail(
    group_dataset_id: int, db: AsyncSession
) -> GroupDatasetResponse:
    stmt = (
        select(GroupDatasetModel)
        .where(GroupDatasetModel.id == group_dataset_id)
        .options(
            joinedload(GroupDatasetModel.created_by_user),
            joinedload(GroupDatasetModel.datasets),
        )
    )
    result = await db.execute(stmt)
    group_dataset = result.scalar_one_or_none()

    if not group_dataset:
        raise HTTPException(status_code=404, detail="GroupDataset not found")

    created_by = UserModel(group_dataset.created_by_user)
    user_data = None
    if created_by:
        user_data = {
            "id": created_by.id,
            "email": created_by.email,
            "created_at": created_by.created_at,
        }

    return GroupDatasetResponse.model_validate(
        {
            "id": group_dataset.id,
            "code": group_dataset.code,
            "name": group_dataset.name,
            "latest_version": group_dataset.latest_version,
            "created_by_user": user_data,
            "created_at": group_dataset.created_at,
        }
    )

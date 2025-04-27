from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import update, delete
from apps.group_datasets.models import GroupDatasetModel
from apps.dataset_versions.models import DatasetVersionModel
from apps.group_datasets.schema import GroupDatasetResponse
from apps.users.schema import UserInToken
from apps.users.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from typing import List, Optional


async def fetch_group_dataset_detail(
    group_dataset_id: int, db: AsyncSession, user: UserInToken
) -> GroupDatasetResponse:
    print("-------------------fetch_group_dataset_detail-------------------")
    stmt = (
        select(GroupDatasetModel)
        .where(
            GroupDatasetModel.id == group_dataset_id,
            GroupDatasetModel.created_by_id == user.id,
        )
        .options(joinedload(GroupDatasetModel.created_by_user))
    )
    result = await db.execute(stmt)
    group_dataset = result.scalar_one_or_none()

    if not group_dataset:
        raise HTTPException(status_code=404, detail="GroupDataset not found")

    created_by = group_dataset.created_by_user
    user_data = None
    if created_by:
        user_data = {
            "id": created_by.id,
            "email": created_by.email,
            "is_supper_admin": created_by.is_supper_admin,
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


async def update_latest_version_group_dataset(
    id: int, latest_version: int, db: AsyncSession
) -> bool:
    stmt = (
        update(GroupDatasetModel)
        .where(GroupDatasetModel.id == id)
        .values(latest_version=latest_version)
        .execution_options(synchronize_session="fetch")
    )

    await db.execute(stmt)

    return True


async def update_info_group_dataset(
    id: int, code: str, name: str, db: AsyncSession
) -> GroupDatasetResponse:
    stmt = (
        update(GroupDatasetModel)
        .where(GroupDatasetModel.id == id)
        .values(code=code, name=name)
        .execution_options(synchronize_session="fetch")
    )

    await db.execute(stmt)
    await db.commit()

    result = await db.execute(
        select(GroupDatasetModel).where(GroupDatasetModel.id == id)
    )

    record_group_dataset = result.scalar_one()
    return GroupDatasetResponse.model_validate(record_group_dataset)


async def delete_group_datasets(db: AsyncSession, ids: List[int], commit: bool = False):
    stmt = delete(GroupDatasetModel).where(GroupDatasetModel.id.in_(ids))
    await db.execute(stmt)

    if commit:
        await db.commit()


async def get_group_dataset_id_by_version_id(
    db: AsyncSession, version_id: int
) -> Optional[int]:
    result = await db.scalar(
        select(DatasetVersionModel.group_dataset_id).where(
            DatasetVersionModel.id == version_id
        )
    )
    return result

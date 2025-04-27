# services/dataset_version_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from apps.dataset_versions.models import DatasetVersionModel
from apps.users.schema import UserInToken
from apps.dataset_versions.schema import (
    DatasetVersionCreateRequest,
    DatasetVersionResponse,
)
from typing import List

from sqlalchemy import delete, update, select


async def create_dataset_version(
    db: AsyncSession,
    data: DatasetVersionCreateRequest,
) -> DatasetVersionResponse:
    print("-----------------create_dataset_version", data)
    new_version = DatasetVersionModel(
        group_dataset_id=data.group_dataset_id,
        version=data.version,
        created_by_id=data.created_by_id,
    )

    db.add(new_version)
    await db.flush()
    await db.refresh(new_version)

    return DatasetVersionResponse.model_validate(new_version)


async def delete_dataset_version(
    db: AsyncSession, ids: List[int], commit: bool = False
):
    if not ids:
        return

    stmt = delete(DatasetVersionModel).where(DatasetVersionModel.id.in_(ids))
    await db.execute(stmt)

    if commit:
        await db.commit()


async def update_note_in_dataset_version(
    db: AsyncSession, version_id: int, note: str, commit: bool = False
) -> None:
    stmt = (
        update(DatasetVersionModel)
        .where(DatasetVersionModel.id == version_id)
        .values(note=note)
    )
    await db.execute(stmt)

    if commit:
        await db.commit()

    result = await db.execute(
        select(DatasetVersionModel).where(DatasetVersionModel.id == version_id)
    )
    updated_version = result.scalar_one_or_none()

    return DatasetVersionResponse.model_validate(updated_version)

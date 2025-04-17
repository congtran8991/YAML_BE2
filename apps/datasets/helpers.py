from apps.datasets.models import DatasetModel
from apps.datasets.schema import DatasetResponse
from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.schema import UserInToken
from apps.group_datasets.fetch import (
    update_latest_version_group_dataset,
)
from apps.datasets.schema import RecordDatasetCreateRequest
from typing import List
from fastapi.encoders import jsonable_encoder


async def add_and_update_version_dataset(
    group_dataset_id: int,
    version_id: int,
    latest_version: int,
    list_dataset: List[RecordDatasetCreateRequest],
    db: AsyncSession,
    user: UserInToken,
) -> List[DatasetResponse]:
    await update_latest_version_group_dataset(
        id=group_dataset_id, db=db, latest_version=latest_version
    )

    created = []
    for req in list_dataset:
        dataset = DatasetModel(
            version_id=version_id,
            name=req.name,
            input=req.input,
            steps=req.steps,
            output=req.output,
            created_by_id=user.id,
        )
        db.add(dataset)
        created.append(dataset)

    await db.flush()
    for dataset in created:
        await db.refresh(dataset)

    return created

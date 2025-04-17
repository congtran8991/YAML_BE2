# services/dataset_version_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from apps.dataset_versions.models import DatasetVersionModel
from apps.users.schema import UserInToken
from apps.dataset_versions.schema import (
    DatasetVersionCreateRequest,
    DatasetVersionCreateResponse,
)


async def create_dataset_version(
    db: AsyncSession,
    data: DatasetVersionCreateRequest,
) -> DatasetVersionCreateResponse:
    print("-----------------create_dataset_version", data)
    new_version = DatasetVersionModel(
        group_dataset_id=data.group_dataset_id,
        version=data.version,
        created_by_id=data.created_by_id,
    )

    db.add(new_version)
    await db.flush()
    await db.refresh(new_version)

    return DatasetVersionCreateResponse.model_validate(new_version)

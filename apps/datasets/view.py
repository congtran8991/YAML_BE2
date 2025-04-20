from typing import TYPE_CHECKING, List, Any, ByteString
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.datasets.schema import (
    DatasetCreateRequest,
    DatasetsByGroupDatasetRequest,
    DatasetResponse,
)
from apps.datasets.service import (
    create_multiple_dataset,
    get_datasets_by_dataset_version_service,
)
from database.postgresql import get_db

# if TYPE_CHECKING:
#     from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/api/datasets", response_model=Any)
async def created_dataset(
    request: Request,
    requestBody: DatasetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    return await create_multiple_dataset(db=db, user=user, requestBody=requestBody)


@router.get(
    "/api/datasets/group-dataset/{group_dataset_id}/dataset-version/{dataset_version_id}",
    response_model=Any,
    tags=["datasets"],
)
async def get_dataset_by_dataset_version(
    request: Request,
    group_dataset_id: int,
    dataset_version_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[DatasetResponse]:
    user = request.state.user
    return await get_datasets_by_dataset_version_service(
        db=db,
        dataset_version_id=dataset_version_id,
        group_dataset_id=group_dataset_id,
        user=user,
    )


# @router.get(
#     "/api/datasets/group-dataset/{group_dataset_id}",
#     response_model=Any,
#     tags=["datasets"],
# )
# async def get_dataset_by_group_dataset(
#     group_dataset_id: int,
#     version: int,
#     db: AsyncSession = Depends(get_db),
# ) -> List[DatasetResponse]:
#     return await get_datasets_by_group_dataset_id(
#         db=db, group_dataset_id=group_dataset_id, version=version
#     )

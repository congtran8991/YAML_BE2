from typing import TYPE_CHECKING, List, Any
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from apps.dataset_versions.service import get_version_dataset_by_group_dataset_service

from apps.datasets.schema import (
    DatasetCreateRequest,
    DatasetsByGroupDatasetRequest,
    DatasetResponse,
)

from database.postgresql import get_db


router = APIRouter()


@router.get(
    "/api/dataset-version/group-dataset/{group_dataset_id}",
    response_model=Any,
    tags=["dataset-version"],
)
async def get_version_dataset_by_group_dataset(
    request: Request,
    group_dataset_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[DatasetResponse]:
    user = request.state.user
    return await get_version_dataset_by_group_dataset_service(
        db=db, group_dataset_id=group_dataset_id, user=user
    )

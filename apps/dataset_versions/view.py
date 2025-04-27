from typing import TYPE_CHECKING, List, Any
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from apps.dataset_versions.service import (
    get_version_dataset_by_group_dataset_service,
    delete_group_datasets_version_service,
    update_group_dataset_version_service,
)

from apps.dataset_versions.schema import DatasetVersionDelete, DatasetVersionUpdate
from apps.datasets.schema import (
    DatasetResponse,
)

from utils.common import validate_list_ids

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


@router.delete(
    "/api/dataset-version/group-dataset/{group_dataset_id}", response_model=Any
)
async def delete_dataset_version(
    request: Request,
    group_dataset_id: int,
    db: AsyncSession = Depends(get_db),
):
    ids = request.query_params.getlist("ids")  # Lấy tất cả giá trị của tham số "ids"

    _ids = validate_list_ids(ids=ids)
    # Log thông tin request để kiểm tra

    # Lấy thông tin người dùng từ request
    user = request.state.user

    # Gọi service xử lý xóa quyền
    return await delete_group_datasets_version_service(
        db=db,
        user=user,
        requestBody=DatasetVersionDelete(group_dataset_id=group_dataset_id, ids=_ids),
    )


@router.put("/api/dataset-version/group-dataset/{group_dataset_id}", response_model=Any)
async def update_dataset_version(
    request: Request,
    group_dataset_id: int,
    requestBody: DatasetVersionUpdate,
    db: AsyncSession = Depends(get_db),
):

    # Log thông tin request để kiểm tra

    # Lấy thông tin người dùng từ request
    user = request.state.user

    # Gọi service xử lý xóa quyền
    return await update_group_dataset_version_service(
        db=db, user=user, group_dataset_id=group_dataset_id, requestBody=requestBody
    )

from typing import TYPE_CHECKING, List, Any, ByteString
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


from apps.permission_group_datasets.schema import AddingPermissionRequest
from apps.permission_group_datasets.service import (
    adding_permission_service,
    get_permissions_for_group_dataset_service,
)
from database.postgresql import get_db

# if TYPE_CHECKING:
#     from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/api/permission-group-datasets/group-dataset/{group_dataset_id}",
    response_model=Any,
)
async def get_permissions_for_group_dataset_view(
    request: Request,
    group_dataset_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    return await get_permissions_for_group_dataset_service(
        db=db, user=user, group_dataset_id=group_dataset_id
    )


@router.post("/api/permission-group-datasets", response_model=Any)
async def adding_permission(
    request: Request,
    requestBody: AddingPermissionRequest,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    return await adding_permission_service(db=db, user=user, requestBody=requestBody)

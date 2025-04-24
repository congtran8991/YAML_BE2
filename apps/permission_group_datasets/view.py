from typing import Any
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from apps.permission_group_datasets.schema import (
    AddPermissionRequest,
    UpdatePermissionRequest,
    DeletePermissionRequest,
)
from apps.permission_group_datasets.service import (
    add_permission_service,
    update_permission_service,
    delete_permission_service,
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
async def add_permission(
    request: Request,
    requestBody: AddPermissionRequest,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    return await add_permission_service(db=db, user=user, requestBody=requestBody)


@router.put("/api/permission-group-datasets", response_model=Any)
async def update_permission(
    request: Request,
    requestBody: UpdatePermissionRequest,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    return await update_permission_service(db=db, user=user, requestBody=requestBody)


@router.delete("/api/permission-group-datasets", response_model=Any)
async def delete_permission(
    request: Request,
    # requestBody: DeletePermissionRequest,
    db: AsyncSession = Depends(get_db),
):
    group_dataset_id = request.query_params.get("group_dataset_id")
    ids = request.query_params.getlist("ids")  # Lấy tất cả giá trị của tham số "ids"
    # Log thông tin request để kiểm tra

    # Lấy thông tin người dùng từ request
    user = request.state.user

    # Gọi service xử lý xóa quyền
    return await delete_permission_service(
        db=db, user=user, requestBody={"group_dataset_id": group_dataset_id, "ids": ids}
    )

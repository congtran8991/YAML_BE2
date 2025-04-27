from typing import List
from apps.datasets.schema import DatasetCreateRequest
from apps.datasets.models import DatasetModel
from apps.users.schema import UserInToken
from apps.dataset_versions.helpers import create_dataset_version
from apps.dataset_versions.schema import DatasetVersionCreateRequest

from apps.group_datasets.fetch import (
    fetch_group_dataset_detail,
    update_latest_version_group_dataset,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import selectinload


from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from apps.group_datasets.schema import GroupDatasetResponse
from apps.datasets.helpers import add_and_update_version_dataset
from apps.users.schema import UserInToken

from utils.response import ResponseErrUtils
from utils.handling_errors.exception_handler import UnicornException
from utils.permission import has_permission


async def get_datasets_by_dataset_version_service(
    dataset_version_id: int, group_dataset_id: int, db: AsyncSession, user: UserInToken
):
    try:
        _is_permission = has_permission(
            db=db, group_dataset_id=group_dataset_id, user=user, action="view"
        )

        if not _is_permission:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="you_do_not_have_access",
            )

        _dataset_version_id = dataset_version_id

        stmt = (
            select(DatasetModel)
            .options(
                selectinload(DatasetModel.created_by_user),
                selectinload(DatasetModel.dataset_versions),
            )
            .where(
                DatasetModel.version_id == _dataset_version_id,
            )
        )
        result = await db.execute(stmt)
        list_dataset_in_dataset_versions = result.scalars().all()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Get data successfully",
                    "data": list_dataset_in_dataset_versions,
                }
            ),
        )
    except SQLAlchemyError as err:
        print("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except UnicornException as err:
        print("------error", err)
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except Exception as err:
        print("------error", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)


async def create_multiple_dataset(
    user: UserInToken, requestBody: DatasetCreateRequest, db: AsyncSession
):

    try:

        _list_dataset = requestBody.list_dataset
        _group_dataset_id = requestBody.group_dataset_id

        _is_permission = await has_permission(
            db=db, group_dataset_id=_group_dataset_id, user=user, action="create"
        )

        if not _is_permission:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="you_do_not_have_access",
            )

        if len(_list_dataset) == 0:
            raise UnicornException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Danh sách dataset của group_dataset không đúng forrmat",
            )

        _group_dataset = await fetch_group_dataset_detail(
            group_dataset_id=_group_dataset_id, db=db, user=user
        )

        if not _group_dataset:
            raise UnicornException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="group_dataset_not_found",
            )

        _group_dataset = GroupDatasetResponse.model_validate(_group_dataset)

        _latest_version = _group_dataset.latest_version

        if _latest_version < 0:
            raise UnicornException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="latest_version_must_be_greater_than_0",
            )

        _data_create_dataset_version = {
            "group_dataset_id": _group_dataset_id,
            "version": _latest_version + 1,
            "created_by_id": user.id,
        }

        _dataset_version = await create_dataset_version(
            db=db, data=DatasetVersionCreateRequest(**_data_create_dataset_version)
        )

        print("-------------dataset_version-------------")

        created_dataset = await add_and_update_version_dataset(
            version_id=_dataset_version.id,
            group_dataset_id=_group_dataset_id,
            latest_version=_latest_version + 1,
            list_dataset=_list_dataset,
            db=db,
            user=user,
        )

        await db.commit()
        for dataset in created_dataset:
            await db.refresh(dataset)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Create data successfully",
                    "data": [jsonable_encoder(d) for d in created_dataset],
                }
            ),
        )

    except SQLAlchemyError as err:
        print("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except UnicornException as err:
        print("------error", err)
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except Exception as err:
        print("------error", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)

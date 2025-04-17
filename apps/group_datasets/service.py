from typing import List
from apps.group_datasets.schema import GroupDatasetResponse, GroupDatasetCreateRequest
from apps.users.schema import UserInToken
from apps.group_datasets.models import GroupDatasetModel
from apps.group_datasets.fetch import fetch_group_dataset_detail
from apps.users.models import UserModel
from apps.users.schema import UserResponse
from apps.permission_group_datasets.helpers import grant_full_permission
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
import logging

from fastapi.responses import JSONResponse
from utils.handling_errors.exception_handler import UnicornException


from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from utils.response import ResponseErrUtils, ResponseCreateSuccess


async def get_all_group_datasets(db: AsyncSession) -> List[GroupDatasetResponse]:
    try:
        stmt = select(GroupDatasetModel).options(
            joinedload(GroupDatasetModel.created_by_user)
        )
        result = await db.execute(stmt)
        list_group_datasets = result.scalars().all()

        db_group_dataset = group_datasets_filtered = []
        for dataset in list_group_datasets:
            created_by_user = None
            if dataset.created_by_user:
                created_by_user = UserResponse.model_validate(dataset.created_by_user)
                # Bỏ trường hashed_password
                user_data = {
                    "id": created_by_user.id,
                    "email": created_by_user.email,
                    "created_at": created_by_user.created_at,
                }
            else:
                user_data = None

            group_datasets_filtered.append(
                {
                    "id": dataset.id,
                    "code": dataset.code,
                    "name": dataset.name,
                    "latest_version": dataset.latest_version,
                    "created_by_user": user_data,
                    "created_at": dataset.created_at,
                }
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Get data successfully",
                    "data": db_group_dataset,
                }
            ),
        )

    except SQLAlchemyError as err:
        return await ResponseErrUtils.error_DB(err)

    except Exception as err:
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        return await ResponseErrUtils.error_Other(err)


async def get_group_dataset_detail(
    group_dataset_id: int, db: AsyncSession
) -> GroupDatasetResponse:
    try:
        _group_dataset = await fetch_group_dataset_detail(
            group_dataset_id=group_dataset_id, db=db
        )
        if not _group_dataset:
            raise UnicornException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="group_dataset_not_found",
            )
        return _group_dataset

    except UnicornException as err:
        print("------error", err)
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except SQLAlchemyError as err:
        print("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except Exception as err:
        print("------error ", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)


async def create_group_dataset(
    user: UserInToken, requestBody: GroupDatasetCreateRequest, db: AsyncSession
) -> JSONResponse:
    db_group_dataset = None
    try:
        db_group_dataset = GroupDatasetModel(
            code=requestBody.code,
            name=requestBody.name,
            # latest_version = 0,
            created_by_id=user.id,
        )

        db.add(db_group_dataset)
        await db.flush()

        await grant_full_permission(
            db=db,
            user_id=user.id,
            group_dataset_id=db_group_dataset.id,
        )

        await db.commit()
        await db.refresh(db_group_dataset, attribute_names=["created_by_user"])

        created_by_user = UserResponse.model_validate(db_group_dataset.created_by_user)

        response_data = GroupDatasetResponse(
            id=db_group_dataset.id,
            code=db_group_dataset.code,
            name=db_group_dataset.name,
            latest_version=db_group_dataset.latest_version,
            created_by_user=user,  # Trả về thông tin đầy đủ của user
            created_at=db_group_dataset.created_at,
        )

        return await ResponseCreateSuccess.success_created(
            data=response_data.model_dump()
        )

    except SQLAlchemyError as err:
        logging.exception("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except Exception as err:
        logging.exception("------error", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)

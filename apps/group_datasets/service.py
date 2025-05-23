from typing import List
from apps.group_datasets.schema import (
    GroupDatasetResponse,
    GroupDatasetCreateRequest,
    GroupDatasetUpdateRequest,
    GroupDatasetDelete,
)
from apps.users.schema import UserInToken
from apps.group_datasets.models import GroupDatasetModel
from apps.permission_group_datasets.models import GroupDatasetPermissionModel
from apps.group_datasets.fetch import (
    fetch_group_dataset_detail,
    update_info_group_dataset,
    delete_group_datasets,
)
from apps.users.schema import UserResponse, TypePermission
from apps.permission_group_datasets.helpers import (
    grant_full_permission,
    delete_permission_by_group_dataset_id,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
import logging

from fastapi.responses import JSONResponse
from utils.handling_errors.exception_handler import UnicornException


from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from utils.response import ResponseErrUtils, ResponseSuccess
from utils.permission import has_permission, process_permissions


async def get_all_group_datasets(
    db: AsyncSession, user: UserInToken
) -> List[GroupDatasetResponse]:
    try:
        subquery = select(GroupDatasetPermissionModel.group_dataset_id).where(
            GroupDatasetPermissionModel.granted_to_user_id == user.id,
            GroupDatasetPermissionModel.can_view == True,
        )
        stmt = (
            select(GroupDatasetModel)
            .options(joinedload(GroupDatasetModel.created_by_user))
            .where(
                or_(
                    user.is_supper_admin == True,
                    GroupDatasetModel.created_by_id == user.id,
                    GroupDatasetModel.id.in_(subquery),
                )
            )
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
    group_dataset_id: int, db: AsyncSession, user: UserInToken
) -> GroupDatasetResponse:
    try:
        _group_dataset = await fetch_group_dataset_detail(
            group_dataset_id=group_dataset_id, db=db, user=user
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
            granted_by_user_id=user.id,
            granted_to_user_id=user.id,
            group_dataset_id=db_group_dataset.id,
            type_permission=TypePermission(
                can_view=True, can_create=True, can_edit=True, can_delete=True
            ),
        )

        await db.commit()
        await db.refresh(db_group_dataset, attribute_names=["created_by_user"])

        # created_by_user = UserResponse.model_validate(db_group_dataset.created_by_user)

        response_data = GroupDatasetResponse(
            id=db_group_dataset.id,
            code=db_group_dataset.code,
            name=db_group_dataset.name,
            latest_version=db_group_dataset.latest_version,
            created_by_user=user,  # Trả về thông tin đầy đủ của user
            created_at=db_group_dataset.created_at,
        )

        return await ResponseSuccess.success_created(data=response_data.model_dump())

    except SQLAlchemyError as err:
        logging.exception("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except UnicornException as err:
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except Exception as err:
        logging.exception("------error", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)


async def update_group_dataset_service(
    user: UserInToken, requestBody: GroupDatasetUpdateRequest, db: AsyncSession
):
    try:
        _id = requestBody.id
        _code = requestBody.code
        _name = requestBody.name

        _is_permission = has_permission(
            db=db, group_dataset_id=_id, user=user, action="view"
        )

        if not _is_permission:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="you_do_not_have_access",
            )

        record_group_dataset = await update_info_group_dataset(
            db=db, id=_id, code=_code, name=_name
        )

        return await ResponseSuccess.success_update(data=record_group_dataset)

    except SQLAlchemyError as err:
        logging.exception("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except UnicornException as err:
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except Exception as err:
        logging.exception("------error", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)


async def delete_group_datasets_service(
    user: UserInToken, requestBody: GroupDatasetDelete, db: AsyncSession
):
    try:

        _ids = requestBody.ids

        _is_permission = await process_permissions(db=db, user=user, ids=_ids)

        if not _is_permission:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="you_do_not_have_access",
            )

        await delete_permission_by_group_dataset_id(db=db, ids=_ids)

        await delete_group_datasets(db=db, ids=_ids)

        await db.commit()

        return await ResponseSuccess.success_delete(True)

    except SQLAlchemyError as err:
        logging.exception("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except UnicornException as err:
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except Exception as err:
        logging.exception("------error", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)

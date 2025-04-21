from typing import List
from apps.group_datasets.schema import GroupDatasetResponse, GroupDatasetCreateRequest
from apps.users.schema import UserInToken
from apps.group_datasets.models import GroupDatasetModel
from apps.permission_group_datasets.models import GroupDatasetPermissionModel
from apps.permission_group_datasets.schema import AddingPermissionRequest
from apps.group_datasets.fetch import fetch_group_dataset_detail
from apps.users.models import UserModel
from apps.users.schema import UserResponse, TypePermission
from apps.permission_group_datasets.helpers import grant_full_permission
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

from utils.response import ResponseErrUtils, ResponseCreateSuccess
from utils.permission import has_permission


async def adding_permission_service(
    user: UserInToken, requestBody: AddingPermissionRequest, db: AsyncSession
) -> JSONResponse:

    try:
        db_permission = await grant_full_permission(
            db=db,
            user_id=user.id,
            group_dataset_id=requestBody.group_dataset_id,
            type_permission=TypePermission(
                can_view=requestBody.can_view,
                can_create=requestBody.can_create,
                can_edit=requestBody.can_create,
                can_delete=requestBody.can_delete,
            ),
        )

        await db.commit()
        await db.refresh(db_permission)

        # created_by_user = UserResponse.model_validate(db_group_dataset.created_by_user)

        return await ResponseCreateSuccess.success_created(data=True)

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

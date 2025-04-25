from apps.users.schema import UserInToken
from apps.permission_group_datasets.schema import (
    AddPermissionRequest,
    UpdatePermissionRequest,
    DeletePermissionRequest,
)
from apps.users.schema import TypePermission
from apps.permission_group_datasets.helpers import (
    grant_full_permission,
    validate_user_permission,
    get_permissions_for_group_dataset,
    update_permission,
    validate_user_permissions_by_grant_user,
    delete_permission,
    parse_delete_permission_request,
)

from apps.users.helpers import get_user_by_identifier
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from utils.handling_errors.exception_handler import UnicornException
from fastapi.encoders import jsonable_encoder

from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from utils.response import ResponseErrUtils, ResponseSuccess
from sqlalchemy.exc import IntegrityError
from utils.permission import has_permission


async def get_permissions_for_group_dataset_service(
    db: AsyncSession, group_dataset_id: int, user: UserInToken
):
    try:
        _is_permission = await has_permission(
            db=db, group_dataset_id=group_dataset_id, user=user, action="view"
        )

        if not _is_permission:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="you_do_not_have_access",
            )

        list_permission = await get_permissions_for_group_dataset(
            db=db, group_dataset_id=group_dataset_id, user=user
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Get data successfully",
                    "data": list_permission,
                }
            ),
        )

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


async def add_permission_service(
    user: UserInToken, requestBody: AddPermissionRequest, db: AsyncSession
) -> JSONResponse:

    try:
        # Kiểm tra người cho quyền có phải là người tạo group dataset hoặc là super_admin hay không
        await validate_user_permission(
            db=db, group_dataset_id=requestBody.group_dataset_id, user=user
        )

        granted_to_user = await get_user_by_identifier(
            db=db, identifier=requestBody.email
        )

        db_permission = await grant_full_permission(
            db=db,
            granted_by_user_id=user.id,
            granted_to_user_id=granted_to_user.id,
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

        return await ResponseSuccess.success_created(data=True)

    except IntegrityError as e:
        # Xử lý lỗi khi vi phạm unique constraint
        logging.exception("IntegrityError: Duplicate permission")
        raise HTTPException(
            status_code=400,
            detail="Permission already granted for this user and dataset",
        )

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


async def update_permission_service(
    user: UserInToken, requestBody: UpdatePermissionRequest, db: AsyncSession
) -> JSONResponse:
    try:
        # Kiểm tra người cho quyền có phải là người tạo group dataset hoặc là super_admin hay không
        await validate_user_permission(
            db=db, group_dataset_id=requestBody.group_dataset_id, user=user
        )

        await validate_user_permissions_by_grant_user(
            db=db, ids=[requestBody.id], user=user
        )

        updated_permission = await update_permission(
            db=db,
            id=requestBody.id,
            type_permission=TypePermission(
                can_view=requestBody.can_view,
                can_create=requestBody.can_create,
                can_edit=requestBody.can_create,
                can_delete=requestBody.can_delete,
            ),
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Permission updated successfully.",
                    "data": updated_permission,
                }
            ),
        )

    except IntegrityError as e:
        # Xử lý lỗi khi vi phạm unique constraint
        logging.exception("IntegrityError: Duplicate permission")
        raise HTTPException(
            status_code=400,
            detail="Permission already granted for this user and dataset",
        )

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


async def delete_permission_service(user: UserInToken, requestBody, db: AsyncSession):
    try:

        _group_dataset_id, _ids = parse_delete_permission_request(requestBody)
        await validate_user_permission(
            db=db, group_dataset_id=_group_dataset_id, user=user
        )

        await validate_user_permissions_by_grant_user(db=db, ids=_ids, user=user)

        await delete_permission(db=db, ids=_ids)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Delete is success",
                    "data": True,
                }
            ),
        )

    except IntegrityError as e:
        # Xử lý lỗi khi vi phạm unique constraint
        logging.exception("IntegrityError: Duplicate permission")
        raise HTTPException(
            status_code=400,
            detail="Permission already granted for this user and dataset",
        )

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

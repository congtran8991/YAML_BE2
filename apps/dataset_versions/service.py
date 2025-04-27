from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from apps.dataset_versions.models import DatasetVersionModel
from apps.dataset_versions.schema import DatasetVersionDelete

from sqlalchemy.orm import selectinload
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status

from sqlalchemy.exc import SQLAlchemyError
from utils.response import ResponseErrUtils
from utils.handling_errors.exception_handler import UnicornException
from apps.users.schema import UserInToken

from utils.permission import has_permission, process_permissions

from apps.dataset_versions.helpers import delete_dataset_version

from utils.response import ResponseErrUtils, ResponseSuccess


async def get_version_dataset_by_group_dataset_service(
    db=AsyncSession, group_dataset_id=int, user=UserInToken
):
    try:
        _group_dataset_id = group_dataset_id

        _is_permission = await has_permission(
            db=db, group_dataset_id=group_dataset_id, user=user, action="view"
        )

        if not _is_permission:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="you_do_not_have_access",
            )

        stmt = (
            select(DatasetVersionModel)
            .options(
                selectinload(DatasetVersionModel.created_by_user),
                selectinload(DatasetVersionModel.group_datasets),
            )
            .where(
                DatasetVersionModel.group_dataset_id == _group_dataset_id,
                DatasetVersionModel.created_by_id == user.id,
            )
        )
        result = await db.execute(stmt)

        list_dataset_version = result.scalars().all()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Get data successfully",
                    "data": list_dataset_version,
                }
            ),
        )
    except SQLAlchemyError as err:
        print("------error1 get_version_dataset_by_group_dataset_service-------", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except UnicornException as err:
        print("------error2 get_version_dataset_by_group_dataset_service--------", err)
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except Exception as err:
        print("------error3 get_version_dataset_by_group_dataset_service---------", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)


async def delete_group_datasets_version_service(
    user: UserInToken, requestBody: DatasetVersionDelete, db: AsyncSession
):
    try:

        _group_dataset_id = requestBody.group_dataset_id
        _version_ids = requestBody.ids

        group_dataset_ids_in_db = await db.scalars(
            select(DatasetVersionModel.group_dataset_id).where(
                DatasetVersionModel.id.in_(_version_ids)
            )
        )

        if set(group_dataset_ids_in_db) != {_group_dataset_id}:
            raise Exception("Invalid groupDatasetId")

        _is_permission = await process_permissions(
            db=db, user=user, ids=[_group_dataset_id]
        )

        if not _is_permission:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="you_do_not_have_access",
            )

        await delete_dataset_version(db=db, ids=_version_ids, commit=False)

        await db.commit()

        return await ResponseSuccess.success_delete(True)

    except SQLAlchemyError as err:
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except UnicornException as err:
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except Exception as err:
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseErrUtils.error_Other(err)

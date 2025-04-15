from typing import List
from apps.datasets.schema import DatasetCreateRequest
from apps.datasets.models import DatasetModel

from apps.group_datasets.fetch import fetch_group_dataset_detail

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import selectinload


from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from utils.response import ResponseErrUtils
from utils.handling_errors.exception_handler import UnicornException


async def get_datasets_by_group_dataset_id(
    group_dataset_id: int,
    version: int,
    db: AsyncSession,
):
    try:
        _version = version
        _group_dataset_id = group_dataset_id

        print(_version, _group_dataset_id, "_group_dataset_id")

        stmt = select(DatasetModel).options(
            selectinload(DatasetModel.created_by_user),
            selectinload(DatasetModel.group_datasets),
        )
        result = await db.execute(stmt)
        list_dataset_in_group = result.scalars().all()
        print("list_dataset_in_group", list_dataset_in_group)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Get data successfully",
                    "data": list_dataset_in_group,
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


async def create_multiple_dataset(requestBody: DatasetCreateRequest, db: AsyncSession):

    try:
        _list_dataset = requestBody.list_dataset
        _group_dataset_id = requestBody.group_dataset_id

        _group_dataset = fetch_group_dataset_detail(
            group_dataset_id=_group_dataset_id, db=db
        )

        if not _group_dataset:
            raise UnicornException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="group_dataset_not_found",
            )
        # else:
        # update version 0 -> 1

        if len(_list_dataset) == 0:
            raise UnicornException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="Danh sách dataset của group_dataset không đúng forrmat",
            )
        created = []
        for req in _list_dataset:
            dataset = DatasetModel(
                group_dataset_id=_group_dataset_id,
                name=req.name,
                input=req.input,
                steps=req.steps,
                output=req.output,
            )
            db.add(dataset)
            created.append(dataset)

        await db.commit()
        for dataset in created:
            await db.refresh(dataset)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(
                {
                    "success": True,
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Create data successfully",
                    "data": [jsonable_encoder(d) for d in created],
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

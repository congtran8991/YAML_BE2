from typing import List
from apps.datasets.schema import  DatasetCreateRequest
from apps.datasets.models import DatasetModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from utils.response import ResponseUtils

async def create_multiple_datasets(
    requestBody: List[DatasetCreateRequest],
    db: AsyncSession
):

    try:
        created = []
        for req in requestBody:
            dataset = DatasetModel(
                group_dataset_id=req.group_dataset_id,
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
            content=jsonable_encoder({
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "message": "Create data successfully",
                "data": [jsonable_encoder(d) for d in created]
            })
        )
    
    except SQLAlchemyError as err:
        print("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseUtils.error_DB(err)
    
    except Exception as err:
        print("------error", err)
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseUtils.error_Other(err)
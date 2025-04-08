from typing import List
from apps.group_datasets.schema import GroupDatasetResponse, GroupDatasetCreateRequest
from apps.group_datasets.models import GroupDatasetModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from fastapi.responses import JSONResponse


from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from utils.response import ResponseUtils

async def get_all_group_datasets(db: AsyncSession) -> List[GroupDatasetResponse]:
    
    db_group_dataset = None
    try:
        stmt = select(GroupDatasetModel)
        result = await db.execute(stmt)
        list_group_datasets = result.scalars().all()
        
        db_group_dataset = list(map(GroupDatasetResponse.model_validate, list_group_datasets))
    
    except SQLAlchemyError as err:
        # Lỗi liên quan đến database
        return ResponseUtils.error_DB(err)
    
    except Exception as err:
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        return ResponseUtils.error_Other(err)
    
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Get data successfully",
                "data": db_group_dataset
            })
        ) 
    
async def create_group_dataset(requestBody: GroupDatasetCreateRequest, db: AsyncSession) -> JSONResponse:
    db_group_dataset = None
    try:
        db_group_dataset = GroupDatasetModel(
            code=requestBody.code,
            name=requestBody.name,
            latest_version=requestBody.latest_version,
            created_by=requestBody.created_by
        )

        db.add(db_group_dataset)
        await db.commit()
        await db.refresh(db_group_dataset)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "message": "Create data successfully",
                "data": True
            }
        )
    except SQLAlchemyError as err:
        print(err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseUtils.error_DB(err)
    
    except Exception as err:
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        await db.rollback()
        return await ResponseUtils.error_Other(err)
   
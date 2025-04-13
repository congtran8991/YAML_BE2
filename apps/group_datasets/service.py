from typing import List
from apps.group_datasets.schema import GroupDatasetResponse, GroupDatasetCreateRequest
from apps.users.schema import  UserInToken
from apps.group_datasets.models import GroupDatasetModel
from apps.permission_group_datasets.helpers import grant_full_permission
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload


from fastapi.responses import JSONResponse
 



from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from utils.response import ResponseErrUtils, ResponseCreateSuccess

async def get_all_group_datasets(user: UserInToken, db: AsyncSession) -> List[GroupDatasetResponse]:
    print("-----------------User-------------:", user)
    
    db_group_dataset = None
    try:
        stmt = select(GroupDatasetModel).options(joinedload(GroupDatasetModel.created_by_user))
        result = await db.execute(stmt)
        list_group_datasets = result.scalars().all()
        print(list_group_datasets, "db_group_dataset")
        
        db_group_dataset = group_datasets_filtered = []
        for dataset in list_group_datasets:
            created_by_user = dataset.created_by_user
            if created_by_user:
                # Bỏ trường hashed_password
                user_data = {
                    "id": created_by_user.id,
                    "email": created_by_user.email,
                    "created_at": created_by_user.created_at
                }
            else:
                user_data = None

            group_datasets_filtered.append({
                    "id": dataset.id,
                    "code": dataset.code,
                    "name": dataset.name,
                    "latest_version": dataset.latest_version,
                    "created_by_user": user_data,
                    "created_at": dataset.created_at
                })

            # db_group_dataset = list_group_datasets

            
    
    except SQLAlchemyError as err:
        return await ResponseErrUtils.error_DB(err)
    
    except Exception as err:
        # Lỗi khác (có thể do model_validate hoặc lỗi không xác định)
        return await ResponseErrUtils.error_Other(err)
    
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
    
async def create_group_dataset(user: UserInToken, requestBody: GroupDatasetCreateRequest, db: AsyncSession) -> JSONResponse:
    print("-----------------User-------------:", isinstance(user, dict), user)
    db_group_dataset = None
    try:
        db_group_dataset = GroupDatasetModel(
            code = requestBody.code,
            name = requestBody.name,
            latest_version = 1,
            created_by_id = user.id
        )

        db.add(db_group_dataset)
        await db.flush()

        await grant_full_permission(
            db=db,
            user_id=user.id,
            group_dataset_id=db_group_dataset.id,
        )

        await db.commit()
        await db.refresh(db_group_dataset)

        response_data = GroupDatasetResponse(
            id=db_group_dataset.id,
            code=db_group_dataset.code,
            name=db_group_dataset.name,
            latest_version=db_group_dataset.latest_version,
            created_by_user= UserInToken(id = user.id, email= user.email),  # Trả về thông tin đầy đủ của user
            created_at=db_group_dataset.created_at
        )

        return await ResponseCreateSuccess.success_created(data = response_data.model_dump())

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
    


   
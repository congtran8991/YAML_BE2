from typing import TYPE_CHECKING, List, Any, ByteString
from fastapi.middleware.cors import CORSMiddleware
from fastapi import  APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.users.schema import UserRegisterRequest, UserRegisterResponse
from apps.users.service import register_user_db
from database.postgresql import get_db

# if TYPE_CHECKING:
#     from sqlalchemy.orm import Session

router = APIRouter()

# @router.get("/api/", response_model=List[GroupDatasetResponse])
# async def get_group_datasets(db: AsyncSession = Depends(get_db)):
#     return await get_all_group_datasets(db=db)

@router.post("/api/register-user", response_model=UserRegisterResponse)
async def register_users(requestBody: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_user_db(db=db, requestBody=requestBody)
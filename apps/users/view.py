from typing import TYPE_CHECKING, List, Any, ByteString
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response import ResponseWrapper

from apps.users.schema import (
    UserRegisterRequest,
    UserResponse,
    UserLoginRequest,
    UserLoginResponse,
)
from apps.users.service import (
    register_user_db,
    login_account,
    get_current_users_service,
)
from database.postgresql import get_db

# if TYPE_CHECKING:
#     from sqlalchemy.orm import Session

router = APIRouter()

# @router.get("/api/", response_model=List[GroupDatasetResponse])
# async def get_group_datasets(db: AsyncSession = Depends(get_db)):
#     return await get_all_group_datasets(db=db)


@router.post("/api/register-user", response_model=ResponseWrapper[UserResponse])
async def register_users(
    requestBody: UserRegisterRequest, db: AsyncSession = Depends(get_db)
):
    return await register_user_db(db=db, requestBody=requestBody)


@router.post("/api/login-user", response_model=ResponseWrapper[UserLoginResponse])
async def login_users(
    requestBody: UserLoginRequest, db: AsyncSession = Depends(get_db)
):
    return await login_account(db=db, requestBody=requestBody)


@router.get("/api/current-user", response_model=ResponseWrapper[UserResponse])
async def get_current_users(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.state.user
    return await get_current_users_service(db=db, user=user)

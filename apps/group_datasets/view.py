from typing import TYPE_CHECKING, List, Any, ByteString
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.group_datasets.schema import GroupDatasetCreateRequest, GroupDatasetResponse
from apps.group_datasets.service import get_all_group_datasets
from database.postgresql import get_db

# if TYPE_CHECKING:
#     from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/api/group-datasets", response_model=List[GroupDatasetResponse])
async def get_group_datasets(db: AsyncSession = Depends(get_db)):
    return await get_all_group_datasets(db=db)

@router.post("/api/group-datasets", response_model=Any)
async def created_group_dataset(group_dataset: GroupDatasetCreateRequest):
    return {}
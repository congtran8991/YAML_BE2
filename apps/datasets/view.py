from typing import TYPE_CHECKING, List, Any, ByteString
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.datasets.schema import DatasetCreateRequest
from apps.datasets.service import create_multiple_datasets
from database.postgresql import get_db

# if TYPE_CHECKING:
#     from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/api/datasets", response_model=Any)
async def created_dataset(datasets: List[DatasetCreateRequest], db: AsyncSession = Depends(get_db)):
    return await create_multiple_datasets(db=db, requestBody=datasets)
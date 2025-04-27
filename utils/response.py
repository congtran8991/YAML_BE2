from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from utils.handling_errors.exception_handler import UnicornException

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel


# Khai báo một biến kiểu generic
T = TypeVar("T")

# Định nghĩa response wrapper với kiểu dữ liệu động


class ResponseWrapper(BaseModel, Generic[T]):
    success: bool
    status_code: int
    message: str
    data: Optional[T]


class ResponseErrUtils:
    @staticmethod
    async def error_DB(err):
        print("SQLAlchemyError >>>", repr(err))
        try:
            message = str(getattr(err.orig, "args", [str(err)])[0])
        except AttributeError:
            message = str(err)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": message,
                "message": repr(err),
                "data": None,
            },
        )

    @staticmethod
    async def error_Other(err: Exception) -> any:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(err),
                "data": None,
            },
        )

    @staticmethod
    async def error_UE(err: UnicornException) -> ResponseWrapper:
        return JSONResponse(
            status_code=err.status_code,
            content={
                "success": False,
                "status_code": err.status_code,
                "message": err.message,
                "data": None,
            },
        )

    @staticmethod
    async def error_invalid_data(message: str) -> any:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": message,
                "data": None,
            },
        )


class ResponseSuccess:
    @staticmethod
    async def success_created(data: T) -> ResponseWrapper:
        return ResponseWrapper(
            success=True,
            status_code=status.HTTP_201_CREATED,
            message="Create data successfully",
            data=data,
        )

    @staticmethod
    async def success_get(data: T) -> ResponseWrapper:
        return ResponseWrapper(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Get data successfully",
            data=data,
        )

    @staticmethod
    async def success_update(data: T) -> ResponseWrapper:
        return ResponseWrapper(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Update data successfully",
            data=data,
        )

    @staticmethod
    async def success_delete(data: T) -> ResponseWrapper:
        return ResponseWrapper(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Delete data successfully",
            data=data,
        )

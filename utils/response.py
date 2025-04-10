from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from utils.handling_errors.exception_handler import UnicornException

class ResponseErrUtils:
    @staticmethod
    async def error_DB(err: SQLAlchemyError) -> any:
        message = str(getattr(err.orig, 'args', [str(err)])[0])
        

        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": f"Database error: {message}",
                "data": None
            }
        )
    
    @staticmethod
    async def error_Other(err: Exception) -> any:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(err),
                "data": None
            }
        )
    
    @staticmethod
    async def error_UE(err: UnicornException) -> JSONResponse:
        return JSONResponse(
            status_code=err.status_code,
            content={
                "success": False,
                "status_code": err.status_code,
                "message": err.message,
                "data": None
            }
        )
    
    @staticmethod
    async def error_invalid_data(message: str) -> any:
        return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "status_code":status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message":  message,
            "data": None
        }
    )


class ResponseCreateSuccess:
    @staticmethod
    async def success_created(data: dict) -> any:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "status_code": status.HTTP_201_CREATED,
                "message": "Create data successfully",
                "data": data
            }
        ) 
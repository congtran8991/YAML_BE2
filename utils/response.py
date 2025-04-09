from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

class ResponseUtils:
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
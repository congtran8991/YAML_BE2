from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

class ResponseUtils:
    @staticmethod
    async def error_DB(err: SQLAlchemyError) -> any:
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": f"Database error: {str(err)}",
                "data": None
            }
        )
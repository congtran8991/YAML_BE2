from fastapi import FastAPI, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable, Awaitable
from utils.token import verify_jwt_token
from utils.handling_errors.exception_handler import UnicornException
from utils.response import ResponseErrUtils
from apps.users.schema import UserInToken

app = FastAPI()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            if request.method == "OPTIONS":
                return await call_next(request)

            include_paths = ["/api/login-user", "/docs"]
            if request.url.path in include_paths:
                return await call_next(request)

            auth_header = request.headers.get("Authorization")

            payload = verify_jwt_token(auth_header)
            if payload:
                request.state.user = UserInToken(
                    id=payload.get("iss"), email=payload.get("sub")
                )
                return await call_next(request)
            else:
                request.state.user = None
                raise UnicornException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message="Token không hợp lệ hoặc đã hết hạn",
                )

        except UnicornException as err:
            print("------error1", err.__dict__)
            request.state.user = None
            return await ResponseErrUtils.error_UE(err)

        except Exception as e:
            # response.headers["Access-Control-Allow-Origin"] = "*"
            # response.headers["Access-Control-Allow-Methods"] = "*"
            # response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            return await ResponseErrUtils.error_Other(e)

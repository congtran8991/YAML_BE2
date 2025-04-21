from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import time

from apps.users import schema, models
from utils.handling_errors.exception_handler import UnicornException
from utils.hasher import Hasher
from utils.response import ResponseErrUtils, ResponseCreateSuccess
from utils.token import get_access_token, get_refetch_token

from apps.users.schema import UserRegisterRequest, UserResponse, UserLoginResponse


async def register_user_db(
    requestBody: UserRegisterRequest, db: AsyncSession
) -> JSONResponse:

    try:
        _query = select(models.UserModel).where(
            models.UserModel.email == requestBody.email
        )
        result = await db.execute(_query)
        existing_user = result.scalars().first()

        if existing_user:
            raise UnicornException(
                status_code=status.HTTP_400_BAD_REQUEST, message="Duplicate Data"
            )

        # Băm mật khẩu trực tiếp và cập nhật trong requestBody
        hashed_password = Hasher.get_password_hash(requestBody.hashed_password)
        db_user = models.UserModel(
            email=requestBody.email, hashed_password=hashed_password
        )

        print("existing_user", existing_user)

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        _user = UserResponse(
            id=db_user.id,
            email=db_user.email,
            created_at=db_user.created_at.isoformat(),
        )

        return await ResponseCreateSuccess.success_created(data=_user)

    except SQLAlchemyError as err:
        print("------error", err)
        # Lỗi liên quan đến database
        await db.rollback()
        return await ResponseErrUtils.error_DB(err)

    except UnicornException as err:
        print("------error1", err.__dict__)
        await db.rollback()
        return await ResponseErrUtils.error_UE(err)

    except Exception as e:
        await db.rollback()
        print("Lỗi Exception", e)
        return await ResponseErrUtils.error_Other(e)


async def login_account(requestBody: schema.UserLoginRequest, db: AsyncSession):

    email_body = requestBody.email
    hashed_password_body = requestBody.hashed_password

    print("Email body:", requestBody, type(email_body))

    try:
        _query = select(models.UserModel).where(models.UserModel.email == email_body)
        result = await db.execute(_query)
        existing_user = result.scalars().first()

        if not existing_user:
            raise UnicornException(
                status_code=status.HTTP_404_NOT_FOUND, message="User does not exit"
            )

        id = existing_user.id
        email = existing_user.email
        hashed_password = existing_user.hashed_password
        is_supper_admin = existing_user.is_supper_admin
        created_at = existing_user.created_at

        is_verify_password = Hasher.verify_password(
            hashed_password_body, hashed_password
        )

        current_time_seconds = int(time.time())

        if is_verify_password:
            payload_access_token = {
                "iss": id,
                "sub": email,
                "exp": current_time_seconds + 60 * 60 * 1,  # 1 phút
                "is_supper_admin": is_supper_admin,
            }

            payload_refetch_token = {
                "iss": id,
                "sub": email,
                "exp": current_time_seconds + 60 * 60 * 1,  # 60 phút
                "is_supper_admin": is_supper_admin,
            }

            access_token = get_access_token(payload_access_token)
            refetch_token = get_refetch_token(payload_refetch_token)

            res_data = UserLoginResponse(
                id=id,
                email=email,
                created_at=created_at,
                access_token=access_token,
                refetch_token=refetch_token,
            )
            return await ResponseCreateSuccess.success_created(data=res_data)

        raise UnicornException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Incorrect username or password",
        )

    except UnicornException as err:
        db.rollback()
        return JSONResponse(
            status_code=err.status_code,
            content={
                "success": False,
                "status_code": err.status_code,
                "message": err.message,
                "data": None,
            },
        )

    except Exception as e:
        db.rollback()
        print("Lỗi Exception", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None,
            },
        )

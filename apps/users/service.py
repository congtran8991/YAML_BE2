from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import status
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from apps.users import schema, models
from utils.handling_errors.exception_handler import UnicornException
from utils.hasher import Hasher
from utils.response import ResponseErrUtils, ResponseCreateSuccess

from apps.users.schema import UserRegisterRequest, UserRegisterResponse


async def register_user_db(requestBody: schema.UserRegisterRequest, db: AsyncSession) -> JSONResponse:

    try:
        _query = select(models.UserModel).where(models.UserModel.email == requestBody.email)
        result = await db.execute(_query)
        existing_user = result.scalars().first()
        
        if existing_user:
            raise UnicornException(status_code = status.HTTP_400_BAD_REQUEST, message = "Duplicate Data")
        
        # Băm mật khẩu trực tiếp và cập nhật trong requestBody
        hashed_password = Hasher.get_password_hash(requestBody.hashed_password)
        db_user = models.UserModel(
            email=requestBody.email,
            hashed_password=hashed_password
        ) 

        print("existing_user", existing_user)

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        UserRegisterResponse(
            id=db_user.id,
            email=db_user.email,
            created_at=db_user.created_at
        )
        return UserRegisterResponse(
            id=db_user.id,
            email=db_user.email,
            created_at=db_user.created_at,
            emasqil=db_user.email,
        )
    
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
    


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apps.users.models import UserModel
from utils.handling_errors.exception_handler import UnicornException
from fastapi import status


async def get_user_by_identifier(db: AsyncSession, identifier: str | int) -> UserModel:
    """
    Tìm user theo email (str) hoặc user ID (int).
    Trả về UserModel hoặc raise exception nếu không tìm thấy.
    """
    stmt = select(UserModel)

    if isinstance(identifier, int):
        stmt = stmt.where(UserModel.id == identifier)
    elif isinstance(identifier, str):
        stmt = stmt.where(UserModel.email == identifier.lower())
    else:
        raise UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="invalid_user_identifier",
        )

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UnicornException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="user_not_found",
        )

    return user

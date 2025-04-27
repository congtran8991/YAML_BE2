import asyncio
from database.postgresql import engine, AsyncSessionLocal, get_db
from database.db_setting import ModelBase  # import Base chứa models
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import text

from apps.datasets.models import DatasetModel
from apps.dataset_versions.models import DatasetVersionModel
from apps.group_datasets.models import GroupDatasetModel
from apps.permission_group_datasets.models import GroupDatasetPermissionModel
from apps.users.models import UserModel

from apps.users.schema import UserInToken, UserLoginRequest

from apps.users.service import register_user_db


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)
        print("✅ Tables created successfully!")

    async with AsyncSessionLocal() as session:
        user_exits = await session.execute(text("SELECT 1 FROM users LIMIT 1"))

        requestBody = UserLoginRequest(email="cong1234@gmail.com", hashed_password="1")

        if not user_exits.scalar():
            try:
                response = await register_user_db(
                    db=session,
                    requestBody=requestBody,
                )
                print(f"✅ Default user created successfully! API response: {response}")
            except Exception as e:
                # Trong trường hợp có lỗi, rollback transaction
                await session.rollback()  # Gọi rollback trên db (AsyncSession)
                print(f"❌ Error: {str(e)}")
                raise HTTPException(status_code=500, detail="Error creating tables")
            # new_user = UserModel(
            #     email="cong1234@gmail.com", hashed_password="1", is_supper_admin=True
            # )
            # session.add(new_user)
            # await session.commit()
            # print("✅ Default user created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())

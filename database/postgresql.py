from sqlalchemy import  MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


URL_DATABASE = "postgresql+asyncpg://macintosh:1234@localhost:5432/yaml_tool2"

engine = create_async_engine(URL_DATABASE)

AsyncSessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine,  class_=AsyncSession,)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session



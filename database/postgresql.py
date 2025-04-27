from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


URL_DATABASE = "postgresql+asyncpg://macintosh:1234@localhost:5432/yaml_tool3"

engine = create_async_engine(URL_DATABASE, echo=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        print("🔓 OPEN session")
        yield session
        print("🔒 CLOSE session")  # sẽ chạy sau khi API call kết thúc

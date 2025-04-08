from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.group_datasets import view as group_datasets_view




# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Khởi động (startup)
#     print("📦 Khởi tạo CSDL...")
#     async with engine.begin() as conn:
#         await conn.run_sync(ModelBase.metadata.create_all)
#     print("✅ DB ready!")
#     yield
#     # Dọn dẹp (shutdown)
#     print("🛑 Shutting down...")
#     await engine.dispose()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Ghi rõ domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(group_datasets_view.router)

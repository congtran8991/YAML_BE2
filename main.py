from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from apps.group_datasets import view as group_datasets_view
from apps.datasets import view as datasets_view
from apps.users import view as users_view

from sqlalchemy.exc import IntegrityError
import asyncpg

from fastapi import status

from utils.response import ResponseErrUtils



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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("Error:", exc.errors(),"------------request:", request)
    return await ResponseErrUtils.error_invalid_data("Dữ liệu gửi lên không hợp lệ")
    
app.include_router(users_view.router)
app.include_router(group_datasets_view.router)
app.include_router(datasets_view.router)

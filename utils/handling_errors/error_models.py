from pydantic import BaseModel

class ErrorDetail(BaseModel):
    loc: list
    msg: str
    type: str

class ErrorResponse(BaseModel):
    message: str
    errors: list[ErrorDetail]

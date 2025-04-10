from pydantic import BaseModel

class UnicornException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

class ErrorUnicornException(BaseModel):
    status_code: int
    message: str

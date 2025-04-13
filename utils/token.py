from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta
from jwt.exceptions import PyJWTError

from utils.handling_errors.exception_handler import UnicornException
from fastapi import status


JWT_SECRET_ACCESS = "JWT_SECRET_ACCESS"
JWT_SECRET_REFETCH = "JWT_SECRET_REFETCH"
ALGORITHM = "HS256"


def get_access_token(payload: dict):
    access_token = jwt.encode(payload, JWT_SECRET_ACCESS, algorithm=ALGORITHM)
    return access_token

def get_refetch_token(payload):
    refetch_token = jwt.encode(payload, JWT_SECRET_REFETCH, algorithm=ALGORITHM)
    return refetch_token

def verify_jwt_token(auth_header: str):
    try:
        if not auth_header:
            return None
        
        if auth_header.startswith('Bearer '):
            _token = auth_header.split(" ")[1]
            print(_token, "_token")
        else:
            _token = auth_header

        payload = jwt.decode(_token, JWT_SECRET_ACCESS, algorithms=[ALGORITHM])
        print('payload', payload)
        return payload
    except PyJWTError as e:
        print(f"Token không hợp lệ: {str(e)}")
        return None
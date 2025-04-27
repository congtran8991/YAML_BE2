from typing import List
from fastapi import HTTPException, status


def validate_list_ids(ids: List[str]) -> List[int]:
    try:
        _ids = [int(i) for i in ids]
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 'ids' parameter. Must be a list of integers.",
        )

    if not isinstance(_ids, list) or not all(isinstance(i, int) for i in _ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 'ids' parameter. Must be a list of integers.",
        )
    return _ids

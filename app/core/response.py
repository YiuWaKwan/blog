from typing import Any

from app.schemas.common import ApiResponse


def success(data: Any = None, message: str = "ok") -> dict[str, Any]:
    return ApiResponse(data=data, message=message).model_dump()


def error(code: int, message: str, data: Any = None) -> dict[str, Any]:
    return ApiResponse(code=code, message=message, data=data).model_dump()

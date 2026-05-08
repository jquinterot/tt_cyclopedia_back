from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class APIError(HTTPException):
    """
    Custom API error exception that includes a machine-readable error code.

    Usage:
        raise APIError(
            status_code=404,
            detail="Resource not found",
            code="POST_001"
        )
    """

    def __init__(self, status_code: int, detail: str, code: str, headers: dict = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


async def api_error_handler(request: Request, exc: APIError):
    """Exception handler for APIError that returns standardized error responses."""
    content = {"detail": exc.detail, "code": exc.code}
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers,
    )

import logging

from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger("secure_candidate_app")


async def internal_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected application errors safely."""

    request_id = getattr(
        request.state,
        "request_id",
        "unknown",
    )

    logger.exception(
        "unexpected application error",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )
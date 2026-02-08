"""
Middleware package for Backend Task API.

[Task]: T012, T011
[From]: specs/001-backend-task-api/plan.md §Phase 2
[From]: specs/002-auth-jwt/plan.md §JWT Verification
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from .jwt_auth import verify_jwt, create_jwt_token

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: FastAPI request object
        exc: Exception that was raised

    Returns:
        JSONResponse: Error response with 500 status code
    """
    # Log the error for debugging
    logger.error(f"Unhandled error: {exc}", exc_info=True)

    # Return generic error to user (don't expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Service temporarily unavailable"},
    )


def setup_exception_handlers(app):
    """
    Register exception handlers with FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(Exception, global_exception_handler)


__all__ = ["verify_jwt", "create_jwt_token", "setup_exception_handlers"]

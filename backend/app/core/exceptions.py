from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class FinPilotException(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class NotFoundException(FinPilotException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)

async def finpilot_exception_handler(request: Request, exc: FinPilotException):
    logger.warning(f"Handled Exception: {exc.message} on {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.message}}
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)} on {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": 500, "message": "Internal Server Error"}}
    )

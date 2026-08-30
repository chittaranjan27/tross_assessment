import logging
import time
import uuid
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.api.v1 import health
from app.api.v1.endpoints import profiles
from app.core.config import settings
from app.core.exceptions import AppException

# Set up logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["profiles"])


@app.middleware("http")
async def request_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()

    # Process the request
    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"completed in {process_time:.4f}s "
        f"Status: {response.status_code} "
        f"RequestID: {request_id}"
    )

    return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )

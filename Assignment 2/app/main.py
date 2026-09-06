"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: FastAPI Application
Description: Main application entry point and health check endpoint.
"""

import json
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors import GitHubAPIError
from app.event_store import initialize_database
from app.routers.events import router as events_router
from app.routers.issues import router as issues_router
from app.routers.webhook import router as webhook_router

logger = logging.getLogger("issues_gateway")

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

app = FastAPI(
    title="GitHub Issues Gateway",
    version="1.0.0",
)


@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    """Add request IDs and emit structured request logs.

    Author: Changhyun Kim
    """

    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    github_delivery_id = request.headers.get("X-GitHub-Delivery")

    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    response.headers["X-Request-ID"] = request_id

    log_entry = {
        "event": "http_request",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }

    if github_delivery_id:
        log_entry["github_delivery_id"] = github_delivery_id

    logger.info(json.dumps(log_entry))

    return response


initialize_database()

app.include_router(issues_router)
app.include_router(webhook_router)
app.include_router(events_router)


@app.exception_handler(GitHubAPIError)
async def github_api_error_handler(
    request: Request,
    exc: GitHubAPIError,
):
    """Return GitHub API errors using the standard error format."""

    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": "github_api_error",
            "message": exc.message,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Return request validation failures as HTTP 400 errors."""

    errors = exc.errors()

    if errors:
        message = errors[0].get("msg", "Invalid request.")
    else:
        message = "Invalid request."

    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": message,
            "status_code": 400,
        },
    )


@app.get(
    "/healthz",
    operation_id="health_check",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                    }
                }
            },
        }
    },
)
def health_check():
    """Return the health status of the service."""

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Custom OpenAPI
# ---------------------------------------------------------------------------

original_openapi = app.openapi


def custom_openapi():
    """Keep the OpenAPI contract aligned with actual API behavior.

    FastAPI documents request validation errors as HTTP 422 by default.
    This application converts RequestValidationError responses to HTTP 400,
    so the automatically generated 422 responses are removed from the
    runtime OpenAPI schema.

    Author: Changhyun Kim
    """

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = original_openapi()

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            responses = operation.get("responses", {})
            responses.pop("422", None)

    schemas = openapi_schema.get("components", {}).get("schemas", {})

    schemas.pop("HTTPValidationError", None)
    schemas.pop("ValidationError", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

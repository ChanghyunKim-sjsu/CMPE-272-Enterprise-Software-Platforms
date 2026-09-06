"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Webhook Events API
Description: Provides access to recently processed webhook deliveries.
"""

from fastapi import APIRouter, Query

from app.event_store import list_events
from app.schemas import ErrorResponse, WebhookEventResponse

router = APIRouter()


EVENT_EXAMPLE = {
    "id": 1,
    "event": "issues",
    "action": "opened",
    "issue_number": 4,
    "timestamp": "2026-09-05T20:25:00Z",
}

VALIDATION_ERROR_EXAMPLE = {
    "error": "validation_error",
    "message": "Input should be less than or equal to 100",
    "status_code": 400,
}


@router.get(
    "/events",
    response_model=list[WebhookEventResponse],
    operation_id="list_webhook_events",
    responses={
        200: {
            "description": "Webhook events returned successfully",
            "content": {
                "application/json": {
                    "example": [EVENT_EXAMPLE],
                }
            },
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid limit query parameter",
            "content": {
                "application/json": {
                    "example": VALIDATION_ERROR_EXAMPLE,
                }
            },
        },
    },
)
def get_events(
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return recently processed webhook events."""

    return list_events(limit)

"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Webhook Events API
Description: Provides access to recently processed webhook deliveries.
"""

from fastapi import APIRouter, Query

from app.event_store import list_events
from app.schemas import WebhookEventResponse


router = APIRouter()


@router.get(
    "/events",
    response_model=list[WebhookEventResponse],
)
def get_events(
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return recently processed webhook events."""

    return list_events(limit)
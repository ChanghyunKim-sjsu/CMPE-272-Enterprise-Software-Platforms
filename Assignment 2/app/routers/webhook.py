"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Webhook API Route
Description: Receives and validates GitHub webhook deliveries.
"""

import json

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse

from app.webhook import verify_webhook_signature

from app.event_store import save_event


router = APIRouter()

ALLOWED_EVENTS = {"issues", "issue_comment", "ping"}

ALLOWED_ACTIONS = {
    "issues": {
        "opened",
        "edited",
        "deleted",
        "transferred",
        "pinned",
        "unpinned",
        "closed",
        "reopened",
        "assigned",
        "unassigned",
        "labeled",
        "unlabeled",
        "locked",
        "unlocked",
        "milestoned",
        "demilestoned",
    },
    "issue_comment": {
        "created",
        "edited",
        "deleted",
    },
}


@router.post(
    "/webhook",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def github_webhook(request: Request):
    """Receive and validate GitHub webhook deliveries."""

    body = await request.body()

    signature = request.headers.get("X-Hub-Signature-256")
    event = request.headers.get("X-GitHub-Event")

    if not verify_webhook_signature(body, signature):
        return JSONResponse(
            status_code=401,
            content={
                "error": "invalid_signature",
                "message": "Webhook signature validation failed.",
                "status_code": 401,
            },
        )

    if event not in ALLOWED_EVENTS:
        return JSONResponse(
            status_code=400,
            content={
                "error": "unsupported_event",
                "message": "Unsupported GitHub webhook event.",
                "status_code": 400,
            },
        )

    if event == "ping":
        return Response(status_code=204)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_payload",
                "message": "Webhook payload is not valid JSON.",
                "status_code": 400,
            },
        )

    action = payload.get("action")

    if action not in ALLOWED_ACTIONS[event]:
        return JSONResponse(
            status_code=400,
            content={
                "error": "unsupported_action",
                "message": f"Unsupported action '{action}' for event '{event}'.",
                "status_code": 400,
            },
        )

    delivery_id = request.headers.get("X-GitHub-Delivery")

    if not delivery_id:
        return JSONResponse(
            status_code=400,
            content={
                "error": "missing_delivery_id",
                "message": "X-GitHub-Delivery header is required.",
                "status_code": 400,
            },
        )

    issue = payload.get("issue", {})
    issue_number = issue.get("number")

    save_event(
        delivery_id=delivery_id,
        event=event,
        action=action,
        issue_number=issue_number,
    )

    return Response(status_code=204)
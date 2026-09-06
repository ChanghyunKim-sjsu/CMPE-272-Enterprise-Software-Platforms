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

from app.event_store import save_event
from app.schemas import ErrorResponse
from app.webhook import verify_webhook_signature

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
    operation_id="receive_github_webhook",
    responses={
        204: {
            "description": ("Webhook delivery accepted and processed successfully"),
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid or unsupported webhook delivery",
            "content": {
                "application/json": {
                    "examples": {
                        "unsupported_event": {
                            "summary": "Unsupported GitHub event",
                            "value": {
                                "error": "unsupported_event",
                                "message": ("Unsupported GitHub webhook event."),
                                "status_code": 400,
                            },
                        },
                        "invalid_payload": {
                            "summary": "Invalid JSON payload",
                            "value": {
                                "error": "invalid_payload",
                                "message": ("Webhook payload is not valid JSON."),
                                "status_code": 400,
                            },
                        },
                        "unsupported_action": {
                            "summary": "Unsupported webhook action",
                            "value": {
                                "error": "unsupported_action",
                                "message": (
                                    "Unsupported action 'unknown' for event 'issues'."
                                ),
                                "status_code": 400,
                            },
                        },
                        "missing_delivery_id": {
                            "summary": "Missing delivery ID",
                            "value": {
                                "error": "missing_delivery_id",
                                "message": ("X-GitHub-Delivery header is required."),
                                "status_code": 400,
                            },
                        },
                    }
                }
            },
        },
        401: {
            "model": ErrorResponse,
            "description": "Webhook signature validation failed",
            "content": {
                "application/json": {
                    "example": {
                        "error": "invalid_signature",
                        "message": ("Webhook signature validation failed."),
                        "status_code": 401,
                    }
                }
            },
        },
    },
    openapi_extra={
        "parameters": [
            {
                "name": "X-Hub-Signature-256",
                "in": "header",
                "required": True,
                "description": (
                    "GitHub HMAC SHA-256 signature used to verify the webhook payload."
                ),
                "schema": {
                    "type": "string",
                    "example": "sha256=<signature>",
                },
            },
            {
                "name": "X-GitHub-Event",
                "in": "header",
                "required": True,
                "description": (
                    "GitHub webhook event type, such as issues, issue_comment, or ping."
                ),
                "schema": {
                    "type": "string",
                    "example": "issues",
                },
            },
            {
                "name": "X-GitHub-Delivery",
                "in": "header",
                "required": False,
                "description": (
                    "Unique GitHub delivery identifier. Required for "
                    "issues and issue_comment events and used for "
                    "idempotent event storage."
                ),
                "schema": {
                    "type": "string",
                    "example": "12345678-abcd-1234-abcd-123456789abc",
                },
            },
        ],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "example": {
                        "action": "opened",
                        "issue": {
                            "number": 4,
                        },
                    }
                }
            },
        },
    },
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
                "message": (f"Unsupported action '{action}' for event '{event}'."),
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

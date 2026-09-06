"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - Webhook Route
Description: Tests webhook endpoint validation and event processing.
"""

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from app.config import WEBHOOK_SECRET
from app.main import app


client = TestClient(app)


def make_signature(body: bytes) -> str:
    """Create a valid HMAC SHA-256 signature for a webhook payload."""

    return "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()


def test_webhook_rejects_invalid_signature():
    """Invalid webhook signatures should return HTTP 401."""

    response = client.post(
        "/webhook",
        content=b'{"action":"opened"}',
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "issues",
            "X-Hub-Signature-256": "sha256=invalid",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_signature"


def test_webhook_rejects_unknown_event():
    """Unsupported GitHub events should return HTTP 400."""

    body = b'{"action":"created"}'

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": make_signature(body),
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "unsupported_event"


def test_webhook_accepts_ping():
    """A valid GitHub ping should return HTTP 204."""

    body = b"{}"

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "ping",
            "X-Hub-Signature-256": make_signature(body),
        },
    )

    assert response.status_code == 204


def test_webhook_rejects_invalid_json():
    """A signed body containing invalid JSON should return HTTP 400."""

    body = b"not-json"

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "issues",
            "X-Hub-Signature-256": make_signature(body),
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_payload"


def test_webhook_rejects_unsupported_action():
    """An unsupported issue action should return HTTP 400."""

    body = json.dumps(
        {
            "action": "something_invalid",
            "issue": {"number": 10},
        }
    ).encode()

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "issues",
            "X-Hub-Signature-256": make_signature(body),
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "unsupported_action"


def test_webhook_requires_delivery_id():
    """A valid webhook without a delivery ID should return HTTP 400."""

    body = json.dumps(
        {
            "action": "opened",
            "issue": {"number": 10},
        }
    ).encode()

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "issues",
            "X-Hub-Signature-256": make_signature(body),
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "missing_delivery_id"
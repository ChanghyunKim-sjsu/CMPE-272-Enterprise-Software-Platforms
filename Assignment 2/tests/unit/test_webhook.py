"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - Webhook Security
Description: Tests GitHub webhook HMAC SHA-256 signature verification.
"""

import hashlib
import hmac

from app.config import WEBHOOK_SECRET
from app.webhook import verify_webhook_signature


def make_signature(body: bytes) -> str:
    """Create a valid test signature using the configured webhook secret."""

    return "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()


def test_valid_webhook_signature_returns_true():
    """A correctly signed webhook body should be accepted."""

    body = b'{"action":"opened"}'
    signature = make_signature(body)

    assert verify_webhook_signature(body, signature) is True


def test_invalid_webhook_signature_returns_false():
    """An invalid webhook signature should be rejected."""

    body = b'{"action":"opened"}'

    assert verify_webhook_signature(
        body,
        "sha256=invalid",
    ) is False


def test_tampered_webhook_body_returns_false():
    """Changing the body after signing should invalidate the signature."""

    original_body = b'{"action":"opened"}'
    tampered_body = b'{"action":"closed"}'

    signature = make_signature(original_body)

    assert verify_webhook_signature(
        tampered_body,
        signature,
    ) is False
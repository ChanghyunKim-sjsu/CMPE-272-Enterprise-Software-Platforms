"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Webhook Security
Description: Verifies GitHub webhook signatures using HMAC SHA-256.
"""

import hashlib
import hmac

from app.config import WEBHOOK_SECRET


def verify_webhook_signature(
    body: bytes,
    signature: str | None,
) -> bool:
    """Verify a GitHub webhook HMAC SHA-256 signature."""

    if not WEBHOOK_SECRET or not signature:
        return False

    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )
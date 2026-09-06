"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - Request Validation
Description: Tests API validation for invalid issue requests.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_issue_without_title_returns_400():
    """Creating an issue without a title should return HTTP 400."""

    response = client.post(
        "/issues",
        json={
            "body": "Missing title test.",
            "labels": [],
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"] == "validation_error"
    assert data["status_code"] == 400


def test_update_issue_with_invalid_state_returns_400():
    """Updating an issue with an invalid state should return HTTP 400."""

    response = client.patch(
        "/issues/2",
        json={
            "state": "deleted",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"] == "validation_error"
    assert data["status_code"] == 400
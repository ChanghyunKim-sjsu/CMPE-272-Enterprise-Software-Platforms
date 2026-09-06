"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: GitHub Integration Tests
Description: Tests the Issues Gateway end-to-end against the real GitHub test repository.
"""

import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="Set RUN_INTEGRATION_TESTS=1 to run real GitHub integration tests.",
)


def test_github_issue_lifecycle():
    """Test create, read, update, close, reopen, and comment operations."""

    timestamp = datetime.now(timezone.utc).isoformat()

    create_response = client.post(
        "/issues",
        json={
            "title": f"Integration Test {timestamp}",
            "body": "Created by the automated integration test.",
            "labels": [],
        },
    )

    assert create_response.status_code == 201

    issue = create_response.json()
    issue_number = issue["number"]

    try:
        # Read the newly created issue.
        get_response = client.get(
            f"/issues/{issue_number}"
        )

        assert get_response.status_code == 200
        assert get_response.json()["number"] == issue_number

        # Update title and body.
        update_response = client.patch(
            f"/issues/{issue_number}",
            json={
                "title": "Updated Integration Test",
                "body": "Updated through the integration test.",
            },
        )

        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Integration Test"

        # Close the issue.
        close_response = client.patch(
            f"/issues/{issue_number}",
            json={
                "state": "closed",
            },
        )

        assert close_response.status_code == 200
        assert close_response.json()["state"] == "closed"

        # Reopen the issue.
        reopen_response = client.patch(
            f"/issues/{issue_number}",
            json={
                "state": "open",
            },
        )

        assert reopen_response.status_code == 200
        assert reopen_response.json()["state"] == "open"

        # Create a comment.
        comment_response = client.post(
            f"/issues/{issue_number}/comments",
            json={
                "body": "Integration test comment.",
            },
        )

        assert comment_response.status_code == 201

        comment_id = comment_response.json()["id"]

        # Fetch comments and verify the new comment exists.
        comments_response = client.get(
            f"/issues/{issue_number}/comments"
        )

        assert comments_response.status_code == 200

        comment_ids = [
            comment["id"]
            for comment in comments_response.json()
        ]

        assert comment_id in comment_ids

    finally:
        # Leave the test repository clean by closing the issue.
        client.patch(
            f"/issues/{issue_number}",
            json={
                "state": "closed",
            },
        )
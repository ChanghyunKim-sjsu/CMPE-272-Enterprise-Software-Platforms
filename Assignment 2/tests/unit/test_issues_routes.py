"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - Issues Routes
Description: Tests successful issue and comment API route behavior.
"""

from fastapi.testclient import TestClient

import app.routers.issues as issues_router
from app.main import app

client = TestClient(app)


MOCK_ISSUE = {
    "number": 10,
    "html_url": "https://github.com/test/issues/10",
    "state": "open",
    "title": "Mock Issue",
    "body": "Mock body",
    "labels": [
        {"name": "bug"},
    ],
    "created_at": "2026-09-05T20:00:00Z",
    "updated_at": "2026-09-05T20:00:00Z",
}


def test_create_issue_route(monkeypatch):
    """POST /issues should return HTTP 201 and Location header."""

    async def mock_create_issue(title, body, labels):
        return MOCK_ISSUE

    monkeypatch.setattr(
        issues_router,
        "create_issue",
        mock_create_issue,
    )

    response = client.post(
        "/issues",
        json={
            "title": "Mock Issue",
            "body": "Mock body",
            "labels": ["bug"],
        },
    )

    assert response.status_code == 201
    assert response.headers["Location"] == "/issues/10"
    assert response.json()["number"] == 10
    assert response.json()["labels"] == ["bug"]


def test_list_issues_route_forwards_link_header(monkeypatch):
    """GET /issues should return issues and propagate Link pagination."""

    async def mock_list_issues(
        state,
        labels,
        page,
        per_page,
    ):
        return (
            [MOCK_ISSUE],
            '<https://api.github.com/test?page=2>; rel="next"',
        )

    monkeypatch.setattr(
        issues_router,
        "list_issues",
        mock_list_issues,
    )

    response = client.get("/issues?state=open&page=1&per_page=1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert 'rel="next"' in response.headers["Link"]


def test_get_single_issue_route(monkeypatch):
    """GET /issues/{number} should return one issue."""

    async def mock_get_issue(number):
        return MOCK_ISSUE

    monkeypatch.setattr(
        issues_router,
        "get_issue",
        mock_get_issue,
    )

    response = client.get("/issues/10")

    assert response.status_code == 200
    assert response.json()["number"] == 10
    assert response.json()["title"] == "Mock Issue"


def test_update_issue_route(monkeypatch):
    """PATCH /issues/{number} should return updated issue data."""

    updated_issue = {
        **MOCK_ISSUE,
        "state": "closed",
        "title": "Updated Mock Issue",
    }

    async def mock_update_issue(
        number,
        title,
        body,
        state,
    ):
        return updated_issue

    monkeypatch.setattr(
        issues_router,
        "update_issue",
        mock_update_issue,
    )

    response = client.patch(
        "/issues/10",
        json={
            "title": "Updated Mock Issue",
            "state": "closed",
        },
    )

    assert response.status_code == 200
    assert response.json()["state"] == "closed"
    assert response.json()["title"] == "Updated Mock Issue"


def test_create_comment_route(monkeypatch):
    """POST /issues/{number}/comments should create a comment."""

    async def mock_create_comment(number, body):
        return {
            "id": 500,
            "body": body,
            "user": {
                "login": "test-user",
            },
            "created_at": "2026-09-05T20:00:00Z",
            "html_url": ("https://github.com/test/issues/10#issuecomment-500"),
        }

    monkeypatch.setattr(
        issues_router,
        "create_comment",
        mock_create_comment,
    )

    response = client.post(
        "/issues/10/comments",
        json={
            "body": "Mock comment",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 500
    assert response.json()["user"] == "test-user"


def test_list_comments_route(monkeypatch):
    """GET /issues/{number}/comments should return comments."""

    async def mock_list_comments(number):
        return [
            {
                "id": 500,
                "body": "Mock comment",
                "user": {
                    "login": "test-user",
                },
                "created_at": "2026-09-05T20:00:00Z",
                "html_url": ("https://github.com/test/issues/10#issuecomment-500"),
            }
        ]

    monkeypatch.setattr(
        issues_router,
        "list_comments",
        mock_list_comments,
    )

    response = client.get("/issues/10/comments")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["body"] == "Mock comment"

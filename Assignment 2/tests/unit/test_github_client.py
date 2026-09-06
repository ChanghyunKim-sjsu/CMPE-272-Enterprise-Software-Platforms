"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - GitHub Client
Description: Tests successful GitHub REST API calls and client error handling.
"""

import asyncio
import re

import httpx
import pytest

import app.github_client as github_client
from app.errors import GitHubAPIError

GITHUB_BASE_URL = github_client.GITHUB_API_BASE_URL


def test_get_headers_contains_required_github_headers():
    """GitHub requests should contain authentication and API headers."""

    headers = github_client.get_headers()

    assert headers["Authorization"].startswith("Bearer ")
    assert headers["Accept"] == "application/vnd.github+json"
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"


def test_get_headers_requires_token(monkeypatch):
    """A missing GitHub token should raise a configuration error."""

    monkeypatch.setattr(
        github_client,
        "GITHUB_TOKEN",
        None,
    )

    with pytest.raises(RuntimeError):
        github_client.get_headers()


def test_list_issues_returns_data_and_link_header(httpx_mock):
    """Issue listing should return GitHub data and pagination information."""

    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(GITHUB_BASE_URL)}/issues\?.*"),
        status_code=200,
        json=[
            {
                "number": 1,
                "title": "Mock Issue",
            }
        ],
        headers={"Link": ('<https://api.github.com/test/issues?page=2>; rel="next"')},
    )

    issues, link_header = asyncio.run(
        github_client.list_issues(
            state="open",
            page=1,
            per_page=30,
        )
    )

    assert len(issues) == 1
    assert issues[0]["number"] == 1
    assert 'rel="next"' in link_header


def test_create_issue_success(httpx_mock):
    """Creating an issue should return the GitHub response."""

    httpx_mock.add_response(
        method="POST",
        url=f"{GITHUB_BASE_URL}/issues",
        status_code=201,
        json={
            "number": 10,
            "title": "Created Issue",
        },
    )

    issue = asyncio.run(
        github_client.create_issue(
            title="Created Issue",
            body="Created in unit test.",
            labels=[],
        )
    )

    assert issue["number"] == 10
    assert issue["title"] == "Created Issue"


def test_get_issue_success(httpx_mock):
    """get_issue should return issue data and ETag metadata."""

    httpx_mock.add_response(
        method="GET",
        url=f"{GITHUB_BASE_URL}/issues/10",
        status_code=200,
        headers={
            "ETag": '"etag-v1"',
        },
        json={
            "number": 10,
            "title": "Test issue",
            "state": "open",
        },
    )

    issue, etag, not_modified = asyncio.run(github_client.get_issue(10))

    assert issue["number"] == 10
    assert issue["title"] == "Test issue"
    assert etag == '"etag-v1"'
    assert not_modified is False


def test_update_issue_success(httpx_mock):
    """Updating an issue should return the updated GitHub issue."""

    httpx_mock.add_response(
        method="PATCH",
        url=f"{GITHUB_BASE_URL}/issues/10",
        status_code=200,
        json={
            "number": 10,
            "title": "Updated Issue",
            "state": "closed",
        },
    )

    issue = asyncio.run(
        github_client.update_issue(
            number=10,
            title="Updated Issue",
            body="Updated body.",
            state="closed",
        )
    )

    assert issue["title"] == "Updated Issue"
    assert issue["state"] == "closed"


def test_create_comment_success(httpx_mock):
    """Creating a comment should return GitHub comment data."""

    httpx_mock.add_response(
        method="POST",
        url=f"{GITHUB_BASE_URL}/issues/10/comments",
        status_code=201,
        json={
            "id": 500,
            "body": "Mock comment",
        },
    )

    comment = asyncio.run(
        github_client.create_comment(
            number=10,
            body="Mock comment",
        )
    )

    assert comment["id"] == 500
    assert comment["body"] == "Mock comment"


def test_list_comments_success(httpx_mock):
    """Listing comments should return comments from GitHub."""

    httpx_mock.add_response(
        method="GET",
        url=f"{GITHUB_BASE_URL}/issues/10/comments",
        status_code=200,
        json=[
            {
                "id": 500,
                "body": "Mock comment",
            }
        ],
    )

    comments = asyncio.run(github_client.list_comments(10))

    assert len(comments) == 1
    assert comments[0]["id"] == 500


def test_github_422_maps_to_400():
    """GitHub validation failures should become HTTP 400 errors."""

    response = httpx.Response(
        status_code=422,
        json={
            "message": "Validation Failed",
        },
    )

    with pytest.raises(GitHubAPIError) as exc_info:
        github_client.handle_github_error(response)

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == "Validation Failed"


def test_github_500_maps_to_502():
    """Unexpected GitHub failures should become gateway errors."""

    response = httpx.Response(
        status_code=500,
        json={
            "message": "GitHub internal error",
        },
    )

    with pytest.raises(GitHubAPIError) as exc_info:
        github_client.handle_github_error(response)

    assert exc_info.value.status_code == 502


def test_get_issue_forwards_if_none_match_and_handles_304(
    httpx_mock,
):
    """get_issue should forward If-None-Match and handle HTTP 304."""

    etag = '"etag-v1"'

    httpx_mock.add_response(
        method="GET",
        url=f"{GITHUB_BASE_URL}/issues/10",
        status_code=304,
        headers={
            "ETag": etag,
        },
        match_headers={
            "If-None-Match": etag,
        },
    )

    issue, returned_etag, not_modified = asyncio.run(
        github_client.get_issue(
            10,
            if_none_match=etag,
        )
    )

    assert issue is None
    assert returned_etag == etag
    assert not_modified is True

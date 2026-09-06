"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: GitHub REST API Client
Description: Handles communication with the GitHub REST API.
"""

import time

import httpx

from app.config import GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN
from app.errors import GitHubAPIError

GITHUB_API_BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"


def get_headers():
    """Return the HTTP headers required by the GitHub REST API."""

    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is not configured.")

    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def handle_github_error(response: httpx.Response):
    """Convert GitHub API errors into application exceptions."""

    if response.is_success:
        return

    try:
        github_error = response.json()
        message = github_error.get(
            "message",
            "GitHub API request failed.",
        )
    except ValueError:
        message = "GitHub API request failed."

    error_headers = {}

    remaining = response.headers.get("X-RateLimit-Remaining")

    if response.status_code == 429 or (
        response.status_code == 403 and remaining == "0"
    ):
        status_code = 429

        retry_after = response.headers.get("Retry-After")

        if not retry_after:
            reset_time = response.headers.get("X-RateLimit-Reset")

            if reset_time:
                wait_seconds = max(
                    1,
                    int(reset_time) - int(time.time()),
                )
                retry_after = str(wait_seconds)

        if retry_after:
            error_headers["Retry-After"] = retry_after

        message = f"GitHub rate limit exceeded. {message}"

    elif response.status_code == 401:
        status_code = 401

    elif response.status_code == 403:
        status_code = 403

    elif response.status_code == 404:
        status_code = 404

    elif response.status_code == 422:
        status_code = 400

    else:
        status_code = 502

    raise GitHubAPIError(
        status_code=status_code,
        message=message,
        headers=error_headers,
    )


async def list_issues(
    state: str = "open",
    labels: str | None = None,
    page: int = 1,
    per_page: int = 30,
):
    """Return issues and pagination information from GitHub."""

    url = f"{GITHUB_API_BASE_URL}/issues"

    params = {
        "state": state,
        "page": page,
        "per_page": per_page,
    }

    if labels:
        params["labels"] = labels

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=get_headers(),
            params=params,
        )

    handle_github_error(response)

    return response.json(), response.headers.get("Link")


async def create_issue(
    title: str,
    body: str | None = None,
    labels: list[str] | None = None,
):
    """Create a new issue in the configured GitHub repository."""

    url = f"{GITHUB_API_BASE_URL}/issues"

    payload = {
        "title": title,
    }

    if body is not None:
        payload["body"] = body

    if labels is not None:
        payload["labels"] = labels

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=get_headers(),
            json=payload,
        )

    handle_github_error(response)

    return response.json()


async def get_issue(number: int):
    """Return a single GitHub issue by issue number."""

    url = f"{GITHUB_API_BASE_URL}/issues/{number}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=get_headers(),
        )

    handle_github_error(response)

    return response.json()


async def update_issue(
    number: int,
    title: str | None = None,
    body: str | None = None,
    state: str | None = None,
):
    """Update an existing GitHub issue."""

    url = f"{GITHUB_API_BASE_URL}/issues/{number}"

    payload = {}

    if title is not None:
        payload["title"] = title

    if body is not None:
        payload["body"] = body

    if state is not None:
        payload["state"] = state

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url,
            headers=get_headers(),
            json=payload,
        )

    handle_github_error(response)

    return response.json()


async def create_comment(number: int, body: str):
    """Create a comment on an existing GitHub issue."""

    url = f"{GITHUB_API_BASE_URL}/issues/{number}/comments"

    payload = {
        "body": body,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=get_headers(),
            json=payload,
        )

    handle_github_error(response)

    return response.json()


async def list_comments(number: int):
    """Return comments for an existing GitHub issue."""

    url = f"{GITHUB_API_BASE_URL}/issues/{number}/comments"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=get_headers(),
        )

    handle_github_error(response)

    return response.json()

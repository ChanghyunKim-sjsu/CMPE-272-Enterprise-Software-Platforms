"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Issues API Routes
Description: Provides HTTP endpoints for GitHub issue operations.
"""

from fastapi import APIRouter, Query, Response, status

from app.github_client import (
    create_comment,
    create_issue,
    get_issue,
    list_issues,
    list_comments,
    update_issue,
)

from app.schemas import (
    CommentCreate,
    CommentResponse,
    ErrorResponse,
    IssueCreate,
    IssueResponse,
    IssueUpdate,
)

from typing import Literal

router = APIRouter()


@router.get(
    "/issues/{number}",
    response_model=IssueResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Issue not found",
        }
    },
)
async def get_issue_endpoint(number: int):
    """Return a single issue by issue number."""

    issue = await get_issue(number)

    return {
        "number": issue["number"],
        "html_url": issue["html_url"],
        "state": issue["state"],
        "title": issue["title"],
        "body": issue["body"],
        "labels": [
            label["name"]
            for label in issue.get("labels", [])
        ],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
    }


@router.get(
    "/issues",
    response_model=list[IssueResponse],
)
@router.get(
    "/issues",
    response_model=list[IssueResponse],
)
async def list_issues_endpoint(
    response: Response,
    state: Literal["open", "closed", "all"] = "open",
    labels: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=100),
):
    """Return issues from the configured GitHub repository."""

    github_issues, link_header = await list_issues(
        state=state,
        labels=labels,
        page=page,
        per_page=per_page,
    )

    if link_header:
        response.headers["Link"] = link_header

    return [
        {
            "number": issue["number"],
            "html_url": issue["html_url"],
            "state": issue["state"],
            "title": issue["title"],
            "body": issue["body"],
            "labels": [
                label["name"]
                for label in issue.get("labels", [])
            ],
            "created_at": issue["created_at"],
            "updated_at": issue["updated_at"],
        }
        for issue in github_issues
        if "pull_request" not in issue
    ]

@router.post(
    "/issues",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid issue payload",
        },
        401: {
            "model": ErrorResponse,
            "description": "GitHub authentication failed",
        },
    },
)
async def create_issue_endpoint(
    payload: IssueCreate,
    response: Response,
):
    """Create a new issue in the configured GitHub repository."""

    github_issue = await create_issue(
        title=payload.title,
        body=payload.body,
        labels=payload.labels,
    )

    response.headers["Location"] = f"/issues/{github_issue['number']}"

    return {
        "number": github_issue["number"],
        "html_url": github_issue["html_url"],
        "state": github_issue["state"],
        "title": github_issue["title"],
        "body": github_issue["body"],
        "labels": [
            label["name"]
            for label in github_issue.get("labels", [])
        ],
        "created_at": github_issue["created_at"],
        "updated_at": github_issue["updated_at"],
    }

@router.patch(
    "/issues/{number}",
    response_model=IssueResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid issue update payload",
        },
        404: {
            "model": ErrorResponse,
            "description": "Issue not found",
        },
    },
)
async def update_issue_endpoint(
    number: int,
    payload: IssueUpdate,
):
    """Update an existing issue."""

    issue = await update_issue(
        number=number,
        title=payload.title,
        body=payload.body,
        state=payload.state,
    )

    return {
        "number": issue["number"],
        "html_url": issue["html_url"],
        "state": issue["state"],
        "title": issue["title"],
        "body": issue["body"],
        "labels": [
            label["name"]
            for label in issue.get("labels", [])
        ],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
    }

@router.post(
    "/issues/{number}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment_endpoint(
    number: int,
    payload: CommentCreate,
):
    """Create a comment on an existing issue."""

    comment = await create_comment(
        number=number,
        body=payload.body,
    )

    return {
        "id": comment["id"],
        "body": comment["body"],
        "user": comment["user"]["login"],
        "created_at": comment["created_at"],
        "html_url": comment["html_url"],
    }

@router.get(
    "/issues/{number}/comments",
    response_model=list[CommentResponse],
)
async def list_comments_endpoint(number: int):
    """Return comments for an existing issue."""

    comments = await list_comments(number)

    return [
        {
            "id": comment["id"],
            "body": comment["body"],
            "user": comment["user"]["login"],
            "created_at": comment["created_at"],
            "html_url": comment["html_url"],
        }
        for comment in comments
    ]
"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Issues API Routes
Description: Provides HTTP endpoints for GitHub issue operations.
"""

from typing import Literal

from fastapi import APIRouter, Query, Response, status

from app.github_client import (
    create_comment,
    create_issue,
    get_issue,
    list_comments,
    list_issues,
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

router = APIRouter()


# ---------------------------------------------------------------------------
# OpenAPI examples
# ---------------------------------------------------------------------------

ISSUE_EXAMPLE = {
    "number": 4,
    "html_url": (
        "https://github.com/"
        "ChanghyunKim-sjsu/CMPE-272-issues-test/issues/4"
    ),
    "state": "open",
    "title": "Example issue",
    "body": "Created through the CMPE 272 Issues Gateway.",
    "labels": ["bug"],
    "created_at": "2026-09-05T20:15:00Z",
    "updated_at": "2026-09-05T20:15:00Z",
}

COMMENT_EXAMPLE = {
    "id": 123456789,
    "body": "This comment was created through the Issues Gateway.",
    "user": "ChanghyunKim-sjsu",
    "created_at": "2026-09-05T20:20:00Z",
    "html_url": (
        "https://github.com/"
        "ChanghyunKim-sjsu/CMPE-272-issues-test/issues/4"
        "#issuecomment-123456789"
    ),
}

VALIDATION_ERROR_EXAMPLE = {
    "error": "validation_error",
    "message": "Invalid request",
    "status_code": 400,
}

AUTH_ERROR_EXAMPLE = {
    "error": "github_api_error",
    "message": "Bad credentials",
    "status_code": 401,
}

NOT_FOUND_ERROR_EXAMPLE = {
    "error": "github_api_error",
    "message": "Issue not found",
    "status_code": 404,
}

RATE_LIMIT_ERROR_EXAMPLE = {
    "error": "github_api_error",
    "message": "GitHub API rate limit exceeded",
    "status_code": 429,
}


def error_response(description: str, example: dict) -> dict:
    """Build reusable OpenAPI metadata for error responses."""

    return {
        "model": ErrorResponse,
        "description": description,
        "content": {
            "application/json": {
                "example": example,
            }
        },
    }


# ---------------------------------------------------------------------------
# Issue endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/issues/{number}",
    response_model=IssueResponse,
    operation_id="get_issue",
    responses={
        200: {
            "description": "Issue returned successfully",
            "content": {
                "application/json": {
                    "example": ISSUE_EXAMPLE,
                }
            },
        },
        400: error_response(
            "Invalid issue number",
            VALIDATION_ERROR_EXAMPLE,
        ),
        401: error_response(
            "GitHub authentication failed",
            AUTH_ERROR_EXAMPLE,
        ),
        404: error_response(
            "Issue not found",
            NOT_FOUND_ERROR_EXAMPLE,
        ),
        429: error_response(
            "GitHub API rate limit exceeded",
            RATE_LIMIT_ERROR_EXAMPLE,
        ),
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
    operation_id="list_issues",
    responses={
        200: {
            "description": "Issues returned successfully",
            "headers": {
                "Link": {
                    "description": "GitHub pagination links",
                    "schema": {
                        "type": "string",
                    },
                },
                "X-Request-ID": {
                    "description": "Request correlation identifier",
                    "schema": {
                        "type": "string",
                    },
                },
            },
            "content": {
                "application/json": {
                    "example": [ISSUE_EXAMPLE],
                }
            },
        },
        400: error_response(
            "Invalid query parameters",
            VALIDATION_ERROR_EXAMPLE,
        ),
        401: error_response(
            "GitHub authentication failed",
            AUTH_ERROR_EXAMPLE,
        ),
        429: error_response(
            "GitHub API rate limit exceeded",
            RATE_LIMIT_ERROR_EXAMPLE,
        ),
    },
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
    operation_id="create_issue",
    responses={
        201: {
            "description": "Issue created successfully",
            "headers": {
                "Location": {
                    "description": "Location of the newly created issue",
                    "schema": {
                        "type": "string",
                    },
                }
            },
            "content": {
                "application/json": {
                    "example": ISSUE_EXAMPLE,
                }
            },
        },
        400: error_response(
            "Invalid issue payload",
            VALIDATION_ERROR_EXAMPLE,
        ),
        401: error_response(
            "GitHub authentication failed",
            AUTH_ERROR_EXAMPLE,
        ),
        429: error_response(
            "GitHub API rate limit exceeded",
            RATE_LIMIT_ERROR_EXAMPLE,
        ),
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

    response.headers["Location"] = (
        f"/issues/{github_issue['number']}"
    )

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
    operation_id="update_issue",
    responses={
        200: {
            "description": "Issue updated successfully",
            "content": {
                "application/json": {
                    "example": ISSUE_EXAMPLE,
                }
            },
        },
        400: error_response(
            "Invalid issue update payload",
            VALIDATION_ERROR_EXAMPLE,
        ),
        401: error_response(
            "GitHub authentication failed",
            AUTH_ERROR_EXAMPLE,
        ),
        404: error_response(
            "Issue not found",
            NOT_FOUND_ERROR_EXAMPLE,
        ),
        429: error_response(
            "GitHub API rate limit exceeded",
            RATE_LIMIT_ERROR_EXAMPLE,
        ),
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


# ---------------------------------------------------------------------------
# Comment endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/issues/{number}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_issue_comment",
    responses={
        201: {
            "description": "Comment created successfully",
            "content": {
                "application/json": {
                    "example": COMMENT_EXAMPLE,
                }
            },
        },
        400: error_response(
            "Invalid comment payload",
            VALIDATION_ERROR_EXAMPLE,
        ),
        401: error_response(
            "GitHub authentication failed",
            AUTH_ERROR_EXAMPLE,
        ),
        404: error_response(
            "Issue not found",
            NOT_FOUND_ERROR_EXAMPLE,
        ),
        429: error_response(
            "GitHub API rate limit exceeded",
            RATE_LIMIT_ERROR_EXAMPLE,
        ),
    },
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
    operation_id="list_issue_comments",
    responses={
        200: {
            "description": "Issue comments returned successfully",
            "content": {
                "application/json": {
                    "example": [COMMENT_EXAMPLE],
                }
            },
        },
        400: error_response(
            "Invalid issue number",
            VALIDATION_ERROR_EXAMPLE,
        ),
        401: error_response(
            "GitHub authentication failed",
            AUTH_ERROR_EXAMPLE,
        ),
        404: error_response(
            "Issue not found",
            NOT_FOUND_ERROR_EXAMPLE,
        ),
        429: error_response(
            "GitHub API rate limit exceeded",
            RATE_LIMIT_ERROR_EXAMPLE,
        ),
    },
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
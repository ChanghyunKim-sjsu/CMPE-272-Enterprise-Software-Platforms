"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: API Schemas
Description: Defines request and response data models for the API.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class IssueCreate(BaseModel):
    """Request model for creating a GitHub issue."""

    title: str = Field(min_length=1)
    body: str | None = None
    labels: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Example issue",
                    "body": "Created through the CMPE 272 Issues Gateway.",
                    "labels": ["bug", "assignment"],
                }
            ]
        }
    )


class IssueUpdate(BaseModel):
    """Request model for updating a GitHub issue."""

    title: str | None = Field(default=None, min_length=1)
    body: str | None = None
    state: Literal["open", "closed"] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Updated issue title",
                    "body": "The issue body has been updated.",
                    "state": "open",
                }
            ]
        }
    )


class IssueResponse(BaseModel):
    """Response model returned by the Issues Gateway."""

    number: int
    html_url: str
    state: Literal["open", "closed"]
    title: str
    body: str | None
    labels: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
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
            ]
        }
    )


class CommentCreate(BaseModel):
    """Request model for creating an issue comment."""

    body: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "body": "This comment was created through the Issues Gateway."
                }
            ]
        }
    )


class CommentResponse(BaseModel):
    """Response model for an issue comment."""

    id: int
    body: str
    user: str
    created_at: datetime
    html_url: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
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
            ]
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response returned by the API."""

    error: str
    message: str
    status_code: int

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": "github_api_error",
                    "message": "Issue not found",
                    "status_code": 404,
                }
            ]
        }
    )


class WebhookEventResponse(BaseModel):
    """Response model for a processed webhook event."""

    id: int
    event: str
    action: str
    issue_number: int | None
    timestamp: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "event": "issues",
                    "action": "opened",
                    "issue_number": 4,
                    "timestamp": "2026-09-05T20:25:00Z",
                }
            ]
        }
    )
"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: API Schemas
Description: Defines request and response data models for the API.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class IssueCreate(BaseModel):
    """Request model for creating a GitHub issue."""

    title: str = Field(min_length=1)
    body: str | None = None
    labels: list[str] = Field(default_factory=list)


class IssueUpdate(BaseModel):
    """Request model for updating a GitHub issue."""

    title: str | None = Field(default=None, min_length=1)
    body: str | None = None
    state: Literal["open", "closed"] | None = None


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


class CommentCreate(BaseModel):
    """Request model for creating an issue comment."""

    body: str = Field(min_length=1)


class CommentResponse(BaseModel):
    """Response model for an issue comment."""

    id: int
    body: str
    user: str
    created_at: datetime
    html_url: str

class ErrorResponse(BaseModel):
    """Standard error response returned by the API."""

    error: str
    message: str
    status_code: int


class WebhookEventResponse(BaseModel):
    """Response model for a processed webhook event."""

    id: int
    event: str
    action: str
    issue_number: int | None
    timestamp: datetime
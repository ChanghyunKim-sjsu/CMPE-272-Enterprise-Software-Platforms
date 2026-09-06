"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Error Handling
Description: Defines custom exceptions for GitHub API failures.
"""


class GitHubAPIError(Exception):
    """Exception raised when the GitHub REST API returns an error."""

    def __init__(
        self,
        status_code: int,
        message: str,
        headers: dict[str, str] | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.headers = headers or {}
        super().__init__(message)
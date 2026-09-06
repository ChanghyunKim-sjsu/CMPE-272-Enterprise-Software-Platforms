"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - Error Mapping
Description: Tests mapping of GitHub API errors to gateway error responses.
"""

from fastapi.testclient import TestClient

from app.config import GITHUB_OWNER, GITHUB_REPO
from app.main import app


client = TestClient(app)

GITHUB_BASE_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
)


def test_github_401_maps_to_gateway_401(httpx_mock):
    """GitHub 401 should be returned as a structured HTTP 401 error."""

    httpx_mock.add_response(
        method="POST",
        url=f"{GITHUB_BASE_URL}/issues",
        status_code=401,
        json={"message": "Bad credentials"},
    )

    response = client.post(
        "/issues",
        json={
            "title": "Test Issue",
            "body": "Testing GitHub 401 mapping.",
            "labels": [],
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["error"] == "github_api_error"
    assert data["message"] == "Bad credentials"
    assert data["status_code"] == 401


def test_github_403_maps_to_gateway_403(httpx_mock):
    """GitHub 403 should be returned as a structured HTTP 403 error."""

    httpx_mock.add_response(
        method="GET",
        url=f"{GITHUB_BASE_URL}/issues/123",
        status_code=403,
        json={"message": "Resource not accessible"},
    )

    response = client.get("/issues/123")

    assert response.status_code == 403

    data = response.json()

    assert data["error"] == "github_api_error"
    assert data["status_code"] == 403


def test_github_404_maps_to_gateway_404(httpx_mock):
    """GitHub 404 should be returned as a structured HTTP 404 error."""

    httpx_mock.add_response(
        method="GET",
        url=f"{GITHUB_BASE_URL}/issues/999999",
        status_code=404,
        json={"message": "Not Found"},
    )

    response = client.get("/issues/999999")

    assert response.status_code == 404

    data = response.json()

    assert data["error"] == "github_api_error"
    assert data["message"] == "Not Found"
    assert data["status_code"] == 404

def test_github_rate_limit_maps_to_429(httpx_mock):
    """GitHub rate limiting should return 429 with Retry-After."""

    httpx_mock.add_response(
        method="GET",
        url=f"{GITHUB_BASE_URL}/issues/123",
        status_code=403,
        json={
            "message": "API rate limit exceeded",
        },
        headers={
            "X-RateLimit-Remaining": "0",
            "Retry-After": "60",
        },
    )

    response = client.get("/issues/123")

    assert response.status_code == 429

    assert response.headers["Retry-After"] == "60"

    data = response.json()

    assert data["error"] == "github_api_error"
    assert data["status_code"] == 429
    assert "rate limit" in data["message"].lower()
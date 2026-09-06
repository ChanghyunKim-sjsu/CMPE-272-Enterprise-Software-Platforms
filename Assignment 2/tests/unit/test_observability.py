"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - Observability
Description: Tests request ID behavior for HTTP requests.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_response_contains_generated_request_id():
    """A request without an ID should receive a generated request ID."""

    response = client.get("/healthz")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_existing_request_id_is_preserved():
    """A client-provided request ID should be returned unchanged."""

    request_id = "cmpe272-test-request-id"

    response = client.get(
        "/healthz",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id
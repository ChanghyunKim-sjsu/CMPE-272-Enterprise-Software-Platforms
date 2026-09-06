"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - OpenAPI
Description: Tests the custom runtime OpenAPI contract.
"""

from app.main import app, custom_openapi


def test_custom_openapi_regenerates_schema():
    """Custom OpenAPI should regenerate and clean the runtime schema."""

    app.openapi_schema = None

    schema = custom_openapi()

    assert schema["openapi"].startswith("3.1")

    for path_item in schema["paths"].values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            responses = operation.get("responses", {})
            assert "422" not in responses

    schemas = schema.get("components", {}).get("schemas", {})

    assert "HTTPValidationError" not in schemas
    assert "ValidationError" not in schemas


def test_custom_openapi_uses_cached_schema():
    """Custom OpenAPI should reuse the cached schema."""

    app.openapi_schema = None

    first_schema = custom_openapi()
    second_schema = custom_openapi()

    assert first_schema is second_schema


def test_openapi_operation_ids_are_unique():
    """Every documented operation ID should be unique."""

    app.openapi_schema = None
    schema = custom_openapi()

    operation_ids = []

    for path_item in schema["paths"].values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "operationId" in operation:
                operation_ids.append(operation["operationId"])

    assert len(operation_ids) == len(set(operation_ids))


def test_etag_is_documented():
    """GET /issues/{number} should document ETag conditional requests."""

    app.openapi_schema = None
    schema = custom_openapi()

    get_issue = schema["paths"]["/issues/{number}"]["get"]

    assert "304" in get_issue["responses"]

    parameter_names = {
        parameter["name"] for parameter in get_issue.get("parameters", [])
    }

    assert "If-None-Match" in parameter_names

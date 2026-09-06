"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: OpenAPI Contract Enhancement
Description: Adds required security metadata, examples, and response documentation
to the generated OpenAPI 3.1 contract.
"""

import yaml


OPENAPI_FILE = "openapi.yaml"


with open(OPENAPI_FILE, "r", encoding="utf-8") as file:
    spec = yaml.safe_load(file)


# -------------------------------------------------------------------
# Security scheme
# -------------------------------------------------------------------

components = spec.setdefault("components", {})
security_schemes = components.setdefault("securitySchemes", {})

security_schemes["GitHubBearer"] = {
    "type": "http",
    "scheme": "bearer",
    "description": (
        "Represents the server-side GitHub credential configured through "
        "GITHUB_TOKEN. The gateway uses this credential when calling GitHub."
    ),
}


# -------------------------------------------------------------------
# Common examples
# -------------------------------------------------------------------

issue_example = {
    "number": 4,
    "html_url": "https://github.com/example/repository/issues/4",
    "state": "open",
    "title": "Example issue",
    "body": "Example issue body.",
    "labels": ["bug"],
    "created_at": "2026-09-05T20:00:00Z",
    "updated_at": "2026-09-05T20:00:00Z",
}

error_400_example = {
    "error": "validation_error",
    "message": "Invalid request.",
    "status_code": 400,
}

error_401_example = {
    "error": "github_api_error",
    "message": "Bad credentials",
    "status_code": 401,
}

error_404_example = {
    "error": "github_api_error",
    "message": "Not Found",
    "status_code": 404,
}


def add_json_example(response_spec, example):
    """Add an application/json example to an OpenAPI response."""

    content = response_spec.setdefault("content", {})
    json_content = content.setdefault(
        "application/json",
        {},
    )

    json_content["example"] = example


# -------------------------------------------------------------------
# POST /issues
# -------------------------------------------------------------------

post_issues = spec["paths"]["/issues"]["post"]
post_issues["security"] = [{"GitHubBearer": []}]

if "201" in post_issues["responses"]:
    add_json_example(
        post_issues["responses"]["201"],
        issue_example,
    )

if "400" in post_issues["responses"]:
    add_json_example(
        post_issues["responses"]["400"],
        error_400_example,
    )

if "401" in post_issues["responses"]:
    add_json_example(
        post_issues["responses"]["401"],
        error_401_example,
    )


# -------------------------------------------------------------------
# GET /issues
# -------------------------------------------------------------------

get_issues = spec["paths"]["/issues"]["get"]
get_issues["security"] = [{"GitHubBearer": []}]

get_issues["responses"]["200"]["headers"] = {
    "Link": {
        "description": (
            "GitHub pagination links such as next, previous, first, and last."
        ),
        "schema": {
            "type": "string",
        },
    },
    "X-Request-ID": {
        "description": "Request tracing identifier.",
        "schema": {
            "type": "string",
        },
    },
}


# -------------------------------------------------------------------
# GET/PATCH /issues/{number}
# -------------------------------------------------------------------

issue_path = spec["paths"]["/issues/{number}"]

for method in ("get", "patch"):
    if method in issue_path:
        issue_path[method]["security"] = [{"GitHubBearer": []}]

if "404" in issue_path["get"]["responses"]:
    add_json_example(
        issue_path["get"]["responses"]["404"],
        error_404_example,
    )


# -------------------------------------------------------------------
# Comment routes
# -------------------------------------------------------------------

comment_path = spec["paths"]["/issues/{number}/comments"]

for method in ("get", "post"):
    if method in comment_path:
        comment_path[method]["security"] = [{"GitHubBearer": []}]


# -------------------------------------------------------------------
# Webhook documentation
# -------------------------------------------------------------------

webhook = spec["paths"]["/webhook"]["post"]

webhook["description"] = (
    "Receives GitHub issues, issue_comment, and ping events. "
    "The X-Hub-Signature-256 header is verified using HMAC SHA-256 "
    "and WEBHOOK_SECRET. Successful deliveries return HTTP 204."
)

webhook["responses"].setdefault(
    "401",
    {
        "description": "Invalid webhook signature",
        "content": {
            "application/json": {
                "example": {
                    "error": "invalid_signature",
                    "message": "Webhook signature validation failed.",
                    "status_code": 401,
                }
            }
        },
    },
)

webhook["responses"].setdefault(
    "400",
    {
        "description": "Unsupported event, action, or invalid payload",
        "content": {
            "application/json": {
                "example": {
                    "error": "unsupported_event",
                    "message": "Unsupported GitHub webhook event.",
                    "status_code": 400,
                }
            }
        },
    },
)


# -------------------------------------------------------------------
# Save
# -------------------------------------------------------------------

with open(OPENAPI_FILE, "w", encoding="utf-8") as file:
    yaml.safe_dump(
        spec,
        file,
        sort_keys=False,
        allow_unicode=True,
    )


print("openapi.yaml enhanced successfully")
## Overview

This project implements a FastAPI service that wraps the GitHub REST API for issue management in a dedicated test repository.

The service supports:

- Creating GitHub issues
- Listing issues with pagination
- Retrieving individual issues
- Updating, closing, and reopening issues
- Creating and retrieving issue comments
- Conditional GET requests using `ETag` and `If-None-Match`
- Receiving GitHub `issues`, `issue_comment`, and `ping` webhooks
- HMAC SHA-256 webhook signature verification
- Webhook persistence and idempotent processing using SQLite
- Structured API and validation error responses
- GitHub rate-limit detection and `Retry-After` propagation
- Request IDs and structured logging
- OpenAPI 3.1 documentation with reusable schemas and examples
- Unit and opt-in integration testing
- Ruff linting and formatting
- Docker deployment
- Automated GitHub Actions CI

## Project Structure

```text
CMPE-272-Enterprise-Software-Platforms/
├── .github/
│   └── workflows/
│       └── ci.yml
└── Assignment 2/
    ├── app/
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   ├── events.py
    │   │   ├── issues.py
    │   │   └── webhook.py
    │   ├── __init__.py
    │   ├── config.py
    │   ├── errors.py
    │   ├── event_store.py
    │   ├── github_client.py
    │   ├── main.py
    │   ├── pagination.py
    │   ├── schemas.py
    │   └── webhook.py
    ├── tests/
    │   ├── unit/
    │   └── integration/
    ├── .dockerignore
    ├── .env.example
    ├── .gitignore
    ├── DESIGN.md
    ├── Dockerfile
    ├── Makefile
    ├── enhance_openapi.py
    ├── openapi.json
    ├── openapi.yaml
    ├── pyproject.toml
    ├── requirements-dev.txt
    ├── requirements.txt
    └── README.md
```

## Run Locally

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the runtime and development dependencies:

```bash
make install
```

The equivalent command is:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Start the FastAPI service:

```bash
make run
```

The service is available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/healthz
```

Expected response:

```json
{
  "status": "ok"
}
```

## Development Commands

The project includes a `Makefile` for common development tasks:

```bash
make install       # Install runtime and development dependencies
make run           # Start the FastAPI development server
make test          # Run the unit test suite
make coverage      # Run tests with the 80% coverage requirement
make lint          # Run Ruff lint and formatting checks
make openapi       # Regenerate openapi.json and openapi.yaml
make docker-build  # Build the Docker image
```

### Conditional GET with ETag

The `GET /issues/{number}` endpoint supports conditional requests using GitHub's entity tag.

First, retrieve the issue and its `ETag` header:

```bash
curl -i http://127.0.0.1:8000/issues/2
```

Send the returned value through `If-None-Match`:

```bash
curl -i \
  -H 'If-None-Match: "<etag-value>"' \
  http://127.0.0.1:8000/issues/2
```

If the issue has not changed, the gateway returns:

```text
HTTP/1.1 304 Not Modified
```

The `304` response contains no response body. If the issue has changed, the gateway returns HTTP `200` with the current issue representation and updated `ETag`.

## Unit Tests

Run all unit tests:

```bash
make test
```

Run the tests with line coverage:

```bash
make coverage
```

The current verified result is:

```text
45 passed
95.21% total line coverage
```

The test suite covers:

- Issue CRUD and comment routes
- Request validation and invalid issue states
- GitHub 401, 403, 404, 422, and 500 error mapping
- GitHub rate-limit handling
- Pagination parameters and Link headers
- ETag propagation and HTTP 304 responses
- HMAC SHA-256 signature validation
- Tampered webhook payloads
- Unsupported webhook events and actions
- Missing webhook delivery IDs
- SQLite persistence and idempotency
- Runtime OpenAPI generation
- Unique OpenAPI operation IDs
- Request ID generation and preservation

The coverage command enforces the assignment requirement using:

```text
--cov-fail-under=80
```

## OpenAPI

The API provides an OpenAPI 3.1 contract in both formats:

```text
openapi.yaml
openapi.json
```

The contract is generated from the running FastAPI application using:

```bash
make openapi
```

It documents:

- All nine API operations
- Request and response models
- Reusable component schemas
- Successful and error response examples
- Pagination and request-ID headers
- Webhook authentication headers and payloads
- ETag and `If-None-Match` behavior
- HTTP 304 conditional responses

The application converts FastAPI request validation failures to HTTP 400. Therefore, the runtime OpenAPI customization removes FastAPI's automatic HTTP 422 responses and unused validation schemas.

GitHub Actions verifies that the committed OpenAPI contract matches the runtime-generated contract.

## Continuous Integration

The repository includes a GitHub Actions workflow at:

```text
.github/workflows/ci.yml
```

The workflow runs automatically for pushes and pull requests targeting `main`.

It verifies:

- Dependency installation
- Ruff linting and formatting
- Unit tests
- Minimum 80% line coverage
- Runtime OpenAPI generation
- OpenAPI contract synchronization
- Unique operation IDs
- Absence of undocumented HTTP 422 responses
- Docker image construction

The real GitHub integration test is intentionally excluded from normal CI because it creates and modifies resources in the dedicated GitHub test repository.

# Assignment 2 - GitHub Issues Gateway

**Course:** CMPE 272 - Enterprise Software Platforms  
**Author:** Changhyun Kim

## Overview

This project implements a FastAPI service that wraps the GitHub REST API for issue management in a dedicated test repository.

The service supports:

- Creating GitHub issues
- Listing issues with pagination
- Retrieving a single issue
- Updating, closing, and reopening issues
- Creating and retrieving issue comments
- Receiving GitHub webhooks
- HMAC SHA-256 webhook signature verification
- Webhook persistence and deduplication using SQLite
- Structured error responses
- GitHub rate-limit handling
- Request IDs and structured logging
- OpenAPI 3.1 documentation
- Unit and integration testing
- Docker deployment

## Project Structure

```text
Assignment 2/
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
├── enhance_openapi.py
├── openapi.yaml
├── requirements.txt
└── README.md
```

## Environment Variables

Create a `.env` file using `.env.example` as a template.

```env
GITHUB_TOKEN=your_github_token_here
GITHUB_OWNER=your_github_username
GITHUB_REPO=your_test_repository
WEBHOOK_SECRET=your_webhook_secret
PORT=8000
```

The GitHub token should be a fine-grained Personal Access Token limited to the dedicated test repository.

Required GitHub permissions:

- Issues: Read and write
- Metadata: Read-only

Secrets must not be hard-coded or committed to Git.

## Run Locally

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI service:

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger UI is available at:

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

## Docker

Build the Docker image:

```bash
docker build -t cmpe272-issues-gateway .
```

Run the container:

```bash
docker run -d \
  --name cmpe272-issues-gateway \
  --env-file .env \
  -p 8001:8000 \
  cmpe272-issues-gateway
```

Verify the container:

```bash
curl http://127.0.0.1:8001/healthz
```

View running containers:

```bash
docker ps
```

Stop the container:

```bash
docker stop cmpe272-issues-gateway
```

Remove the stopped container if needed:

```bash
docker rm cmpe272-issues-gateway
```

The `.env` file is excluded from the Docker build context through `.dockerignore`.

## API Endpoints

### Create Issue

```http
POST /issues
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/issues \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example issue",
    "body": "Created through the Issues Gateway.",
    "labels": []
  }'
```

A successful request returns HTTP `201 Created` and a `Location` header.

### List Issues

```http
GET /issues
```

Supported query parameters:

- `state=open|closed|all`
- `labels`
- `page`
- `per_page`

Example:

```bash
curl "http://127.0.0.1:8000/issues?state=open&page=1&per_page=30"
```

GitHub pagination information from the `Link` response header is propagated by the gateway.

### Get a Single Issue

```http
GET /issues/{number}
```

Example:

```bash
curl http://127.0.0.1:8000/issues/1
```

### Update an Issue

```http
PATCH /issues/{number}
```

Example:

```bash
curl -X PATCH http://127.0.0.1:8000/issues/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated issue title",
    "body": "Updated issue body."
  }'
```

### Close an Issue

GitHub does not support deleting issues. Closing an issue is used as the delete operation for CRUD purposes.

```bash
curl -X PATCH http://127.0.0.1:8000/issues/1 \
  -H "Content-Type: application/json" \
  -d '{
    "state": "closed"
  }'
```

### Reopen an Issue

```bash
curl -X PATCH http://127.0.0.1:8000/issues/1 \
  -H "Content-Type: application/json" \
  -d '{
    "state": "open"
  }'
```

### Create an Issue Comment

```http
POST /issues/{number}/comments
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/issues/1/comments \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Example comment"
  }'
```

### List Issue Comments

```http
GET /issues/{number}/comments
```

Example:

```bash
curl http://127.0.0.1:8000/issues/1/comments
```

### View Processed Webhook Events

```http
GET /events
```

Example:

```bash
curl http://127.0.0.1:8000/events
```

### Health Check

```http
GET /healthz
```

Example:

```bash
curl http://127.0.0.1:8000/healthz
```

## Webhook Setup

For local GitHub webhook testing, expose the FastAPI service through a public HTTPS tunnel.

Using Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflare returns a temporary public URL similar to:

```text
https://example-name.trycloudflare.com
```

Configure the GitHub repository webhook using:

```text
Payload URL:
https://example-name.trycloudflare.com/webhook

Content type:
application/json
```

Use the same value configured in `WEBHOOK_SECRET`.

Select the following GitHub webhook events:

- Issues
- Issue comments

Keep the webhook active and SSL verification enabled.

## Webhook Security

GitHub sends the `X-Hub-Signature-256` header with webhook deliveries.

The gateway calculates an HMAC SHA-256 signature using `WEBHOOK_SECRET` and compares the calculated value using:

```python
hmac.compare_digest()
```

This provides constant-time comparison.

Requests with invalid signatures return:

```text
401 Unauthorized
```

Valid supported webhook deliveries return:

```text
204 No Content
```

Supported events include:

- `ping`
- `issues`
- `issue_comment`

## Webhook Persistence and Idempotency

Processed webhook events are stored in a local SQLite database.

Stored information includes:

- GitHub delivery ID
- Event type
- Action
- Issue number
- Timestamp

The combination of the GitHub delivery ID and action is used as a unique deduplication key.

If GitHub redelivers the same webhook, the gateway safely acknowledges the request without storing the same event twice.

Processed events can be inspected through:

```http
GET /events
```

## Webhook Redelivery

To redeliver a webhook from GitHub:

1. Open the test repository.
2. Go to **Settings**.
3. Select **Webhooks**.
4. Select the configured webhook.
5. Open **Recent Deliveries**.
6. Select a delivery.
7. Click **Redeliver**.

The service safely handles duplicate deliveries using idempotent event storage.

## Error Handling

The service maps GitHub API failures into structured JSON error responses.

Example:

```json
{
  "error": "github_api_error",
  "message": "Not Found",
  "status_code": 404
}
```

Important mappings include:

- GitHub 401 → HTTP 401
- GitHub 403 → HTTP 403
- GitHub 404 → HTTP 404
- GitHub 422 → HTTP 400
- Unexpected GitHub failures → HTTP 502

Request validation failures are returned as HTTP 400.

## Rate Limiting

The gateway checks GitHub rate-limit responses.

A GitHub HTTP 429 response, or an HTTP 403 response with:

```text
X-RateLimit-Remaining: 0
```

is translated into:

```text
429 Too Many Requests
```

When available, the `Retry-After` header is propagated to the client.

## Observability

Every request receives an `X-Request-ID` response header.

If the client provides an `X-Request-ID`, the gateway preserves it. Otherwise, the gateway generates a UUID.

Structured request logs include information such as:

- request ID
- HTTP method
- request path
- status code
- request duration
- GitHub delivery ID when applicable

Secrets, GitHub tokens, webhook secrets, and raw webhook signatures are not logged.

## Unit Tests

Run all unit tests:

```bash
pytest tests/unit -v
```

Run unit tests with line coverage:

```bash
pytest tests/unit --cov=app --cov-report=term-missing
```

The test suite covers:

- Request validation
- Invalid issue state handling
- GitHub 401/403/404 error mapping
- GitHub rate-limit handling
- HMAC signature validation
- Tampered webhook payloads
- Webhook route validation
- SQLite persistence
- Webhook deduplication
- GitHub API mocking
- Pagination utilities
- GitHub Link header parsing
- Issue API routes
- Comment API routes
- Request ID behavior

The current project contains 38 unit tests and is designed to exceed the assignment target of 80% line coverage.

## Integration Test

The real GitHub integration test is disabled by default to avoid accidentally creating issues during normal unit testing.

Run it explicitly with:

```bash
RUN_INTEGRATION_TESTS=1 \
pytest tests/integration/test_github_integration.py -v
```

The integration test exercises the dedicated GitHub test repository and verifies:

- Issue creation
- Issue retrieval
- Issue title/body update
- Issue closing
- Issue reopening
- Comment creation
- Comment retrieval
- Final cleanup by closing the test issue

## OpenAPI

The required OpenAPI 3.1 contract is provided in:

```text
openapi.yaml
```

The contract documents:

- All service routes
- Request schemas
- Response schemas
- Error responses
- Example responses
- Pagination headers
- Webhook responses
- Security metadata

FastAPI also provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

## Security

Security measures include:

- Fine-grained GitHub Personal Access Token
- Repository-specific GitHub permissions
- Environment-variable based secrets
- `.env` excluded from Git
- `.env` excluded from the Docker image
- HMAC SHA-256 webhook authentication
- Constant-time signature comparison
- No secret values in logs
- Structured error responses
- Minimal GitHub token permissions

## Design Note

Additional implementation decisions and trade-offs are documented in:

```text
DESIGN.md
```

## Test Repository

A dedicated GitHub repository is used for API and webhook testing:

```text
CMPE-272-issues-test
```

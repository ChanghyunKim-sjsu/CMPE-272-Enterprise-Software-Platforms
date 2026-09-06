# Design Note

**Course:** CMPE 272 - Enterprise Software Platforms  
**Assignment:** Assignment 2 - GitHub Issues Gateway  
**Author:** Changhyun Kim

## 1. Error Mapping Strategy

The gateway translates GitHub REST API failures into consistent HTTP responses for its clients.

GitHub errors are converted into a reusable structured JSON format containing:

- `error`
- `message`
- `status_code`

For example, a GitHub 404 response is returned by the gateway as:

```json
{
  "error": "github_api_error",
  "message": "Not Found",
  "status_code": 404
}
```

The gateway uses the following general mappings:

- GitHub 401 → HTTP 401
- GitHub 403 → HTTP 403
- GitHub 404 → HTTP 404
- GitHub 422 → HTTP 400
- Unexpected upstream GitHub errors → HTTP 502

GitHub validation failures use HTTP 422, but the gateway exposes them as HTTP 400 because they represent invalid input from the gateway client's perspective.

Request validation performed by FastAPI and Pydantic is also converted into HTTP 400 responses so the API follows the assignment contract.

Rate limiting is handled separately. A GitHub HTTP 429 response, or an HTTP 403 response where `X-RateLimit-Remaining` is zero, is translated into HTTP 429. When GitHub provides `Retry-After`, the gateway forwards that value to the client. If only `X-RateLimit-Reset` is available, the gateway can calculate an appropriate retry interval.

This strategy separates client errors, GitHub upstream failures, and gateway failures while keeping the API response format predictable.

## 2. Pagination Strategy

The `GET /issues` endpoint supports the following GitHub-compatible query parameters:

- `state`
- `labels`
- `page`
- `per_page`

The `state` parameter accepts `open`, `closed`, or `all`.

The `per_page` parameter is validated between 1 and 100, matching GitHub's maximum supported page size.

Pagination parameters are forwarded to the GitHub REST API rather than being reimplemented inside the gateway.

When GitHub returns a `Link` response header, the gateway forwards the same header to its own client. This preserves GitHub pagination semantics and allows clients to determine the next, previous, first, or last page.

A pagination utility is also provided to parse GitHub `Link` headers into relation-to-URL mappings such as:

```text
next
prev
first
last
```

The parsing logic and Link-header behavior are covered by automated unit tests.

## 3. Webhook Deduplication and Idempotency

GitHub includes an `X-GitHub-Delivery` identifier with webhook deliveries.

The gateway stores processed webhook information in SQLite, including:

- delivery ID
- event type
- action
- issue number
- timestamp

The combination of:

```text
delivery_id + action
```

is configured as a unique database key.

When the first delivery is received, the event is stored normally.

If GitHub retries the same delivery, SQLite rejects the duplicate unique key. The application treats this situation as an already-processed event rather than as a server failure.

The gateway still returns a successful acknowledgement so GitHub does not continue retrying an event that has already been processed.

This provides retry-safe and idempotent webhook handling.

The `/events` endpoint exposes recently processed webhook deliveries for debugging and demonstration.

SQLite was selected because the assignment allows a local persistence mechanism and the service runs as a single-instance development application.

For a production system with multiple application instances, a shared durable database or message-processing system would be required to provide deduplication across instances.

## 4. Security Trade-offs

Secrets and configuration values are provided through environment variables rather than being embedded in application source code.

The GitHub credential is a fine-grained Personal Access Token restricted to the dedicated test repository and limited to the permissions required by the application.

Webhook authentication uses HMAC SHA-256.

GitHub sends a signature in the:

```text
X-Hub-Signature-256
```

header.

The gateway calculates the expected signature using `WEBHOOK_SECRET` and compares the two values using:

```python
hmac.compare_digest()
```

This provides constant-time comparison and avoids simple string comparison for sensitive signature verification.

The service intentionally does not log:

- GitHub tokens
- webhook secrets
- raw webhook signatures

The `.env` file is excluded from Git through `.gitignore` and excluded from Docker builds through `.dockerignore`.

Request IDs and structured logging provide request traceability without exposing authentication information.

The service also validates event types and webhook actions before persistence.

A temporary Cloudflare Tunnel is used only for local webhook demonstration. The tunnel provides a public HTTPS endpoint for GitHub while the FastAPI application continues to run locally.

In a production deployment, a stable HTTPS endpoint, centralized secret management, durable distributed storage, and stronger operational monitoring would be preferred.

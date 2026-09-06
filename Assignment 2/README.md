# Assignment 2 - GitHub Issues Gateway

CMPE 272 - Enterprise Software Platforms

Author: Changhyun Kim

## Overview

This project implements a FastAPI service that wraps the GitHub REST API
for issue management in a dedicated test repository.

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
- Request IDs and structured logging
- OpenAPI 3.1 documentation
- Unit and integration testing
- Docker deployment

## Project Structure

```text
Assignment 2/
├── app/
│   ├── routers/
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
├── Dockerfile
├── .dockerignore
├── .env.example
├── openapi.yaml
├── requirements.txt
└── README.md

"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Webhook Event Store
Description: Stores processed GitHub webhook deliveries in SQLite.
"""

import sqlite3
from contextlib import closing
from datetime import datetime, timezone

DATABASE_PATH = "webhook_events.db"


def initialize_database():
    """Create the webhook event table if it does not already exist."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                delivery_id TEXT NOT NULL,
                event TEXT NOT NULL,
                action TEXT NOT NULL,
                issue_number INTEGER,
                timestamp TEXT NOT NULL,
                UNIQUE(delivery_id, action)
            )
            """
        )


def save_event(
    delivery_id: str,
    event: str,
    action: str,
    issue_number: int | None,
) -> bool:
    """Store a webhook event.

    Returns True when a new event is inserted.
    Returns False when the delivery was already processed.
    """

    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute(
                """
                INSERT INTO webhook_events (
                    delivery_id,
                    event,
                    action,
                    issue_number,
                    timestamp
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    delivery_id,
                    event,
                    action,
                    issue_number,
                    timestamp,
                ),
            )

        return True

    except sqlite3.IntegrityError:
        return False


def list_events(limit: int = 20):
    """Return the most recently processed webhook events."""

    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                id,
                event,
                action,
                issue_number,
                timestamp
            FROM webhook_events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]

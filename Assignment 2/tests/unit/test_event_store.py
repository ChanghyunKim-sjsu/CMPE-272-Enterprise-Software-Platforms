"""
CMPE 272 - Enterprise Software Platforms
Assignment 2 - GitHub Issues Gateway

Author: Changhyun Kim
Component: Unit Tests - Event Store
Description: Tests SQLite webhook event persistence and deduplication.
"""

import app.event_store as event_store


def test_save_and_list_webhook_event(tmp_path, monkeypatch):
    """A webhook event should be stored and returned from SQLite."""

    test_db = tmp_path / "test_webhook_events.db"

    monkeypatch.setattr(
        event_store,
        "DATABASE_PATH",
        str(test_db),
    )

    event_store.initialize_database()

    inserted = event_store.save_event(
        delivery_id="delivery-001",
        event="issues",
        action="opened",
        issue_number=10,
    )

    assert inserted is True

    events = event_store.list_events()

    assert len(events) == 1
    assert events[0]["event"] == "issues"
    assert events[0]["action"] == "opened"
    assert events[0]["issue_number"] == 10


def test_duplicate_webhook_event_is_not_inserted(
    tmp_path,
    monkeypatch,
):
    """The same delivery ID and action should only be stored once."""

    test_db = tmp_path / "test_webhook_events.db"

    monkeypatch.setattr(
        event_store,
        "DATABASE_PATH",
        str(test_db),
    )

    event_store.initialize_database()

    first_insert = event_store.save_event(
        delivery_id="delivery-duplicate",
        event="issues",
        action="opened",
        issue_number=20,
    )

    second_insert = event_store.save_event(
        delivery_id="delivery-duplicate",
        event="issues",
        action="opened",
        issue_number=20,
    )

    assert first_insert is True
    assert second_insert is False

    events = event_store.list_events()

    assert len(events) == 1
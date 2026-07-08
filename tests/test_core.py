from __future__ import annotations

from pathlib import Path

import pytest

from notifier.config import ConfigError, parse_config
from notifier.jsonpath import get_path
from notifier.models import SendResult
from notifier.service import NotifierService
from notifier.store import NotificationStore
from notifier.template import render_template


class FakeSourceClient:
    def __init__(self, items_by_source):
        self.items_by_source = items_by_source

    def fetch_source(self, source):
        return self.items_by_source[source.name]


class FakeSender:
    def __init__(self):
        self.sent = []

    def send_text(self, target, message):
        self.sent.append((target, message))
        return SendResult(ok=True)


def make_config(tmp_path: Path):
    return parse_config(
        {
            "site": {"api_base_url": "http://api.test/api/v1", "web_base_url": "http://web.test"},
            "wechat": {"group_name": "test group"},
            "sender": {"type": "stdout"},
            "poll": {"interval_seconds": 60},
            "storage": {"sqlite_path": str(tmp_path / "state.sqlite3")},
            "sources": [
                {
                    "name": "listings",
                    "label": "闲置",
                    "url": "/listings",
                    "method": "GET",
                    "query": {"page": 1},
                    "items_path": "items",
                    "id_field": "id",
                    "created_at_field": "createdAt",
                    "detail_url_template": "{web_base_url}/listings/{id}",
                    "fields": {"title": "title", "price": "price", "author": "author.displayName"},
                    "message_template": "【新闲置】{title} {price} {author} {url}",
                }
            ],
        }
    )


def test_get_path_supports_nested_objects_and_arrays():
    data = {"items": [{"author": {"displayName": "Alice"}}]}
    assert get_path(data, "items.0.author.displayName") == "Alice"
    assert get_path(data, "items.1.author.displayName", "") == ""


def test_template_missing_values_render_empty():
    assert render_template("{title}-{missing}", {"title": "A"}) == "A-"


def test_config_validation_rejects_short_poll_interval(tmp_path):
    raw = {
        "site": {"api_base_url": "x", "web_base_url": "y"},
        "wechat": {"group_name": "g"},
        "poll": {"interval_seconds": 1},
        "sources": [],
    }
    with pytest.raises(ConfigError):
        parse_config(raw)


def test_poll_once_sends_new_items_once(tmp_path):
    config = make_config(tmp_path)
    item = type(
        "Item",
        (),
        {
            "source_name": "listings",
            "source_label": "闲置",
            "item_id": "1",
            "title": "Desk",
            "created_at": "2026-07-08T00:00:00Z",
            "url": "http://web.test/listings/1",
            "fields": {"id": "1", "title": "Desk", "price": 100, "author": "Alice", "url": "http://web.test/listings/1"},
            "dedupe_key": "listings:1",
        },
    )()
    sender = FakeSender()
    service = NotifierService(
        config,
        source_client=FakeSourceClient({"listings": [item]}),
        sender=sender,
        store=NotificationStore(config.storage.sqlite_path),
    )

    assert service.poll_once() == 1
    assert service.poll_once() == 0
    assert len(sender.sent) == 1
    assert "Desk" in sender.sent[0][1]

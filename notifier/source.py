from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from .config import AppConfig, SourceConfig
from .jsonpath import get_path
from .models import NotificationItem


class SourceError(RuntimeError):
    pass


class HttpSourceClient:
    def __init__(self, config: AppConfig, timeout_seconds: int = 20):
        self.config = config
        self.timeout_seconds = timeout_seconds

    def fetch_source(self, source: SourceConfig) -> list[NotificationItem]:
        url = self._build_url(source)
        request = Request(url, method="GET", headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise SourceError(f"{source.name}: failed to fetch {url}: {exc}") from exc

        raw_items = get_path(payload, source.items_path)
        if not isinstance(raw_items, list):
            raise SourceError(f"{source.name}: items_path did not resolve to a list")

        items: list[NotificationItem] = []
        for raw_item in raw_items:
            item = self._map_item(source, raw_item)
            if item:
                items.append(item)
        return items

    def fetch_all(self) -> dict[str, list[NotificationItem]]:
        return {source.name: self.fetch_source(source) for source in self.config.sources}

    def _build_url(self, source: SourceConfig) -> str:
        if source.url.startswith("http://") or source.url.startswith("https://"):
            base = source.url
        else:
            base = urljoin(self.config.site.api_base_url.rstrip("/") + "/", source.url.lstrip("/"))

        query = urlencode(source.query, doseq=True)
        return f"{base}?{query}" if query else base

    def _map_item(self, source: SourceConfig, raw_item: Any) -> NotificationItem | None:
        item_id = get_path(raw_item, source.id_field)
        title = get_path(raw_item, source.fields.get("title", "title"))
        created_at = get_path(raw_item, source.created_at_field)
        if item_id is None or title is None or created_at is None:
            return None

        fields = {name: get_path(raw_item, path) for name, path in source.fields.items()}
        fields["id"] = item_id
        fields["title"] = title
        fields["created_at"] = created_at
        url = source.detail_url_template.format(
            web_base_url=self.config.site.web_base_url.rstrip("/"),
            api_base_url=self.config.site.api_base_url.rstrip("/"),
            **fields,
        )
        fields["url"] = url

        return NotificationItem(
            source_name=source.name,
            source_label=source.label,
            item_id=str(item_id),
            title=str(title),
            created_at=str(created_at),
            url=url,
            fields=fields,
        )

from __future__ import annotations

import time
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import AppConfig, SourceConfig
from .models import NotificationItem
from .senders.base import Sender
from .source import HttpSourceClient
from .store import NotificationStore
from .template import render_template


class NotifierService:
    def __init__(
        self,
        config: AppConfig,
        source_client: HttpSourceClient | None = None,
        sender: Sender | None = None,
        store: NotificationStore | None = None,
    ):
        self.config = config
        self.source_client = source_client or HttpSourceClient(config)
        if sender is None:
            from .senders import create_sender

            sender = create_sender(config.sender)
        self.sender = sender
        self.store = store or NotificationStore(config.storage.sqlite_path)

    def preview(self) -> str:
        messages: list[str] = []
        for source in self.config.sources:
            for item in self.source_client.fetch_source(source):
                messages.append(self.render_item(source, item))
        return "\n\n".join(messages)

    def send_test(self) -> bool:
        result = self.sender.send_text(self.config.wechat.group_name, "微信通知机器人测试消息")
        if not result.ok:
            raise RuntimeError(result.message)
        return True

    def send_digest_now(self, mark_run: bool = False) -> int:
        sections: list[str] = []
        sent_count = 0
        for source in self.config.sources:
            items = self.source_client.fetch_source(source)
            if not items:
                continue
            rendered = [self.render_item(source, item) for item in items]
            sections.append(f"【{source.label}最新】\n" + "\n\n".join(rendered))
            sent_count += len(rendered)

        if not sections:
            return 0

        messages = ["\n\n".join(sections)] if self.config.digest.combine_sources else sections
        for message in messages:
            result = self.sender.send_text(self.config.wechat.group_name, message)
            if not result.ok:
                raise RuntimeError(result.message)

        if mark_run:
            self.store.mark_digest_run(self._today())
        return sent_count

    def poll_once(self) -> int:
        sent = 0
        for source in self.config.sources:
            items = list(reversed(self.source_client.fetch_source(source)))
            for item in items:
                if self.store.has_sent(item.dedupe_key):
                    continue
                message = self.render_item(source, item)
                result = self.sender.send_text(self.config.wechat.group_name, message)
                if not result.ok:
                    raise RuntimeError(result.message)
                self.store.mark_sent(item.dedupe_key, item.source_name, item.item_id)
                sent += 1
        return sent

    def run_forever(self) -> None:
        while True:
            if self._should_send_digest():
                self.send_digest_now(mark_run=True)
            if self.config.poll.enabled:
                self.poll_once()
            time.sleep(self.config.poll.interval_seconds)

    def render_item(self, source: SourceConfig, item: NotificationItem) -> str:
        return render_template(source.message_template, item.fields)

    def _should_send_digest(self) -> bool:
        now = self._now()
        if now.strftime("%H:%M") != self.config.schedule.daily_digest_time:
            return False
        today = now.strftime("%Y-%m-%d")
        return not self.store.has_digest_run(today)

    def _today(self) -> str:
        return self._now().strftime("%Y-%m-%d")

    def _now(self) -> datetime:
        return datetime.now(ZoneInfo(self.config.schedule.timezone))

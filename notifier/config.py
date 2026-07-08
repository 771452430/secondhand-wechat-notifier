from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class SiteConfig:
    api_base_url: str
    web_base_url: str


@dataclass(frozen=True)
class WeChatConfig:
    group_name: str


@dataclass(frozen=True)
class SenderConfig:
    type: str = "macos-accessibility"


@dataclass(frozen=True)
class PollConfig:
    enabled: bool = True
    interval_seconds: int = 60


@dataclass(frozen=True)
class ScheduleConfig:
    daily_digest_time: str = "09:00"
    timezone: str = "Asia/Shanghai"


@dataclass(frozen=True)
class StorageConfig:
    sqlite_path: str = "./notifier-state.sqlite3"


@dataclass(frozen=True)
class DigestConfig:
    combine_sources: bool = True


@dataclass(frozen=True)
class SourceConfig:
    name: str
    label: str
    url: str
    method: str
    query: dict[str, Any]
    items_path: str
    id_field: str
    created_at_field: str
    detail_url_template: str
    fields: dict[str, str]
    message_template: str


@dataclass(frozen=True)
class AppConfig:
    site: SiteConfig
    wechat: WeChatConfig
    sender: SenderConfig = field(default_factory=SenderConfig)
    poll: PollConfig = field(default_factory=PollConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    digest: DigestConfig = field(default_factory=DigestConfig)
    sources: list[SourceConfig] = field(default_factory=list)


def load_config(path: str | Path) -> AppConfig:
    with Path(path).open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    return parse_config(raw)


def parse_config(raw: dict[str, Any]) -> AppConfig:
    try:
        site = SiteConfig(**_required_mapping(raw, "site"))
        wechat = WeChatConfig(**_required_mapping(raw, "wechat"))
        sender = SenderConfig(**raw.get("sender", {}))
        poll = PollConfig(**raw.get("poll", {}))
        schedule = ScheduleConfig(**raw.get("schedule", {}))
        storage = StorageConfig(**raw.get("storage", {}))
        digest = DigestConfig(**raw.get("digest", {}))
        sources = [SourceConfig(**source) for source in raw.get("sources", [])]
    except TypeError as exc:
        raise ConfigError(f"Invalid config shape: {exc}") from exc

    config = AppConfig(
        site=site,
        wechat=wechat,
        sender=sender,
        poll=poll,
        schedule=schedule,
        storage=storage,
        digest=digest,
        sources=sources,
    )
    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    if not config.site.api_base_url:
        raise ConfigError("site.api_base_url is required")
    if not config.site.web_base_url:
        raise ConfigError("site.web_base_url is required")
    if not config.wechat.group_name:
        raise ConfigError("wechat.group_name is required")
    if config.poll.interval_seconds < 5:
        raise ConfigError("poll.interval_seconds must be at least 5")
    if not _is_hhmm(config.schedule.daily_digest_time):
        raise ConfigError("schedule.daily_digest_time must use HH:MM format")
    if not config.sources:
        raise ConfigError("sources must contain at least one source")

    names = set()
    for source in config.sources:
        if source.name in names:
            raise ConfigError(f"duplicated source name: {source.name}")
        names.add(source.name)
        if source.method.upper() != "GET":
            raise ConfigError(f"{source.name}: only GET is supported in v1")
        for attr in ("url", "items_path", "id_field", "created_at_field", "detail_url_template", "message_template"):
            if not getattr(source, attr):
                raise ConfigError(f"{source.name}: {attr} is required")


def _required_mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} is required")
    return value


def _is_hhmm(value: str) -> bool:
    parts = value.split(":")
    if len(parts) != 2:
        return False
    try:
        hour, minute = int(parts[0]), int(parts[1])
    except ValueError:
        return False
    return 0 <= hour <= 23 and 0 <= minute <= 59

from __future__ import annotations

import argparse
from pathlib import Path

from .config import ConfigError, load_config
from .launchd import install_service, service_logs, service_status, start_service, stop_service, uninstall_service
from .preset import SECONDHAND_CONFIG
from .service import NotifierService


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except ConfigError as exc:
        print(f"Config error: {exc}")
        return 2
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wechat-notifier")
    sub = parser.add_subparsers(required=True)

    init = sub.add_parser("init-config")
    init.add_argument("--preset", default="secondhand", choices=["secondhand"])
    init.add_argument("--output", required=True)
    init.set_defaults(func=cmd_init_config)

    for name in ["validate-config", "preview", "send-test", "digest-now", "run"]:
        command = sub.add_parser(name)
        command.add_argument("--config", required=True)
        command.set_defaults(func=globals()[f"cmd_{name.replace('-', '_')}"])

    install = sub.add_parser("install-service")
    install.add_argument("--config", required=True)
    install.set_defaults(func=cmd_install_service)

    uninstall = sub.add_parser("uninstall-service")
    uninstall.set_defaults(func=cmd_uninstall_service)

    service = sub.add_parser("service")
    service_sub = service.add_subparsers(required=True)
    for name in ["start", "stop", "status", "logs"]:
        command = service_sub.add_parser(name)
        command.set_defaults(func=globals()[f"cmd_service_{name}"])

    return parser


def cmd_init_config(args: argparse.Namespace) -> int:
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(f"{output} already exists")
    output.write_text(SECONDHAND_CONFIG, encoding="utf-8")
    print(f"created {output}")
    return 0


def cmd_validate_config(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    print(f"config ok: {len(config.sources)} sources")
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    service = NotifierService(load_config(args.config))
    print(service.preview())
    return 0


def cmd_send_test(args: argparse.Namespace) -> int:
    service = NotifierService(load_config(args.config))
    service.send_test()
    print("test message sent")
    return 0


def cmd_digest_now(args: argparse.Namespace) -> int:
    service = NotifierService(load_config(args.config))
    count = service.send_digest_now()
    print(f"digest sent: {count} items")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    service = NotifierService(load_config(args.config))
    service.run_forever()
    return 0


def cmd_install_service(args: argparse.Namespace) -> int:
    path = install_service(args.config)
    print(f"installed launchd service: {path}")
    return 0


def cmd_uninstall_service(args: argparse.Namespace) -> int:
    uninstall_service()
    print("uninstalled launchd service")
    return 0


def cmd_service_start(args: argparse.Namespace) -> int:
    start_service()
    print("service started")
    return 0


def cmd_service_stop(args: argparse.Namespace) -> int:
    stop_service()
    print("service stopped")
    return 0


def cmd_service_status(args: argparse.Namespace) -> int:
    print(service_status())
    return 0


def cmd_service_logs(args: argparse.Namespace) -> int:
    print(service_logs())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

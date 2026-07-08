from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

LABEL = "com.secondhand.wechat-notifier"


def plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def log_path() -> Path:
    return Path.home() / "Library" / "Logs" / "secondhand-wechat-notifier.log"


def install_service(config_path: str) -> Path:
    config = Path(config_path).expanduser().resolve()
    if not config.exists():
        raise FileNotFoundError(f"config not found: {config}")

    executable = shutil.which("notifier")
    program_arguments = [executable, "run", "--config", str(config)] if executable else [
        sys.executable,
        "-m",
        "notifier.cli",
        "run",
        "--config",
        str(config),
    ]
    log = log_path()
    log.parent.mkdir(parents=True, exist_ok=True)
    plist = {
        "Label": LABEL,
        "ProgramArguments": program_arguments,
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(log),
        "StandardErrorPath": str(log),
        "WorkingDirectory": os.getcwd(),
    }

    target = plist_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        plistlib.dump(plist, handle)
    return target


def uninstall_service() -> None:
    stop_service()
    target = plist_path()
    if target.exists():
        target.unlink()


def start_service() -> None:
    _launchctl("load", str(plist_path()))


def stop_service() -> None:
    target = plist_path()
    if target.exists():
        subprocess.run(["launchctl", "unload", str(target)], check=False)


def service_status() -> str:
    result = subprocess.run(["launchctl", "list"], capture_output=True, text=True, check=False)
    return "running" if LABEL in result.stdout else "stopped"


def service_logs() -> str:
    path = log_path()
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[-8000:]


def _launchctl(*args: str) -> None:
    subprocess.run(["launchctl", *args], check=True)

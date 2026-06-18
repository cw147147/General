"""Simple in-process daily scheduler."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from world_cup_whatsapp_agent.config import AgentSettings


def run_daily(settings: AgentSettings, job: Callable[[], object]) -> None:
    """Run ``job`` every day at the configured local send time."""

    timezone = ZoneInfo(settings.timezone)
    while True:
        next_run = next_run_at(
            now=datetime.now(timezone),
            hour=settings.send_hour,
            minute=settings.send_minute,
            timezone=timezone,
        )
        sleep_seconds = max((next_run - datetime.now(timezone)).total_seconds(), 0)
        print(f"Next World Cup WhatsApp digest scheduled for {next_run.isoformat()}")
        time.sleep(sleep_seconds)
        job()


def next_run_at(now: datetime, hour: int, minute: int, timezone: ZoneInfo) -> datetime:
    candidate = now.astimezone(timezone).replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )
    if candidate <= now.astimezone(timezone):
        candidate += timedelta(days=1)
    return candidate

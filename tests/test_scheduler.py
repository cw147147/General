from datetime import datetime
from zoneinfo import ZoneInfo

from world_cup_whatsapp_agent.scheduler.daily_10am import next_run_at


def test_next_run_at_returns_today_when_time_is_still_upcoming():
    timezone = ZoneInfo("Pacific/Auckland")
    now = datetime(2026, 6, 18, 9, 30, tzinfo=timezone)

    next_run = next_run_at(now=now, hour=10, minute=0, timezone=timezone)

    assert next_run == datetime(2026, 6, 18, 10, 0, tzinfo=timezone)


def test_next_run_at_returns_tomorrow_after_configured_time():
    timezone = ZoneInfo("Pacific/Auckland")
    now = datetime(2026, 6, 18, 10, 1, tzinfo=timezone)

    next_run = next_run_at(now=now, hour=10, minute=0, timezone=timezone)

    assert next_run == datetime(2026, 6, 19, 10, 0, tzinfo=timezone)

"""Command-line entrypoint for the World Cup WhatsApp digest agent."""

from __future__ import annotations

import argparse
import sys

from world_cup_whatsapp_agent.config import AgentSettings, ConfigurationError
from world_cup_whatsapp_agent.factory import build_agent
from world_cup_whatsapp_agent.scheduler.daily_10am import run_daily


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Send FIFA Men's World Cup 2026 updates by WhatsApp."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_once_parser = subparsers.add_parser("run-once", help="Build and send one digest.")
    run_once_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the WhatsApp body instead of sending it.",
    )

    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Run continuously and send at the configured daily time.",
    )
    schedule_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print scheduled WhatsApp bodies instead of sending them.",
    )

    args = parser.parse_args(argv)
    settings = AgentSettings.from_env()

    try:
        agent = build_agent(settings, dry_run=args.dry_run or None)
        if args.command == "run-once":
            agent.run_once()
            return 0

        run_daily(settings, agent.run_once)
        return 0
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

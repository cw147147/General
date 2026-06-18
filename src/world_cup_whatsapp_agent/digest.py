"""Digest orchestration and message formatting."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from world_cup_whatsapp_agent.config import AgentSettings
from world_cup_whatsapp_agent.integrations.football_data import FootballDataClient
from world_cup_whatsapp_agent.integrations.news import GoogleNewsClient
from world_cup_whatsapp_agent.integrations.whatsapp import WhatsAppSender
from world_cup_whatsapp_agent.models import (
    GroupStanding,
    MatchResult,
    NewsStory,
    WorldCupDigest,
)


class WorldCupDigestAgent:
    """Builds and sends the daily World Cup WhatsApp digest."""

    def __init__(
        self,
        settings: AgentSettings,
        football_client: FootballDataClient,
        news_client: GoogleNewsClient,
        whatsapp_sender: WhatsAppSender,
    ) -> None:
        self._settings = settings
        self._football_client = football_client
        self._news_client = news_client
        self._whatsapp_sender = whatsapp_sender

    def run_once(self) -> str:
        digest = self.build_digest()
        message = format_digest(digest, timezone_name=self._settings.timezone)
        return self._whatsapp_sender.send(message)

    def build_digest(self) -> WorldCupDigest:
        return WorldCupDigest(
            generated_at=datetime.now(ZoneInfo(self._settings.timezone)),
            results=self._football_client.latest_results(self._settings.teams),
            standings=self._football_client.group_standings(self._settings.teams),
            news=self._news_client.top_stories(self._settings.teams),
        )


def format_digest(digest: WorldCupDigest, timezone_name: str) -> str:
    local_timezone = ZoneInfo(timezone_name)
    generated_at = digest.generated_at.astimezone(local_timezone)
    lines = [
        "FIFA Men's World Cup 2026 daily update",
        f"Generated {generated_at:%a %d %b %Y, %H:%M %Z}",
        "",
        "Latest results",
        *_format_results(digest.results, local_timezone),
        "",
        "Group standings",
        *_format_standings(digest.standings),
        "",
        "Top news",
        *_format_news(digest.news),
    ]
    return "\n".join(lines).strip()


def _format_results(results: tuple[MatchResult, ...], timezone: ZoneInfo) -> list[str]:
    if not results:
        return ["No finished World Cup 2026 results found yet for the selected teams."]

    formatted: list[str] = []
    for result in results:
        played_at = result.utc_date.astimezone(timezone)
        score = _format_score(result.team_score, result.opponent_score)
        context = ", ".join(value for value in (result.group, result.stage) if value)
        context_suffix = f" ({context})" if context else ""
        formatted.append(
            f"- {result.team} {score} {result.opponent} - {played_at:%d %b, %H:%M}{context_suffix}"
        )
    return formatted


def _format_score(team_score: int | None, opponent_score: int | None) -> str:
    if team_score is None or opponent_score is None:
        return "vs"
    return f"{team_score}-{opponent_score}"


def _format_standings(standings: tuple[GroupStanding, ...]) -> list[str]:
    if not standings:
        return ["No group standings found yet for the selected teams."]

    formatted: list[str] = []
    for standing in standings:
        formatted.append(f"- {standing.group}")
        for row in standing.rows:
            formatted.append(
                "  "
                f"{row.position}. {row.team} "
                f"{row.points} pts "
                f"({row.played}P {row.won}W {row.drawn}D {row.lost}L GD {row.goal_difference:+d})"
            )
    return formatted


def _format_news(news: tuple[NewsStory, ...]) -> list[str]:
    if not news:
        return ["No World Cup news stories found yet for the selected teams."]

    formatted: list[str] = []
    for story in news:
        source_suffix = f" - {story.source}" if story.source else ""
        formatted.append(f"- {story.team}: {story.title}{source_suffix}")
        formatted.append(f"  {story.link}")
    return formatted

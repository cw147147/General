"""News lookup using Google News RSS."""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from world_cup_whatsapp_agent.models import NewsStory


class NewsLookupError(RuntimeError):
    """Raised when news lookup fails."""


class GoogleNewsClient:
    """Fetches the first Google News RSS item for each requested team."""

    def __init__(
        self,
        locale: str = "en-US",
        region: str = "US:en",
        base_url: str = "https://news.google.com/rss/search",
    ) -> None:
        self._locale = locale
        self._region = region
        self._base_url = base_url

    def top_stories(self, teams: tuple[str, ...]) -> tuple[NewsStory, ...]:
        stories: list[NewsStory] = []
        for team in teams:
            story = self.top_story(team)
            if story:
                stories.append(story)
        return tuple(stories)

    def top_story(self, team: str) -> NewsStory | None:
        query = f'"{team}" "FIFA World Cup 2026" football'
        params = urlencode({"q": query, "hl": self._locale, "gl": "US", "ceid": self._region})
        request = Request(
            f"{self._base_url}?{params}",
            headers={"User-Agent": "world-cup-whatsapp-agent/0.1"},
        )

        try:
            with urlopen(request, timeout=30) as response:
                xml = response.read()
        except OSError as exc:
            raise NewsLookupError(f"Could not fetch Google News RSS: {exc}") from exc

        channel = ElementTree.fromstring(xml).find("channel")
        if channel is None:
            return None

        item = channel.find("item")
        if item is None:
            return None

        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source_element = item.find("source")
        source = source_element.text.strip() if source_element is not None and source_element.text else None
        published_at = _parse_pub_date(item.findtext("pubDate"))

        if not title or not link:
            return None

        return NewsStory(
            team=team,
            title=title,
            link=link,
            source=source,
            published_at=published_at,
        )


def _parse_pub_date(value: str | None) -> datetime | None:
    if not value:
        return None

    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

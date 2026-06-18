"""football-data.org integration for World Cup results and standings."""

from __future__ import annotations

import json
import unicodedata
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from world_cup_whatsapp_agent.models import GroupStanding, MatchResult, StandingRow


FINISHED_STATUSES = {"FINISHED", "AWARDED"}
TEAM_ALIASES = {
    "Ivory Coast": ("Ivory Coast", "Cote d'Ivoire", "Côte d'Ivoire"),
    "England": ("England",),
    "New Zealand": ("New Zealand",),
    "Norway": ("Norway",),
}


class FootballDataError(RuntimeError):
    """Raised when football-data.org returns an unusable response."""


def _normalise(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in decomposed if not unicodedata.combining(char))
    return ascii_value.casefold()


def _aliases_for(team: str) -> set[str]:
    aliases = TEAM_ALIASES.get(team, (team,))
    return {_normalise(alias) for alias in aliases}


def _matches_team(name: str, requested_team: str) -> bool:
    return _normalise(name) in _aliases_for(requested_team)


def _parse_utc_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class FootballDataClient:
    """Fetches competition matches and standings from football-data.org v4."""

    def __init__(
        self,
        token: str,
        competition_code: str = "WC",
        season: int = 2026,
        base_url: str = "https://api.football-data.org/v4",
    ) -> None:
        self._token = token
        self._competition_code = competition_code
        self._season = season
        self._base_url = base_url.rstrip("/")

    def latest_results(self, teams: tuple[str, ...]) -> tuple[MatchResult, ...]:
        payload = self._get(
            f"/competitions/{self._competition_code}/matches",
            {"season": str(self._season)},
        )
        matches = payload.get("matches", [])

        latest_by_team: dict[str, MatchResult] = {}
        for match in matches:
            if match.get("status") not in FINISHED_STATUSES:
                continue

            home_team = match.get("homeTeam", {}).get("name")
            away_team = match.get("awayTeam", {}).get("name")
            if not home_team or not away_team:
                continue

            for requested_team in teams:
                if _matches_team(home_team, requested_team):
                    result = self._to_result(match, requested_team, away_team, home=True)
                elif _matches_team(away_team, requested_team):
                    result = self._to_result(match, requested_team, home_team, home=False)
                else:
                    continue

                previous = latest_by_team.get(requested_team)
                if previous is None or result.utc_date > previous.utc_date:
                    latest_by_team[requested_team] = result

        return tuple(
            latest_by_team[team]
            for team in teams
            if team in latest_by_team
        )

    def group_standings(self, teams: tuple[str, ...]) -> tuple[GroupStanding, ...]:
        payload = self._get(
            f"/competitions/{self._competition_code}/standings",
            {"season": str(self._season)},
        )
        selected_groups: list[GroupStanding] = []
        seen_groups: set[str] = set()

        for standing in payload.get("standings", []):
            if standing.get("type") not in {None, "TOTAL"}:
                continue

            rows = tuple(
                StandingRow(
                    position=int(row.get("position", 0)),
                    team=row.get("team", {}).get("name", "Unknown"),
                    played=int(row.get("playedGames", 0)),
                    won=int(row.get("won", 0)),
                    drawn=int(row.get("draw", 0)),
                    lost=int(row.get("lost", 0)),
                    goal_difference=int(row.get("goalDifference", 0)),
                    points=int(row.get("points", 0)),
                )
                for row in standing.get("table", [])
            )

            if not rows:
                continue

            includes_requested_team = any(
                _matches_team(row.team, requested_team)
                for row in rows
                for requested_team in teams
            )
            group_name = standing.get("group") or standing.get("stage") or "Standings"
            if includes_requested_team and group_name not in seen_groups:
                selected_groups.append(GroupStanding(group=group_name, rows=rows))
                seen_groups.add(group_name)

        return tuple(selected_groups)

    def _to_result(
        self,
        match: dict[str, Any],
        team: str,
        opponent: str,
        *,
        home: bool,
    ) -> MatchResult:
        full_time = match.get("score", {}).get("fullTime", {})
        home_score = full_time.get("home")
        away_score = full_time.get("away")
        return MatchResult(
            team=team,
            opponent=opponent,
            team_score=home_score if home else away_score,
            opponent_score=away_score if home else home_score,
            status=match.get("status", "UNKNOWN"),
            utc_date=_parse_utc_datetime(match.get("utcDate")),
            stage=match.get("stage"),
            group=match.get("group"),
        )

    def _get(self, path: str, query: dict[str, str]) -> dict[str, Any]:
        url = f"{self._base_url}{path}?{urlencode(query)}"
        request = Request(url, headers={"X-Auth-Token": self._token})

        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise FootballDataError(f"football-data.org returned HTTP {exc.code}: {details}") from exc
        except OSError as exc:
            raise FootballDataError(f"Could not reach football-data.org: {exc}") from exc

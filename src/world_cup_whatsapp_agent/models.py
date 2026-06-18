"""Shared data structures for digest generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MatchResult:
    team: str
    opponent: str
    team_score: int | None
    opponent_score: int | None
    status: str
    utc_date: datetime
    stage: str | None = None
    group: str | None = None


@dataclass(frozen=True)
class StandingRow:
    position: int
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goal_difference: int
    points: int


@dataclass(frozen=True)
class GroupStanding:
    group: str
    rows: tuple[StandingRow, ...]


@dataclass(frozen=True)
class NewsStory:
    team: str
    title: str
    link: str
    source: str | None = None
    published_at: datetime | None = None


@dataclass(frozen=True)
class WorldCupDigest:
    generated_at: datetime
    results: tuple[MatchResult, ...]
    standings: tuple[GroupStanding, ...]
    news: tuple[NewsStory, ...]

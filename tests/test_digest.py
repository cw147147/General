from datetime import datetime, timezone

from world_cup_whatsapp_agent.digest import format_digest
from world_cup_whatsapp_agent.models import (
    GroupStanding,
    MatchResult,
    NewsStory,
    StandingRow,
    WorldCupDigest,
)


def test_format_digest_includes_results_standings_and_news_link():
    digest = WorldCupDigest(
        generated_at=datetime(2026, 6, 18, 22, 0, tzinfo=timezone.utc),
        results=(
            MatchResult(
                team="England",
                opponent="Norway",
                team_score=2,
                opponent_score=1,
                status="FINISHED",
                utc_date=datetime(2026, 6, 18, 20, 0, tzinfo=timezone.utc),
                group="Group B",
                stage="GROUP_STAGE",
            ),
        ),
        standings=(
            GroupStanding(
                group="Group B",
                rows=(
                    StandingRow(
                        position=1,
                        team="England",
                        played=1,
                        won=1,
                        drawn=0,
                        lost=0,
                        goal_difference=1,
                        points=3,
                    ),
                ),
            ),
        ),
        news=(
            NewsStory(
                team="England",
                title="England open World Cup campaign with win",
                link="https://example.com/story",
                source="Example News",
            ),
        ),
    )

    message = format_digest(digest, timezone_name="Pacific/Auckland")

    assert "FIFA Men's World Cup 2026 daily update" in message
    assert "England 2-1 Norway" in message
    assert "1. England 3 pts" in message
    assert "https://example.com/story" in message

from world_cup_whatsapp_agent.integrations.football_data import FootballDataClient


class FakeFootballDataClient(FootballDataClient):
    def __init__(self, payloads):
        super().__init__(token="token")
        self.payloads = payloads

    def _get(self, path, query):
        return self.payloads[path]


def test_latest_results_returns_latest_finished_match_per_requested_team():
    client = FakeFootballDataClient(
        {
            "/competitions/WC/matches": {
                "matches": [
                    {
                        "status": "FINISHED",
                        "utcDate": "2026-06-12T19:00:00Z",
                        "homeTeam": {"name": "Côte d'Ivoire"},
                        "awayTeam": {"name": "England"},
                        "score": {"fullTime": {"home": 1, "away": 1}},
                        "group": "Group A",
                        "stage": "GROUP_STAGE",
                    },
                    {
                        "status": "FINISHED",
                        "utcDate": "2026-06-16T19:00:00Z",
                        "homeTeam": {"name": "New Zealand"},
                        "awayTeam": {"name": "Norway"},
                        "score": {"fullTime": {"home": 0, "away": 2}},
                        "group": "Group C",
                        "stage": "GROUP_STAGE",
                    },
                    {
                        "status": "TIMED",
                        "utcDate": "2026-06-20T19:00:00Z",
                        "homeTeam": {"name": "England"},
                        "awayTeam": {"name": "Norway"},
                        "score": {"fullTime": {"home": None, "away": None}},
                    },
                ]
            }
        }
    )

    results = client.latest_results(("Ivory Coast", "England", "New Zealand", "Norway"))

    assert [result.team for result in results] == [
        "Ivory Coast",
        "England",
        "New Zealand",
        "Norway",
    ]
    assert results[0].opponent == "England"
    assert results[0].team_score == 1
    assert results[3].opponent == "New Zealand"
    assert results[3].team_score == 2


def test_group_standings_returns_groups_containing_requested_teams():
    client = FakeFootballDataClient(
        {
            "/competitions/WC/standings": {
                "standings": [
                    {
                        "type": "TOTAL",
                        "group": "Group A",
                        "table": [
                            {
                                "position": 1,
                                "team": {"name": "Côte d'Ivoire"},
                                "playedGames": 1,
                                "won": 0,
                                "draw": 1,
                                "lost": 0,
                                "goalDifference": 0,
                                "points": 1,
                            },
                            {
                                "position": 2,
                                "team": {"name": "England"},
                                "playedGames": 1,
                                "won": 0,
                                "draw": 1,
                                "lost": 0,
                                "goalDifference": 0,
                                "points": 1,
                            },
                        ],
                    },
                    {
                        "type": "TOTAL",
                        "group": "Group H",
                        "table": [
                            {
                                "position": 1,
                                "team": {"name": "Brazil"},
                                "playedGames": 1,
                                "won": 1,
                                "draw": 0,
                                "lost": 0,
                                "goalDifference": 2,
                                "points": 3,
                            }
                        ],
                    },
                ]
            }
        }
    )

    standings = client.group_standings(("Ivory Coast", "England"))

    assert len(standings) == 1
    assert standings[0].group == "Group A"
    assert [row.team for row in standings[0].rows] == ["Côte d'Ivoire", "England"]

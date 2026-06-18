"""Environment-backed settings for the World Cup WhatsApp agent."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_TEAMS = ("New Zealand", "England", "Ivory Coast", "Norway")


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing."""


def _csv_env(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw_value = os.getenv(name)
    if not raw_value:
        return default

    values = tuple(item.strip() for item in raw_value.split(",") if item.strip())
    return values or default


def _bool_env(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AgentSettings:
    teams: tuple[str, ...]
    timezone: str
    send_hour: int
    send_minute: int
    football_data_token: str | None
    football_competition_code: str
    football_season: int
    news_locale: str
    news_region: str
    twilio_account_sid: str | None
    twilio_auth_token: str | None
    twilio_whatsapp_from: str | None
    whatsapp_to: str | None
    dry_run: bool

    @classmethod
    def from_env(cls) -> "AgentSettings":
        return cls(
            teams=_csv_env("WORLD_CUP_TEAMS", DEFAULT_TEAMS),
            timezone=os.getenv("WORLD_CUP_DIGEST_TIMEZONE", "Pacific/Auckland"),
            send_hour=int(os.getenv("WORLD_CUP_DIGEST_HOUR", "10")),
            send_minute=int(os.getenv("WORLD_CUP_DIGEST_MINUTE", "0")),
            football_data_token=os.getenv("FOOTBALL_DATA_TOKEN"),
            football_competition_code=os.getenv("FOOTBALL_COMPETITION_CODE", "WC"),
            football_season=int(os.getenv("FOOTBALL_SEASON", "2026")),
            news_locale=os.getenv("GOOGLE_NEWS_LOCALE", "en-US"),
            news_region=os.getenv("GOOGLE_NEWS_REGION", "US:en"),
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
            twilio_whatsapp_from=os.getenv("TWILIO_WHATSAPP_FROM"),
            whatsapp_to=os.getenv("WHATSAPP_TO"),
            dry_run=_bool_env("WORLD_CUP_AGENT_DRY_RUN", False),
        )

    def require_football_token(self) -> str:
        if not self.football_data_token:
            raise ConfigurationError("FOOTBALL_DATA_TOKEN is required to fetch World Cup data.")
        return self.football_data_token

    def require_twilio_settings(self) -> tuple[str, str, str, str]:
        missing = [
            name
            for name, value in (
                ("TWILIO_ACCOUNT_SID", self.twilio_account_sid),
                ("TWILIO_AUTH_TOKEN", self.twilio_auth_token),
                ("TWILIO_WHATSAPP_FROM", self.twilio_whatsapp_from),
                ("WHATSAPP_TO", self.whatsapp_to),
            )
            if not value
        ]
        if missing:
            raise ConfigurationError(
                "Missing WhatsApp delivery settings: " + ", ".join(missing)
            )

        return (
            self.twilio_account_sid or "",
            self.twilio_auth_token or "",
            self.twilio_whatsapp_from or "",
            self.whatsapp_to or "",
        )

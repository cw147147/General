"""Factory helpers for wiring the production agent."""

from __future__ import annotations

from world_cup_whatsapp_agent.config import AgentSettings
from world_cup_whatsapp_agent.digest import WorldCupDigestAgent
from world_cup_whatsapp_agent.integrations.football_data import FootballDataClient
from world_cup_whatsapp_agent.integrations.news import GoogleNewsClient
from world_cup_whatsapp_agent.integrations.whatsapp import (
    DryRunWhatsAppSender,
    TwilioWhatsAppSender,
    WhatsAppSender,
)


def build_agent(settings: AgentSettings, *, dry_run: bool | None = None) -> WorldCupDigestAgent:
    effective_dry_run = settings.dry_run if dry_run is None else dry_run
    football_client = FootballDataClient(
        token=settings.require_football_token(),
        competition_code=settings.football_competition_code,
        season=settings.football_season,
    )
    news_client = GoogleNewsClient(locale=settings.news_locale, region=settings.news_region)
    whatsapp_sender = _build_sender(settings, effective_dry_run)

    return WorldCupDigestAgent(
        settings=settings,
        football_client=football_client,
        news_client=news_client,
        whatsapp_sender=whatsapp_sender,
    )


def _build_sender(settings: AgentSettings, dry_run: bool) -> WhatsAppSender:
    if dry_run:
        return DryRunWhatsAppSender()

    account_sid, auth_token, from_number, to_number = settings.require_twilio_settings()
    return TwilioWhatsAppSender(
        account_sid=account_sid,
        auth_token=auth_token,
        from_number=from_number,
        to_number=to_number,
    )

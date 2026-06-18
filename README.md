# World Cup WhatsApp Agent

A small Python agent that sends a daily WhatsApp digest at 10:00 with:

- Latest FIFA Men's World Cup 2026 results for New Zealand, England, Ivory Coast, and Norway
- Group standings containing those teams
- One top World Cup news story with a link for each team

The agent is dependency-light and uses Python's standard library for HTTP, scheduling, and RSS parsing.

## Providers

- **Football data:** [football-data.org](https://www.football-data.org/) v4
- **News:** Google News RSS search
- **WhatsApp:** Twilio WhatsApp Messages API

## Configuration

Copy `.env.example` and fill in provider credentials:

```bash
cp .env.example .env
```

Required production values:

| Variable | Purpose |
| --- | --- |
| `FOOTBALL_DATA_TOKEN` | football-data.org API token |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_WHATSAPP_FROM` | Twilio WhatsApp sender, for example `+14155238886` |
| `WHATSAPP_TO` | Recipient WhatsApp number |

Important defaults:

| Variable | Default |
| --- | --- |
| `WORLD_CUP_TEAMS` | `New Zealand,England,Ivory Coast,Norway` |
| `WORLD_CUP_DIGEST_TIMEZONE` | `Pacific/Auckland` |
| `WORLD_CUP_DIGEST_HOUR` | `10` |
| `WORLD_CUP_DIGEST_MINUTE` | `0` |
| `FOOTBALL_COMPETITION_CODE` | `WC` |
| `FOOTBALL_SEASON` | `2026` |

Set `WORLD_CUP_DIGEST_TIMEZONE` if 10am should be interpreted in another timezone.

## Run once

From the repository root:

```bash
set -a
. ./.env
set +a
PYTHONPATH=src python -m world_cup_whatsapp_agent run-once
```

Use dry-run mode to print the WhatsApp body instead of sending it:

```bash
PYTHONPATH=src python -m world_cup_whatsapp_agent run-once --dry-run
```

## Schedule daily at 10am

### Option 1: resident process

```bash
set -a
. ./.env
set +a
PYTHONPATH=src python -m world_cup_whatsapp_agent schedule
```

This process calculates the next configured 10:00 run in `WORLD_CUP_DIGEST_TIMEZONE`, sleeps until then, sends the digest, and repeats daily.

### Option 2: cron

For a host already running in the desired timezone:

```cron
0 10 * * * cd /path/to/repo && set -a && . ./.env && set +a && PYTHONPATH=src python -m world_cup_whatsapp_agent run-once
```

If the host timezone differs, either set the host cron timezone or use the resident scheduler.

## Tests

```bash
PYTHONPATH=src python -m unittest
```

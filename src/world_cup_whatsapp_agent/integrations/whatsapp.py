"""WhatsApp delivery integrations."""

from __future__ import annotations

import base64
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class WhatsAppDeliveryError(RuntimeError):
    """Raised when WhatsApp delivery fails."""


class WhatsAppSender:
    def send(self, body: str) -> str:
        raise NotImplementedError


class DryRunWhatsAppSender(WhatsAppSender):
    """Prints messages instead of sending them."""

    def send(self, body: str) -> str:
        print(body)
        return "dry-run"


class TwilioWhatsAppSender(WhatsAppSender):
    """Sends WhatsApp messages through Twilio's Messages API."""

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        to_number: str,
        base_url: str = "https://api.twilio.com/2010-04-01",
    ) -> None:
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = _with_whatsapp_prefix(from_number)
        self._to_number = _with_whatsapp_prefix(to_number)
        self._base_url = base_url.rstrip("/")

    def send(self, body: str) -> str:
        payload = urlencode(
            {
                "From": self._from_number,
                "To": self._to_number,
                "Body": body,
            }
        ).encode("utf-8")
        credentials = f"{self._account_sid}:{self._auth_token}".encode("utf-8")
        authorization = base64.b64encode(credentials).decode("ascii")
        request = Request(
            f"{self._base_url}/Accounts/{self._account_sid}/Messages.json",
            data=payload,
            headers={
                "Authorization": f"Basic {authorization}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8")
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise WhatsAppDeliveryError(f"Twilio returned HTTP {exc.code}: {details}") from exc
        except OSError as exc:
            raise WhatsAppDeliveryError(f"Could not reach Twilio: {exc}") from exc


def _with_whatsapp_prefix(number: str) -> str:
    if number.startswith("whatsapp:"):
        return number
    return f"whatsapp:{number}"

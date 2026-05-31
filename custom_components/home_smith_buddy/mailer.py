"""SMTP delivery for Home Smith Buddy tickets."""

from __future__ import annotations

from email.message import EmailMessage
import logging
from typing import Any

import aiosmtplib

from .const import (
    CONF_ENCRYPTION,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_RECIPIENT,
    CONF_SENDER,
    CONF_USERNAME,
    ENCRYPTION_STARTTLS,
    ENCRYPTION_TLS,
)

_LOGGER = logging.getLogger(__name__)


class TicketDeliveryError(Exception):
    """Raised when a ticket email cannot be delivered."""


def _client_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    """Build the connection kwargs shared by send and connection-test."""
    encryption = config[CONF_ENCRYPTION]
    return {
        "hostname": config[CONF_HOST],
        "port": config[CONF_PORT],
        "use_tls": encryption == ENCRYPTION_TLS,
        "start_tls": encryption == ENCRYPTION_STARTTLS,
        "username": config.get(CONF_USERNAME) or None,
        "password": config.get(CONF_PASSWORD) or None,
    }


async def async_test_connection(config: dict[str, Any]) -> None:
    """Open an SMTP session (and authenticate) to validate config.

    Raises TicketDeliveryError on any failure so the config flow can surface it.
    """
    kwargs = _client_kwargs(config)
    client = aiosmtplib.SMTP(
        hostname=kwargs["hostname"],
        port=kwargs["port"],
        use_tls=kwargs["use_tls"],
        start_tls=kwargs["start_tls"],
    )
    try:
        await client.connect()
        if kwargs["username"]:
            await client.login(kwargs["username"], kwargs["password"])
    except (aiosmtplib.SMTPException, OSError, ValueError) as err:
        raise TicketDeliveryError(str(err)) from err
    finally:
        try:
            await client.quit()
        except (aiosmtplib.SMTPException, OSError):
            pass


def _build_message(config: dict[str, Any], ticket: dict[str, Any]) -> EmailMessage:
    """Render a ticket into an email message."""
    message = EmailMessage()
    message["From"] = config[CONF_SENDER]
    message["To"] = config[CONF_RECIPIENT]
    message["Subject"] = f"[HA Ticket][{ticket['priority']}] {ticket['subject']}"

    body = (
        f"Priority: {ticket['priority']}\n"
        f"Reported by: {ticket['reporter']}\n"
        f"User ID: {ticket['reporter_id']}\n"
        f"Created: {ticket['created']}\n"
        "\n"
        f"{ticket['message']}\n"
    )
    message.set_content(body)
    return message


async def async_send_ticket(config: dict[str, Any], ticket: dict[str, Any]) -> None:
    """Deliver a ticket via SMTP.

    Raises TicketDeliveryError on failure.
    """
    message = _build_message(config, ticket)
    kwargs = _client_kwargs(config)
    try:
        await aiosmtplib.send(message, **kwargs)
    except (aiosmtplib.SMTPException, OSError, ValueError) as err:
        _LOGGER.error("Failed to send ticket email: %s", err)
        raise TicketDeliveryError(str(err)) from err

"""Tests for setup and ticket delivery."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_smith_buddy.const import (
    ATTR_MESSAGE,
    ATTR_SUBJECT,
    DOMAIN,
    PANEL_URL_PATH,
    SERVICE_CREATE_TICKET,
)

from .test_config_flow import USER_INPUT


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=USER_INPUT)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_setup_registers_service_and_panel(hass: HomeAssistant) -> None:
    """Setup registers the service and sidebar panel."""
    await _setup(hass)
    assert hass.services.has_service(DOMAIN, SERVICE_CREATE_TICKET)
    assert PANEL_URL_PATH in hass.data["frontend_panels"]


async def test_create_ticket_service_sends_email(hass: HomeAssistant) -> None:
    """The create_ticket service delivers the ticket via the mailer."""
    await _setup(hass)

    with patch(
        "custom_components.home_smith_buddy.async_send_ticket",
        return_value=None,
    ) as mock_send:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CREATE_TICKET,
            {ATTR_SUBJECT: "Light broken", ATTR_MESSAGE: "Please help"},
            blocking=True,
        )

    assert mock_send.call_count == 1
    config, ticket = mock_send.call_args.args
    assert config["recipient"] == USER_INPUT["recipient"]
    assert ticket["subject"] == "Light broken"
    assert ticket["priority"] == "normal"

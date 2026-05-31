"""Tests for the Home Smith Buddy config flow."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.home_smith_buddy.const import (
    CONF_ENCRYPTION,
    CONF_HOST,
    CONF_PORT,
    CONF_RECIPIENT,
    CONF_SENDER,
    DOMAIN,
    ENCRYPTION_STARTTLS,
)
from custom_components.home_smith_buddy.mailer import TicketDeliveryError

USER_INPUT = {
    CONF_HOST: "smtp.example.com",
    CONF_PORT: 587,
    CONF_SENDER: "ha@example.com",
    CONF_RECIPIENT: "admin@example.com",
    CONF_ENCRYPTION: ENCRYPTION_STARTTLS,
}


async def test_user_flow_success(hass: HomeAssistant) -> None:
    """A valid SMTP config creates an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    with patch(
        "custom_components.home_smith_buddy.config_flow.async_test_connection",
        return_value=None,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == USER_INPUT


async def test_user_flow_cannot_connect(hass: HomeAssistant) -> None:
    """A failed connection surfaces an error and keeps the form open."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    with patch(
        "custom_components.home_smith_buddy.config_flow.async_test_connection",
        side_effect=TicketDeliveryError("nope"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

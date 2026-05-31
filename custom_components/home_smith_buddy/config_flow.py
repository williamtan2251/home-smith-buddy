"""Config flow for Home Smith Buddy."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import (
    CONF_ENCRYPTION,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_RECIPIENT,
    CONF_SENDER,
    CONF_USERNAME,
    DEFAULT_ENCRYPTION,
    DEFAULT_PORT,
    DOMAIN,
    ENCRYPTION_MODES,
)
from .mailer import TicketDeliveryError, async_test_connection


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build the SMTP settings schema, pre-filled with ``defaults``."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST)): str,
            vol.Required(
                CONF_PORT, default=defaults.get(CONF_PORT, DEFAULT_PORT)
            ): vol.All(int, vol.Range(min=1, max=65535)),
            vol.Optional(
                CONF_USERNAME, default=defaults.get(CONF_USERNAME, "")
            ): str,
            vol.Optional(
                CONF_PASSWORD, default=defaults.get(CONF_PASSWORD, "")
            ): str,
            vol.Required(CONF_SENDER, default=defaults.get(CONF_SENDER)): str,
            vol.Required(
                CONF_RECIPIENT, default=defaults.get(CONF_RECIPIENT)
            ): str,
            vol.Required(
                CONF_ENCRYPTION,
                default=defaults.get(CONF_ENCRYPTION, DEFAULT_ENCRYPTION),
            ): vol.In(ENCRYPTION_MODES),
        }
    )


class HomeSmithBuddyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the SMTP setup flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Initial setup: collect and validate SMTP settings."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await async_test_connection(user_input)
            except TicketDeliveryError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Home Smith Buddy", data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Allow editing the SMTP settings after setup."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await async_test_connection(user_input)
            except TicketDeliveryError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry, data=user_input
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_schema(user_input or dict(entry.data)),
            errors=errors,
        )

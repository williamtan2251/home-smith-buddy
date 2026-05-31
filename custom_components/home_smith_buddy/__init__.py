"""The Home Smith Buddy integration."""

from __future__ import annotations

import os

import voluptuous as vol

from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_MESSAGE,
    ATTR_PRIORITY,
    ATTR_SUBJECT,
    DEFAULT_PRIORITY,
    DOMAIN,
    PANEL_ICON,
    PANEL_JS_FILE,
    PANEL_JS_URL,
    PANEL_TITLE,
    PANEL_URL_PATH,
    PANEL_WEBCOMPONENT,
    PRIORITIES,
    SERVICE_CREATE_TICKET,
    WS_CREATE_TICKET,
)
from .mailer import TicketDeliveryError, async_send_ticket

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

CREATE_TICKET_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SUBJECT): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_PRIORITY, default=DEFAULT_PRIORITY): vol.In(PRIORITIES),
    }
)


def _active_config(hass: HomeAssistant) -> dict | None:
    """Return the merged config of the single config entry, if set up."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return None
    entry = entries[0]
    return {**entry.data, **entry.options}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Smith Buddy from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get("_global_setup"):
        await _async_register_frontend(hass)
        websocket_api.async_register_command(hass, websocket_create_ticket)
        _async_register_services(hass)
        domain_data["_global_setup"] = True

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Tear down the panel; the entry config is no longer available."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH)
    hass.data.get(DOMAIN, {}).pop("_global_setup", None)
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the panel JS and register the sidebar panel."""
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                PANEL_JS_URL,
                os.path.join(FRONTEND_DIR, PANEL_JS_FILE),
                cache_headers=False,
            )
        ]
    )
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_WEBCOMPONENT,
        frontend_url_path=PANEL_URL_PATH,
        module_url=PANEL_JS_URL,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=False,
        config={},
    )


def _async_register_services(hass: HomeAssistant) -> None:
    """Register the create_ticket service."""

    async def _handle_create_ticket(call: ServiceCall) -> None:
        reporter = "Automation"
        reporter_id = "—"
        if call.context.user_id:
            user = await hass.auth.async_get_user(call.context.user_id)
            if user is not None:
                reporter = user.name or user.id
                reporter_id = user.id
        await _send(
            hass,
            subject=call.data[ATTR_SUBJECT],
            message=call.data[ATTR_MESSAGE],
            priority=call.data[ATTR_PRIORITY],
            reporter=reporter,
            reporter_id=reporter_id,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_TICKET,
        _handle_create_ticket,
        schema=CREATE_TICKET_SCHEMA,
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_CREATE_TICKET,
        vol.Required(ATTR_SUBJECT): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_PRIORITY, default=DEFAULT_PRIORITY): vol.In(PRIORITIES),
    }
)
@websocket_api.async_response
async def websocket_create_ticket(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Handle a ticket submitted from the Lovelace panel."""
    try:
        await _send(
            hass,
            subject=msg[ATTR_SUBJECT],
            message=msg[ATTR_MESSAGE],
            priority=msg[ATTR_PRIORITY],
            reporter=connection.user.name or connection.user.id,
            reporter_id=connection.user.id,
        )
    except HomeAssistantError as err:
        connection.send_error(msg["id"], "send_failed", str(err))
        return
    connection.send_result(msg["id"], {"status": "sent"})


async def _send(
    hass: HomeAssistant,
    *,
    subject: str,
    message: str,
    priority: str,
    reporter: str,
    reporter_id: str,
) -> None:
    """Build the ticket payload and deliver it, mapping errors for callers."""
    config = _active_config(hass)
    if config is None:
        raise HomeAssistantError("Home Smith Buddy is not configured")

    ticket = {
        "subject": subject,
        "message": message,
        "priority": priority,
        "reporter": reporter,
        "reporter_id": reporter_id,
        "created": dt_util.now().isoformat(timespec="seconds"),
    }
    try:
        await async_send_ticket(config, ticket)
    except TicketDeliveryError as err:
        raise HomeAssistantError(f"Could not deliver ticket: {err}") from err

"""Constants for the Home Smith Buddy integration."""

from __future__ import annotations

DOMAIN = "home_smith_buddy"

# Config entry keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SENDER = "sender"
CONF_RECIPIENT = "recipient"
CONF_ENCRYPTION = "encryption"

# Encryption modes
ENCRYPTION_NONE = "none"
ENCRYPTION_STARTTLS = "starttls"
ENCRYPTION_TLS = "tls"
ENCRYPTION_MODES = [ENCRYPTION_NONE, ENCRYPTION_STARTTLS, ENCRYPTION_TLS]

DEFAULT_PORT = 587
DEFAULT_ENCRYPTION = ENCRYPTION_STARTTLS

# Ticket fields
ATTR_SUBJECT = "subject"
ATTR_MESSAGE = "message"
ATTR_PRIORITY = "priority"

PRIORITIES = ["low", "normal", "high"]
DEFAULT_PRIORITY = "normal"

# Frontend panel
PANEL_URL_PATH = "home-smith-buddy"
PANEL_TITLE = "Log a Ticket"
PANEL_ICON = "mdi:ticket-outline"
PANEL_WEBCOMPONENT = "home-smith-buddy-panel"
PANEL_JS_URL = "/home_smith_buddy/panel.js"
PANEL_JS_FILE = "home-smith-buddy-panel.js"

# Websocket / service command
WS_CREATE_TICKET = f"{DOMAIN}/create_ticket"
SERVICE_CREATE_TICKET = "create_ticket"

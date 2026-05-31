# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`home_smith_buddy` is a Home Assistant **custom integration** (distributed via HACS)
that lets any logged-in Home Assistant user file a support ticket to the admin.
Tickets are entered in a sidebar Lovelace panel and delivered to the admin by email
over SMTP. There is no separate backend or database — the integration only collects
a ticket and sends a one-off email.

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_test.txt

pytest                                   # run the whole suite
pytest tests/test_config_flow.py         # one file
pytest tests/test_init.py::test_create_ticket_service_sends_email  # one test
ruff check .                             # lint
ruff format .                            # format
```

Tests run against a real Home Assistant via `pytest-homeassistant-custom-component`;
the `enable_custom_integrations` fixture (auto-applied in `tests/conftest.py`) is what
allows the component to load. There is no build step — the frontend panel is plain
hand-written JS served as a static file.

## Architecture

The whole integration lives in `custom_components/home_smith_buddy/`. The data flow is:

```
Lovelace panel form ─► websocket cmd  ─┐
                                       ├─► _send() ─► mailer.async_send_ticket() ─► SMTP
service create_ticket ─────────────────┘
```

- **`__init__.py`** — the hub. There are no platforms/entities. `async_setup_entry`
  performs **process-global** registration *once* (guarded by the `_global_setup`
  flag in `hass.data[DOMAIN]`): it serves the panel JS, registers the sidebar panel,
  registers the `home_smith_buddy/create_ticket` **websocket command**, and registers
  the `create_ticket` **service**. Both the websocket handler and the service funnel
  into the private `_send()` helper, which reads the active config, builds the ticket
  dict, and calls the mailer.
- **Single config entry** — `manifest.json` sets `single_config_entry: true`, so there
  is exactly one entry. `_active_config()` reads it as `{**entry.data, **entry.options}`;
  there is no per-entry runtime data. This is why global registration is done once and
  the panel is removed in `async_unload_entry`.
- **`mailer.py`** — all SMTP lives here (via `aiosmtplib`). `async_test_connection`
  (used by the config flow) and `async_send_ticket` share `_client_kwargs`. Both raise
  `TicketDeliveryError`; callers in `__init__.py` translate that into
  `HomeAssistantError` / websocket errors.
- **`config_flow.py`** — `async_step_user` and `async_step_reconfigure` share one
  voluptuous `_schema()`. Both validate by actually opening an SMTP session via
  `async_test_connection` before creating/updating the entry (`cannot_connect` on
  failure).
- **`frontend/home-smith-buddy-panel.js`** — a dependency-free `customElements`
  web component. Home Assistant injects the `hass` object; submission calls
  `hass.connection.sendMessagePromise({type: "home_smith_buddy/create_ticket", ...})`.
  It is **not** the service — the panel goes through the websocket command (the service
  exists for automations).

## Conventions specific to this repo

- Config keys, encryption modes, ticket attribute names, panel URLs, and the
  websocket/service command names are all centralized in `const.py` — add new ones
  there rather than inline strings, and keep the websocket command name in sync with
  the `type` string hard-coded in the panel JS.
- Any user-facing config-flow string added to `strings.json` must also be mirrored in
  `translations/en.json`.
- Bumping behavior/shape requires bumping `version` in `manifest.json` (HACS requires it).
- The `frontend/` JS has no bundler/lint — keep it plain ES (no imports, no framework)
  so it can be served verbatim.

## Repo

Lives at `github.com/williamtan2251/home-smith-buddy`; `manifest.json`
(`codeowners`, `documentation`, `issue_tracker`) points there. `version` in
`manifest.json` must be bumped for every release (HACS requires it).
